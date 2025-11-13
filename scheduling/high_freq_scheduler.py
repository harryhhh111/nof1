"""
高频决策调度器

实现每5分钟的自动交易决策系统

重要原则：
- 一个账户只使用一个LLM进行决策
- 多个LLM用于多账户对比测试（相同prompt，不同LLM，对比效果）
- 不在单个决策过程中融合多个LLM的输出
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
from config import ACCOUNT_CONFIGS, LLM_MODEL_PRIORITY

logger = logging.getLogger(__name__)


class HighFreqScheduler:
    """
    高频决策调度器

    功能：
    - 每5分钟执行一次决策
    - 每个交易对使用单一LLM进行决策
    - 支持多账户对比测试（不同LLM，相同prompt）
    - 自动执行纸交易
    - 智能缓存降低成本

    重要原则：
    - 一个账户只使用一个LLM
    - 多个LLM用于多账户对比，而非单个决策融合
    """

    def __init__(
        self,
        symbols: List[str],
        llm_factory: LLMClientFactory,
        paper_trader: PaperTrader,
        interval_seconds: int = 300,
        cache_ttl: int = 600,
        account_configs: Optional[Dict] = None
    ):
        """
        初始化高频调度器

        Args:
            symbols: 交易对列表
            llm_factory: LLM工厂
            paper_trader: 纸交易执行器
            interval_seconds: 执行间隔（秒），默认300秒（5分钟）
            cache_ttl: 缓存生存时间（秒），默认600秒（10分钟）
            account_configs: 账户配置，指定每个交易对使用的LLM
        """
        self.symbols = symbols
        self.llm_factory = llm_factory
        self.paper_trader = paper_trader
        self.interval_seconds = interval_seconds
        self.is_running = False
        self.account_configs = account_configs or ACCOUNT_CONFIGS

        # 初始化组件
        self.processor = MultiTimeframeProcessor()
        self.prompt_generator = PromptGenerator()
        self.cache = MultiLevelCache({
            'fast': 300,    # 5分钟快速缓存
            'default': 600, # 10分钟默认缓存
            'slow': 900     # 15分钟慢速缓存
        })

        # 构建交易对到LLM的映射
        self.symbol_to_llm = self._build_symbol_llm_mapping()

        # 验证映射
        self._validate_symbol_llm_mapping()

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

        重要原则：每个交易对只使用一个LLM进行决策
        不再融合多个LLM的输出

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
                'price_3m': data_3m.get('current_price'),
                'llm': self.symbol_to_llm.get(symbol, 'default')  # 包含LLM信息到缓存键
            }

            if self.cache.is_valid(symbol, cache_key_data):
                cached_decision = self.cache.get(symbol, cache_key_data)[0]
                self.stats['cache_hits'] += 1
                logger.info(f"{symbol} 缓存命中，使用缓存决策: {cached_decision.action}")

                # 执行缓存决策
                await self._execute_decision(symbol, cached_decision)
                return "cache_hit"

            # 3. 生成综合提示（长期+短期）
            logger.info(f"正在为 {symbol} 生成综合分析提示...")
            prompt = self._get_prompt_for_symbol(symbol, data_4h, data_3m)

            # 4. 调用单一LLM进行决策
            llm_model = self.symbol_to_llm[symbol]
            logger.info(f"正在使用 {llm_model} 分析 {symbol}...")
            decision = await self._single_llm_call(symbol, llm_model, prompt)

            # 5. 缓存决策
            self.cache.set(symbol, cache_key_data, decision)
            self.stats['cache_misses'] += 1

            # 6. 执行决策
            await self._execute_decision(symbol, decision)

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

    async def _single_llm_call(
        self,
        symbol: str,
        llm_model: str,
        prompt: str
    ) -> TradingDecision:
        """
        调用单一LLM进行决策

        重要原则：每个交易对只使用一个LLM
        多个LLM用于多账户对比测试，而非单个决策融合

        Args:
            symbol: 交易对
            llm_model: LLM模型名称
            prompt: 综合分析提示

        Returns:
            交易决策
        """
        # 检查LLM模型是否可用
        available_models = self.llm_factory.list_available_models()

        if llm_model not in available_models:
            logger.warning(f"LLM模型 '{llm_model}' 不可用，尝试使用备选模型...")
            # 使用优先级列表中的第一个可用模型
            for fallback_model in LLM_MODEL_PRIORITY:
                if fallback_model in available_models:
                    llm_model = fallback_model
                    logger.info(f"使用备选LLM模型: {llm_model}")
                    break
            else:
                raise Exception(f"没有可用的LLM模型")

        try:
            # 调用指定的LLM
            logger.info(f"使用 {llm_model} 分析 {symbol}...")
            decision, metadata = self.llm_factory.call_model(
                llm_model,
                prompt,
                temperature=0.3,
                max_tokens=1500
            )

            # 设置决策属性
            decision.symbol = symbol
            decision.timeframe = "combined"
            decision.model_source = llm_model

            # 更新成本统计
            self.stats['total_cost'] += metadata.cost or 0

            logger.info(
                f"{symbol} 决策完成: {decision.action} "
                f"(置信度: {decision.confidence}%, LLM: {llm_model})"
            )

            return decision

        except Exception as e:
            logger.error(f"LLM调用失败 ({llm_model}): {e}")
            # 返回默认HOLD决策
            return TradingDecision(
                action="HOLD",
                confidence=50,
                reasoning=f"LLM调用失败: {e}",
                position_size=0,
                risk_level="MEDIUM",
                risk_score=50,
                model_source=f"error_{llm_model}",
                timeframe="error",
                symbol=symbol
            )

    def _fuse_decisions(
        self,
        decisions: List[Tuple[TradingDecision, Any]],
        data_4h: Dict,
        data_3m: Dict
    ) -> TradingDecision:
        """
        融合多个决策（仅在多账户对比测试时使用）

        重要说明：
        - 当前设计中，每个交易对只使用一个LLM
        - 此方法主要用于多账户对比测试场景（相同prompt，不同LLM）
        - 常规交易决策不再需要此方法

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
            decision.fusion_summary = "单一LLM决策（非融合）"
            decision.consensus_score = 100.0
            logger.info("⚠️  注意：只有一个决策，未进行融合")
            return decision

        # 多个决策融合（多账户对比场景）
        logger.warning(f"⚠️  检测到多个LLM决策进行融合 (共{len(decisions)}个)")
        logger.warning("   建议：每个交易对应一个账户，一个账户使用一个LLM")

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
            reasoning=f"⚠️ 多账户对比融合: {action_scores}",
            position_size=decisions_only[0].position_size,
            risk_level=decisions_only[0].risk_level,
            risk_score=decisions_only[0].risk_score,
            model_source="multi_account_fusion",
            timeframe="fused",
            symbol=decisions_only[0].symbol,
            fusion_summary=f"⚠️ {len(decisions)}个账户对比融合",
            consensus_score=consensus_score,
            execution_timing="立即执行" if consensus_score > 80 else "谨慎执行"
        )

        # 添加各账户贡献度
        for i, decision in enumerate(decisions_only):
            setattr(fused_decision, f'account_{i+1}_contribution',
                   f"账户{i+1}: {decision.action} (置信度: {decision.confidence}, 模型: {decision.model_source})")

        logger.warning(f"多账户融合完成: {best_action} (一致性: {consensus_score:.1f}%)")

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

    def _build_symbol_llm_mapping(self) -> Dict[str, str]:
        """
        构建交易对到LLM的映射

        Returns:
            {symbol: llm_model} 字典
        """
        mapping = {}

        # 根据账户配置构建映射
        for account_id, config in self.account_configs.items():
            llm_model = config['llm_model']
            symbols = config['symbols']

            for symbol in symbols:
                if symbol in self.symbols:
                    mapping[symbol] = llm_model

        # 对于未在配置中的交易对，使用默认LLM
        for symbol in self.symbols:
            if symbol not in mapping:
                # 使用第一个可用的LLM
                available_models = self.llm_factory.list_available_models()
                if available_models:
                    mapping[symbol] = available_models[0]
                    logger.warning(f"交易对 {symbol} 未在账户配置中，使用默认LLM: {available_models[0]}")
                else:
                    raise ValueError("没有可用的LLM模型")

        return mapping

    def _validate_symbol_llm_mapping(self):
        """验证交易对-LLM映射的合理性"""
        logger.info("验证交易对-LLM映射...")

        # 检查是否有重复的LLM分配给多个交易对
        llm_to_symbols = {}
        for symbol, llm in self.symbol_to_llm.items():
            if llm not in llm_to_symbols:
                llm_to_symbols[llm] = []
            llm_to_symbols[llm].append(symbol)

        # 打印映射信息
        for llm, symbols in llm_to_symbols.items():
            logger.info(f"LLM '{llm}' 负责交易对: {', '.join(symbols)}")

        # 检查映射合理性
        if len(self.symbol_to_llm) != len(self.symbols):
            raise ValueError("存在未分配LLM的交易对")

        logger.info(f"✅ 成功构建 {len(self.symbol_to_llm)} 个交易对的LLM映射")

    def _get_prompt_for_symbol(self, symbol: str, data_4h: Dict, data_3m: Dict) -> str:
        """
        为指定交易对生成提示

        重要：一个交易对只生成一个提示，由其配置的LLM处理
        不再分别生成长期和短期提示

        Args:
            symbol: 交易对
            data_4h: 4小时数据
            data_3m: 3分钟数据

        Returns:
            综合提示字符串
        """
        prompt = f"""
你是一个专业的加密货币量化交易员，基于多时间框架数据进行综合决策。

当前分析交易对：{symbol}

=== 4小时长期趋势分析 ===
{data_4h.get('description', '无数据')}

=== 3分钟短期背景 ===
{data_3m.get('description', '无数据')}

=== 交易任务 ===
请综合长期趋势和短期时机，给出最终交易决策。

请以JSON格式返回决策：
{{
  "action": "BUY|SELL|HOLD",
  "confidence": 0-100,
  "reasoning": "详细分析",
  "entry_price": 价格,
  "stop_loss": 价格,
  "take_profit": 价格,
  "position_size": 百分比,
  "risk_level": "LOW|MEDIUM|HIGH",
  "timeframe": "combined",
  "trend_analysis": "长期趋势分析",
  "timing_analysis": "短期时机分析",
  "key_factors": ["关键因素1", "关键因素2"]
}}
"""
        return prompt

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
    重要：每个交易对只使用一个LLM进行决策

    注意：此为简化版本，适用于单交易对场景
    多交易对场景请使用 HighFreqScheduler
    """

    def __init__(
        self,
        symbol: str,
        llm_factory: LLMClientFactory,
        paper_trader: PaperTrader,
        llm_model: Optional[str] = None,
        account_configs: Optional[Dict] = None
    ):
        self.symbol = symbol
        self.llm_factory = llm_factory
        self.paper_trader = paper_trader
        self.account_configs = account_configs or ACCOUNT_CONFIGS
        self.processor = MultiTimeframeProcessor()
        self.cache = DecisionCache(ttl_seconds=600)

        # 选择LLM模型
        self.llm_model = self._select_llm_model(llm_model)

    def _select_llm_model(self, preferred_model: Optional[str] = None) -> str:
        """
        为当前交易对选择LLM模型

        优先级：
        1. 用户指定的模型（llm_model参数）
        2. 账户配置中指定的模型
        3. 第一个可用模型

        Args:
            preferred_model: 用户首选的LLM模型

        Returns:
            选定的LLM模型名称
        """
        available_models = self.llm_factory.list_available_models()

        # 1. 使用用户指定的模型
        if preferred_model and preferred_model in available_models:
            logger.info(f"使用用户指定的LLM模型: {preferred_model}")
            return preferred_model

        # 2. 从账户配置中查找
        for account_id, config in self.account_configs.items():
            if self.symbol in config['symbols']:
                llm_model = config['llm_model']
                if llm_model in available_models:
                    logger.info(f"从账户配置选择LLM模型: {llm_model}")
                    return llm_model

        # 3. 使用第一个可用模型
        if available_models:
            logger.warning(f"使用默认LLM模型: {available_models[0]}")
            return available_models[0]

        raise ValueError("没有可用的LLM模型")

    def _get_comprehensive_prompt(self, data_4h: Dict, data_3m: Dict) -> str:
        """
        生成综合提示（长期+短期）

        Args:
            data_4h: 4小时数据
            data_3m: 3分钟数据

        Returns:
            综合提示字符串
        """
        prompt = f"""
你是一个专业的加密货币量化交易员，基于多时间框架数据进行综合决策。

当前分析交易对：{self.symbol}
使用LLM模型：{self.llm_model}

=== 4小时长期趋势分析 ===
{data_4h.get('description', '无数据')}

=== 3分钟短期背景 ===
{data_3m.get('description', '无数据')}

=== 交易任务 ===
请综合长期趋势和短期时机，给出最终交易决策。

请以JSON格式返回决策：
{{
  "action": "BUY|SELL|HOLD",
  "confidence": 0-100,
  "reasoning": "详细分析",
  "entry_price": 价格,
  "stop_loss": 价格,
  "take_profit": 价格,
  "position_size": 百分比,
  "risk_level": "LOW|MEDIUM|HIGH",
  "timeframe": "combined",
  "trend_analysis": "长期趋势分析",
  "timing_analysis": "短期时机分析",
  "key_factors": ["关键因素1", "关键因素2"]
}}
"""
        return prompt

    async def make_decision(self) -> TradingDecision:
        """
        执行单次决策

        重要：只使用一个LLM进行决策
        不再融合多个LLM的输出

        Returns:
            交易决策
        """
        try:
            # 获取数据
            loop = asyncio.get_event_loop()
            data_4h = await loop.run_in_executor(None, self.processor.process_4h_data, self.symbol)
            data_3m = await loop.run_in_executor(None, self.processor.process_3m_data, self.symbol)

            # 检查缓存
            cache_data = {
                'price_4h': data_4h.get('current_price'),
                'price_3m': data_3m.get('current_price'),
                'llm': self.llm_model  # 包含LLM到缓存键
            }
            cached = self.cache.get(self.symbol, cache_data)
            if cached:
                return cached[0]

            # 生成综合提示
            prompt = self._get_comprehensive_prompt(data_4h, data_3m)

            # 调用单一LLM
            decision, metadata = self.llm_factory.call_model(
                self.llm_model,
                prompt,
                temperature=0.3,
                max_tokens=1500
            )

            # 设置决策属性
            decision.symbol = self.symbol
            decision.timeframe = "combined"
            decision.model_source = self.llm_model

            # 缓存
            self.cache.set(self.symbol, cache_data, decision)

            logger.info(f"{self.symbol} 决策完成: {decision.action} "
                       f"(置信度: {decision.confidence}%, LLM: {self.llm_model})")

            return decision

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
                model_source=f"error_{self.llm_model}",
                timeframe="error",
                symbol=self.symbol
            )
