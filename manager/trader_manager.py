"""
多账户管理器

管理多个独立的Trader实例，负责：
- 统一市场数据输入
- 并发执行所有Trader的决策
- 实时性能对比
- 最佳表现者追踪
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from collections import defaultdict
import time

from models.trader import Trader
from data_fetcher import DataFetcher
from database import Database

logger = logging.getLogger(__name__)


class TraderManager:
    """
    多账户管理器

    管理多个独立的Trader实例，提供：
    - 统一的市场数据获取
    - 并发决策执行
    - 实时性能对比
    - 最佳表现者追踪
    """

    def __init__(self, database_path: Optional[str] = None):
        """
        初始化TraderManager

        Args:
            database_path: 数据库路径（可选）
        """
        self.traders: Dict[str, Trader] = {}  # trader_id -> Trader
        self.market_data: Dict[str, Any] = {}  # 缓存市场数据
        self.is_running = False
        self.start_time: Optional[datetime] = None

        # 统计信息
        self.stats = {
            'total_decisions': 0,
            'successful_decisions': 0,
            'failed_decisions': 0,
            'last_comparison_time': None,
            'best_performer_history': []  # 最佳表现者历史
        }

        # 数据库
        self.database = None
        if database_path:
            try:
                self.database = Database(database_path)
                logger.info(f"TraderManager 初始化数据库: {database_path}")
            except Exception as e:
                logger.warning(f"数据库初始化失败: {e}")

        logger.info("TraderManager 初始化完成")

    def add_trader(self, trader: Trader) -> bool:
        """
        添加交易员

        Args:
            trader: Trader实例

        Returns:
            bool: 是否成功添加
        """
        if trader.trader_id in self.traders:
            logger.error(f"交易员 {trader.trader_id} 已存在")
            return False

        self.traders[trader.trader_id] = trader
        logger.info(f"✅ 添加交易员: {trader.name} (ID: {trader.trader_id}, LLM: {trader.llm_model})")
        logger.info(f"   当前共 {len(self.traders)} 个交易员")

        return True

    def remove_trader(self, trader_id: str) -> bool:
        """
        移除交易员

        Args:
            trader_id: 交易员ID

        Returns:
            bool: 是否成功移除
        """
        if trader_id not in self.traders:
            logger.error(f"交易员 {trader_id} 不存在")
            return False

        trader = self.traders.pop(trader_id)
        logger.info(f"✅ 移除交易员: {trader.name}")
        logger.info(f"   剩余 {len(self.traders)} 个交易员")

        return True

    def get_trader(self, trader_id: str) -> Optional[Trader]:
        """
        获取交易员

        Args:
            trader_id: 交易员ID

        Returns:
            Optional[Trader]: Trader实例或None
        """
        return self.traders.get(trader_id)

    def list_traders(self) -> List[Trader]:
        """
        获取所有交易员列表

        Returns:
            List[Trader]: 交易员列表
        """
        return list(self.traders.values())

    async def start_all(self, interval_seconds: int = 300):
        """
        启动所有交易员

        Args:
            interval_seconds: 执行间隔（秒）
        """
        if not self.traders:
            logger.error("没有交易员，无法启动")
            return

        self.is_running = True
        self.start_time = datetime.now()
        logger.info(f"🚀 启动所有交易员，共 {len(self.traders)} 个")
        logger.info(f"   执行间隔: {interval_seconds} 秒")

        try:
            while self.is_running:
                start_time = time.time()

                # 执行一轮决策
                await self.run_once()

                # 计算下次执行时间
                elapsed = time.time() - start_time
                sleep_time = max(0, interval_seconds - elapsed)

                if sleep_time > 0:
                    logger.info(f"⏱️  等待 {sleep_time:.1f} 秒后执行下一轮...")
                    await asyncio.sleep(sleep_time)

        except KeyboardInterrupt:
            logger.info("收到停止信号，正在关闭...")
        except Exception as e:
            logger.error(f"TraderManager 运行异常: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.is_running = False
            await self.cleanup()

    async def stop_all(self):
        """停止所有交易员"""
        logger.info("📛 停止所有交易员...")
        self.is_running = False

    async def run_once(self):
        """执行一轮决策（所有交易员）"""
        if not self.traders:
            logger.warning("没有交易员，跳过执行")
            return

        round_num = self.stats['total_decisions'] // len(self.traders) + 1
        logger.info(f"\n{'='*60}")
        logger.info(f"第 {round_num} 轮决策 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"{'='*60}")

        try:
            # 1. 获取市场数据
            logger.info("📊 获取市场数据...")
            await self._fetch_market_data()

            # 2. 所有交易员独立决策
            logger.info(f"🤖 {len(self.traders)} 个交易员开始决策...")
            await self._process_all_traders()

            # 3. 更新统计
            self.stats['last_comparison_time'] = datetime.now()

            # 4. 性能对比
            self._log_performance_comparison()

            logger.info(f"✅ 第 {round_num} 轮决策完成")

        except Exception as e:
            logger.error(f"❌ 第 {round_num} 轮决策失败: {e}")
            import traceback
            traceback.print_exc()

    async def _fetch_market_data(self):
        """获取市场数据"""
        try:
            # 获取所有交易对
            symbols = set()
            for trader in self.traders.values():
                if trader.symbols:
                    symbols.update(trader.symbols)
                else:
                    symbols.update(['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT'])

            # 获取市场数据
            fetcher = DataFetcher()
            self.market_data = fetcher.get_multiple_symbols_data(list(symbols))
            fetcher.close()

            logger.info(f"✅ 获取 {len(symbols)} 个交易对的市场数据")

        except Exception as e:
            logger.error(f"❌ 获取市场数据失败: {e}")
            raise

    async def _process_all_traders(self):
        """处理所有交易员"""
        # 并发执行所有交易员的决策
        tasks = []
        for trader in self.traders.values():
            task = self._process_single_trader(trader)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理结果
        for trader, result in zip(self.traders.values(), results):
            if isinstance(result, Exception):
                logger.error(f"❌ {trader.name} 处理失败: {result}")
                self.stats['failed_decisions'] += 1
            else:
                self.stats['successful_decisions'] += 1

        self.stats['total_decisions'] += len(self.traders)

    async def _process_single_trader(self, trader: Trader) -> Dict[str, Any]:
        """处理单个交易员"""
        try:
            # 获取决策
            decision = trader.get_decision(self.market_data)

            # 模拟执行决策（纸交易）
            # 注意：这里使用模拟价格，实际应该从市场数据获取
            if decision.symbol in self.market_data:
                current_price = self.market_data[decision.symbol].get('current_price', 50000.0)
            else:
                current_price = 50000.0

            # 执行决策
            result = trader.execute_decision(decision, current_price)

            # 保存到数据库（如果可用）
            if self.database:
                await self._save_trader_state(trader)

            return {
                'trader_id': trader.trader_id,
                'status': 'success',
                'result': result
            }

        except Exception as e:
            logger.error(f"❌ {trader.name} 处理失败: {e}")
            return {
                'trader_id': trader.trader_id,
                'status': 'error',
                'error': str(e)
            }

    def _log_performance_comparison(self):
        """记录性能对比"""
        if not self.traders:
            return

        logger.info(f"\n🏆 多账户性能对比 ({len(self.traders)} 个账户)")
        logger.info("=" * 80)
        logger.info(
            f"{'账户名称':<20} | {'LLM模型':<12} | {'资金':<10} | {'PnL':<12} | {'收益率':<8} | {'胜率':<6} | {'交易数':<6}"
        )
        logger.info("-" * 80)

        # 获取性能数据并排序
        traders_perf = []
        for trader in self.traders.values():
            perf = trader.get_performance()
            traders_perf.append((trader, perf))

        # 按PnL排序
        traders_perf.sort(key=lambda x: x[1]['total_pnl'], reverse=True)

        # 记录每个交易员的表现
        best_trader = None
        best_pnl = float('-inf')

        for trader, perf in traders_perf:
            logger.info(
                f"{trader.name:<20} | "
                f"{trader.llm_model:<12} | "
                f"${perf['current_balance']:<9.2f} | "
                f"${perf['total_pnl']:<11.2f} | "
                f"{perf['total_pnl_pct']:>+6.2f}% | "
                f"{perf['win_rate']:>5.1f}% | "
                f"{perf['total_trades']:>6}"
            )

            # 更新最佳表现者
            if perf['total_pnl'] > best_pnl:
                best_pnl = perf['total_pnl']
                best_trader = trader

        logger.info("-" * 80)

        # 记录最佳表现者
        if best_trader:
            logger.info(
                f"🥇 当前最佳: {best_trader.name} (LLM: {best_trader.llm_model}) "
                f"PnL: ${best_trader.total_pnl:.2f}"
            )

            # 更新最佳表现者历史
            self.stats['best_performer_history'].append({
                'timestamp': datetime.now().isoformat(),
                'trader_id': best_trader.trader_id,
                'trader_name': best_trader.name,
                'llm_model': best_trader.llm_model,
                'total_pnl': best_trader.total_pnl
            })

            # 保持历史记录长度不超过100
            if len(self.stats['best_performer_history']) > 100:
                self.stats['best_performer_history'].pop(0)

        logger.info("=" * 80)

    def get_best_performer(self) -> Optional[Trader]:
        """
        获取当前最佳表现者

        Returns:
            Optional[Trader]: 最佳表现者或None
        """
        if not self.traders:
            return None

        return max(
            self.traders.values(),
            key=lambda t: t.total_pnl
        )

    def compare_performance(self) -> Dict[str, Any]:
        """
        对比所有交易员性能

        Returns:
            Dict: 性能对比数据
        """
        traders_data = []
        for trader in self.traders.values():
            traders_data.append({
                'trader_id': trader.trader_id,
                'name': trader.name,
                'llm_model': trader.llm_model,
                'performance': trader.get_performance()
            })

        # 按PnL排序
        traders_data.sort(key=lambda x: x['performance']['total_pnl'], reverse=True)

        return {
            'timestamp': datetime.now().isoformat(),
            'total_traders': len(self.traders),
            'traders': traders_data,
            'best_performer': {
                'trader_id': traders_data[0]['trader_id'] if traders_data else None,
                'name': traders_data[0]['name'] if traders_data else None,
                'llm_model': traders_data[0]['llm_model'] if traders_data else None,
                'total_pnl': traders_data[0]['performance']['total_pnl'] if traders_data else 0
            },
            'summary': self._generate_performance_summary(traders_data)
        }

    def _generate_performance_summary(self, traders_data: List[Dict]) -> Dict[str, Any]:
        """生成性能摘要"""
        if not traders_data:
            return {}

        total_initial = sum(t['performance']['initial_balance'] for t in traders_data)
        total_current = sum(t['performance']['current_balance'] for t in traders_data)
        total_pnl = sum(t['performance']['total_pnl'] for t in traders_data)
        total_trades = sum(t['performance']['total_trades'] for t in traders_data)

        return {
            'total_initial_balance': total_initial,
            'total_current_balance': total_current,
            'total_pnl': total_pnl,
            'total_pnl_pct': (total_pnl / total_initial) * 100 if total_initial > 0 else 0,
            'total_trades': total_trades,
            'avg_win_rate': sum(t['performance']['win_rate'] for t in traders_data) / len(traders_data)
        }

    async def _save_trader_state(self, trader: Trader):
        """保存交易员状态到数据库"""
        try:
            if not self.database:
                return

            # 保存交易员配置
            trader_data = {
                'trader_id': trader.trader_id,
                'name': trader.name,
                'llm_model': trader.llm_model,
                'initial_balance': trader.initial_balance,
                'current_balance': trader.current_balance,
                'total_pnl': trader.total_pnl,
                'total_trades': trader.total_trades,
                'updated_at': datetime.now().isoformat()
            }

            # 这里应该调用数据库的保存方法
            # self.database.save_trader(trader_data)
            logger.debug(f"💾 保存交易员状态: {trader.name}")

        except Exception as e:
            logger.warning(f"❌ 保存交易员状态失败: {e}")

    def get_summary(self) -> str:
        """
        获取管理器摘要

        Returns:
            str: 格式化的摘要信息
        """
        if not self.start_time:
            runtime = 0
        else:
            runtime = (datetime.now() - self.start_time).total_seconds() / 60

        best = self.get_best_performer()

        return f"""
{'='*60}
TraderManager 摘要
{'='*60}
交易员数量: {len(self.traders)}
运行时间: {runtime:.0f} 分钟
总决策数: {self.stats['total_decisions']}
成功决策: {self.stats['successful_decisions']}
失败决策: {self.stats['failed_decisions']}
成功率: {(self.stats['successful_decisions'] / max(1, self.stats['total_decisions']) * 100):.1f}%

当前最佳表现者:
  名称: {best.name if best else 'N/A'}
  LLM: {best.llm_model if best else 'N/A'}
  PnL: ${best.total_pnl if best else 0:.2f}
{'='*60}
""".strip()

    async def cleanup(self):
        """清理资源"""
        logger.info("🧹 清理TraderManager资源...")

        # 关闭数据库连接
        if self.database:
            self.database.close()
            self.database = None

        # 显示最终统计
        if self.start_time:
            runtime = (datetime.now() - self.start_time).total_seconds() / 60
            logger.info(f"\n📊 最终统计:")
            logger.info(f"   运行时间: {runtime:.0f} 分钟")
            logger.info(f"   总决策数: {self.stats['total_decisions']}")
            logger.info(f"   成功决策: {self.stats['successful_decisions']}")
            logger.info(f"   失败决策: {self.stats['failed_decisions']}")

        # 显示所有交易员的最终表现
        if self.traders:
            logger.info(f"\n🏁 所有交易员最终表现:")
            for trader in self.traders.values():
                logger.info(f"   {trader.name}: PnL ${trader.total_pnl:.2f} ({trader.total_pnl_pct:+.2f}%)")

        logger.info("✅ TraderManager 清理完成")

    def __repr__(self) -> str:
        return f"TraderManager(traders={len(self.traders)}, running={self.is_running})"
