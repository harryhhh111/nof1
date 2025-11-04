"""
高频决策调度器

实现每5分钟的自动交易决策系统
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json
import traceback

from multi_timeframe_preprocessor import MultiTimeframeProcessor
from prompt_generator import PromptGenerator
from llm_clients.llm_factory import LLMClientFactory
from trading.paper_trader import PaperTrader
from models.trading_decision import TradingDecision
from scheduling.decision_cache import DecisionCache, MultiLevelCache

logger = logging.getLogger(__name__)


class HighFreqScheduler:
    """
    高频决策调度器

    功能：
    - 每5分钟执行一次决策
    - 并行调用多个LLM
    - 融合长期和短期决策
    - 自动执行纸交易
    - 智能缓存降低成本
    """

    def __init__(
        self,
        symbols: List[str],
        llm_factory: LLMClientFactory,
        paper_trader: PaperTrader,
        interval_seconds: int = 300,
        cache_ttl: int = 600
    ):
        """
        初始化高频调度器

        Args:
            symbols: 交易对列表
            llm_factory: LLM工厂
            paper_trader: 纸交易执行器
            interval_seconds: 执行间隔（秒），默认300秒（5分钟）
            cache_ttl: 缓存生存时间（秒），默认600秒（10分钟）
        """
        self.symbols = symbols
        self.llm_factory = llm_factory
        self.paper_trader = paper_trader
        self.interval_seconds = interval_seconds
        self.is_running = False

        # 初始化组件
        self.processor = MultiTimeframeProcessor()
        self.prompt_generator = PromptGenerator()
        self.cache = MultiLevelCache({
            'fast': 300,    # 5分钟快速缓存
            'default': 600, # 10分钟默认缓存
            'slow': 900     # 15分钟慢速缓存
        })

        # 统计数据
        self.stats = {
            'total_runs': 0,
            'successful_decisions': 0,
            'failed_decisions': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_cost': 0.0,
            'start_time': None,
            'last_run_time': None
        }

        # 错误统计
        self.error_counts = {symbol: 0 for symbol in symbols}

    async def start(self):
        """
        启动高频决策调度

        每5分钟执行一次：
        1. 获取多时间框架数据
        2. 检查缓存
        3. 生成提示
        4. 并行调用LLM
        5. 融合决策
        6. 执行纸交易
        """
        self.is_running = True
        self.stats['start_time'] = datetime.now()

        logger.info(f"高频决策调度器已启动，监控 {len(self.symbols)} 个交易对")
        logger.info(f"执行间隔: {self.interval_seconds}秒")

        try:
            while self.is_running:
                start_time = time.time()
                logger.info(f"开始第 {self.stats['total_runs'] + 1} 轮决策")

                # 并行处理所有交易对
                tasks = []
                for symbol in self.symbols:
                    tasks.append(self._process_symbol(symbol))

                # 等待所有任务完成
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # 处理结果
                for symbol, result in zip(self.symbols, results):
                    if isinstance(result, Exception):
                        logger.error(f"处理 {symbol} 失败: {result}")
                        self.error_counts[symbol] += 1
                    else:
                        logger.info(f"处理 {symbol} 成功: {result}")

                # 更新统计
                self.stats['total_runs'] += 1
                self.stats['last_run_time'] = datetime.now()

                # 打印统计信息
                self._print_stats()

                # 计算下次执行时间
                elapsed = time.time() - start_time
                sleep_time = max(0, self.interval_seconds - elapsed)

                if sleep_time > 0:
                    logger.info(f"等待 {sleep_time:.1f} 秒后执行下一轮...")
                    await asyncio.sleep(sleep_time)

        except KeyboardInterrupt:
            logger.info("收到停止信号，正在关闭...")
        except Exception as e:
            logger.error(f"调度器异常: {e}\n{traceback.format_exc()}")
        finally:
            self.is_running = False
            self.cleanup()

    async def _process_symbol(self, symbol: str) -> str:
        """
        处理单个交易对

        Args:
            symbol: 交易对

        Returns:
            处理结果状态
        """
        try:
            # 1. 获取多时间框架数据
            logger.info(f"正在获取 {symbol} 的数据...")
            data_4h, data_3m = await self._get_data(symbol)

            # 2. 检查缓存
            cache_key_data = {
                '4h': data_4h.get('trend', {}).get('direction'),
                '3m': data_3m.get('momentum', {}).get('momentum_direction'),
                'price_4h': data_4h.get('current_price'),
                'price_3m': data_3m.get('current_price')
            }

            if self.cache.is_valid(symbol, cache_key_data):
                cached_decision = self.cache.get(symbol, cache_key_data)[0]
                self.stats['cache_hits'] += 1
                logger.info(f"{symbol} 缓存命中，使用缓存决策: {cached_decision.action}")

                # 执行缓存决策
                await self._execute_decision(symbol, cached_decision)
                return "cache_hit"

            # 3. 生成提示
            logger.info(f"正在为 {symbol} 生成提示...")
            prompt_4h = self.prompt_generator.generate_4h_prompt(data_4h, data_3m)
            prompt_3m = self.prompt_generator.generate_3m_prompt(data_3m)

            # 4. 并行调用LLM
            logger.info(f"正在并行调用LLM分析 {symbol}...")
            decisions = await self._parallel_llm_call(symbol, prompt_4h, prompt_3m)

            # 5. 融合决策
            final_decision = self._fuse_decisions(decisions, data_4h, data_3m)

            # 6. 缓存决策
            self.cache.set(symbol, cache_key_data, final_decision)
            self.stats['cache_misses'] += 1

            # 7. 执行决策
            await self._execute_decision(symbol, final_decision)

            self.stats['successful_decisions'] += 1
            return "success"

        except Exception as e:
            logger.error(f"处理 {symbol} 时发生错误: {e}\n{traceback.format_exc()}")
            self.stats['failed_decisions'] += 1
            raise

    async def _get_data(self, symbol: str) -> Tuple[Dict, Dict]:
        """
        获取多时间框架数据

        Args:
            symbol: 交易对

        Returns:
            (4h数据, 3m数据)
        """
        # 使用线程池执行阻塞操作
        loop = asyncio.get_event_loop()

        # 并行获取4h和3m数据
        tasks = [
            loop.run_in_executor(None, self.processor.process_4h_data, symbol),
            loop.run_in_executor(None, self.processor.process_3m_data, symbol)
        ]

        data_4h, data_3m = await asyncio.gather(*tasks, return_exceptions=True)

        if isinstance(data_4h, Exception):
            raise Exception(f"获取4h数据失败: {data_4h}")
        if isinstance(data_3m, Exception):
            raise Exception(f"获取3m数据失败: {data_3m}")

        return data_4h, data_3m

    async def _parallel_llm_call(
        self,
        symbol: str,
        prompt_4h: str,
        prompt_3m: str
    ) -> List[Tuple[TradingDecision, Any]]:
        """
        并行调用多个LLM

        Args:
            symbol: 交易对
            prompt_4h: 4小时提示
            prompt_3m: 3分钟提示

        Returns:
            [(决策, 元数据), ...]
        """
        # 简化版本：顺序调用两个模型
        # 生产环境中可以改为真正的异步并行
        results = []

        # DeepSeek - 长期分析
        try:
            if 'deepseek' in self.llm_factory.list_available_models():
                logger.info(f"调用 DeepSeek 分析 {symbol}...")
                decision_4h, metadata_4h = self.llm_factory.call_model(
                    'deepseek',
                    prompt_4h,
                    temperature=0.3,
                    max_tokens=1500
                )
                decision_4h.symbol = symbol
                decision_4h.timeframe = "4h"
                results.append((decision_4h, metadata_4h))
                self.stats['total_cost'] += metadata_4h.cost or 0
        except Exception as e:
            logger.error(f"DeepSeek 调用失败: {e}")

        # Qwen - 短期分析
        try:
            if 'qwen' in self.llm_factory.list_available_models():
                logger.info(f"调用 Qwen 分析 {symbol}...")
                decision_3m, metadata_3m = self.llm_factory.call_model(
                    'qwen',
                    prompt_3m,
                    temperature=0.3,
                    max_tokens=1500
                )
                decision_3m.symbol = symbol
                decision_3m.timeframe = "3m"
                results.append((decision_3m, metadata_3m))
                self.stats['total_cost'] += metadata_3m.cost or 0
        except Exception as e:
            logger.error(f"Qwen 调用失败: {e}")

        if not results:
            raise Exception("所有LLM调用都失败")

        return results

    def _fuse_decisions(
        self,
        decisions: List[Tuple[TradingDecision, Any]],
        data_4h: Dict,
        data_3m: Dict
    ) -> TradingDecision:
        """
        融合多个决策

        Args:
            decisions: 决策列表
            data_4h: 4小时数据
            data_3m: 3分钟数据

        Returns:
            融合后的决策
        """
        if not decisions:
            # 默认HOLD决策
            return TradingDecision(
                action="HOLD",
                confidence=50,
                reasoning="无有效决策，默认HOLD",
                position_size=0,
                risk_level="MEDIUM",
                risk_score=50,
                model_source="system",
                timeframe="fused"
            )

        if len(decisions) == 1:
            # 只有一个决策，直接返回
            decision, metadata = decisions[0]
            decision.fusion_summary = "单一模型决策"
            decision.consensus_score = 100.0
            return decision

        # 多个决策融合
        decisions_only = [d[0] for d in decisions]

        # 统计各动作的置信度
        action_scores = {"BUY": 0, "SELL": 0, "HOLD": 0}
        total_confidence = 0

        for decision in decisions_only:
            action_scores[decision.action] += decision.confidence
            total_confidence += decision.confidence

        # 选择置信度最高的动作
        best_action = max(action_scores.items(), key=lambda x: x[1])[0]

        # 计算一致性评分
        max_score = max(action_scores.values())
        consensus_score = (max_score / total_confidence * 100) if total_confidence > 0 else 0

        # 创建融合决策
        fused_decision = decisions_only[0].__class__(
            action=best_action,
            confidence=max_score / len(decisions_only),
            reasoning=f"融合{len(decisions)}个决策: {action_scores}",
            position_size=decisions_only[0].position_size,
            risk_level=decisions_only[0].risk_level,
            risk_score=decisions_only[0].risk_score,
            model_source="fused",
            timeframe="fused",
            symbol=decisions_only[0].symbol,
            fusion_summary=f"{len(decisions)}个模型融合",
            consensus_score=consensus_score,
            execution_timing="立即执行" if consensus_score > 80 else "谨慎执行"
        )

        # 添加长期和短期贡献度
        if len(decisions_only) >= 2:
            fused_decision.long_term_contribution = f"长期决策: {decisions_only[0].action} (置信度: {decisions_only[0].confidence})"
            fused_decision.short_term_contribution = f"短期决策: {decisions_only[1].action} (置信度: {decisions_only[1].confidence})"

        return fused_decision

    async def _execute_decision(self, symbol: str, decision: TradingDecision):
        """
        执行决策

        Args:
            symbol: 交易对
            decision: 交易决策
        """
        try:
            # 获取当前价格（简化版本）
            current_price = self._get_current_price(symbol)

            # 执行决策
            result = self.paper_trader.execute_decision(decision, current_price)

            if result['status'] == 'success':
                logger.info(f"{symbol} 决策执行成功: {decision.action} - {decision.reasoning[:50]}...")
            elif result['status'] == 'hold':
                logger.info(f"{symbol} HOLD决策: {result['message']}")
            else:
                logger.warning(f"{symbol} 决策执行失败: {result.get('message', '未知错误')}")

        except Exception as e:
            logger.error(f"执行 {symbol} 决策时发生错误: {e}")

    def _get_current_price(self, symbol: str) -> float:
        """
        获取当前价格（简化版本）

        Args:
            symbol: 交易对

        Returns:
            当前价格
        """
        # 简化实现：从纸交易持仓中获取
        positions = self.paper_trader.get_positions()
        for pos in positions:
            if pos['symbol'] == symbol:
                return pos['current_price']

        # 默认价格（实际应该从交易所API获取）
        return 50000.0

    def _print_stats(self):
        """打印统计信息"""
        if self.stats['total_runs'] == 0:
            return

        logger.info(f"""
===== 统计信息 (第 {self.stats['total_runs']} 轮) =====
成功决策: {self.stats['successful_decisions']}
失败决策: {self.stats['failed_decisions']}
缓存命中: {self.stats['cache_hits']}
缓存未命中: {self.stats['cache_misses']}
总成本: ${self.stats['total_cost']:.4f}
上次执行: {self.stats['last_run_time']}
==========================================
        """.strip())

    def stop(self):
        """停止调度器"""
        logger.info("正在停止高频决策调度器...")
        self.is_running = False

    def cleanup(self):
        """清理资源"""
        logger.info("正在清理资源...")
        self.processor.close()
        self.paper_trader.close()
        self.llm_factory.close_all()

        # 最终统计
        total_time = 0
        if self.stats['start_time']:
            total_time = (datetime.now() - self.stats['start_time']).total_seconds()

        logger.info(f"""
===== 最终统计 =====
总运行时间: {total_time:.1f} 秒
总执行轮数: {self.stats['total_runs']}
成功决策: {self.stats['successful_decisions']}
失败决策: {self.stats['failed_decisions']}
总成本: ${self.stats['total_cost']:.4f}
平均成本/轮: ${self.stats['total_cost'] / max(1, self.stats['total_runs']):.4f}
==============================
        """.strip())


class DecisionScheduler:
    """
    决策调度器（简化版）

    单次决策执行器
    """

    def __init__(
        self,
        symbol: str,
        llm_factory: LLMClientFactory,
        paper_trader: PaperTrader
    ):
        self.symbol = symbol
        self.llm_factory = llm_factory
        self.paper_trader = paper_trader
        self.processor = MultiTimeframeProcessor()
        self.prompt_generator = PromptGenerator()
        self.cache = DecisionCache(ttl_seconds=600)

    async def make_decision(self) -> TradingDecision:
        """
        执行单次决策

        Returns:
            交易决策
        """
        try:
            # 获取数据
            loop = asyncio.get_event_loop()
            data_4h = await loop.run_in_executor(None, self.processor.process_4h_data, self.symbol)
            data_3m = await loop.run_in_executor(None, self.processor.process_3m_data, self.symbol)

            # 检查缓存
            cache_data = {'price_4h': data_4h.get('current_price'), 'price_3m': data_3m.get('current_price')}
            cached = self.cache.get(self.symbol, cache_data)
            if cached:
                return cached[0]

            # 生成提示
            prompt_4h = self.prompt_generator.generate_4h_prompt(data_4h, data_3m)
            prompt_3m = self.prompt_generator.generate_3m_prompt(data_3m)

            # 调用LLM（简化版本）
            decision_4h, _ = self.llm_factory.call_model('deepseek', prompt_4h)
            decision_3m, _ = self.llm_factory.call_model('qwen', prompt_3m)

            # 融合决策
            fused = self._simple_fusion([decision_4h, decision_3m], data_4h, data_3m)

            # 缓存
            self.cache.set(self.symbol, cache_data, fused)

            return fused

        except Exception as e:
            logger.error(f"决策失败: {e}")
            # 返回默认决策
            return TradingDecision(
                action="HOLD",
                confidence=50,
                reasoning=f"决策失败: {e}",
                position_size=0,
                risk_level="MEDIUM",
                risk_score=50,
                model_source="error",
                timeframe="error"
            )

    def _simple_fusion(
        self,
        decisions: List[TradingDecision],
        data_4h: Dict,
        data_3m: Dict
    ) -> TradingDecision:
        """简化融合"""
        if not decisions:
            raise ValueError("没有决策")

        # 如果只有一个决策
        if len(decisions) == 1:
            return decisions[0]

        # 多个决策，取置信度最高者
        best = max(decisions, key=lambda d: d.confidence)
        best.fusion_summary = f"从{len(decisions)}个决策中选择置信度最高者"
        return best
