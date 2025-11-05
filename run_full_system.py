#!/usr/bin/env python3
"""
完整系统运行脚本

启动所有组件：
1. 数据收集（每3分钟）
2. LLM决策系统（每5分钟）
3. 监控和日志
4. API服务器（用于HTML面板）
"""

import sys
import os
import asyncio
import time
import logging
from datetime import datetime, timedelta
from typing import List
import threading

# 添加项目根目录
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_fetcher import DataFetcher
from database import Database
from trading.real_trader import RealTrader  # ✅ 使用Binance Demo Trading
from monitoring.performance_monitor import PerformanceMonitor
from models.trading_decision import TradingDecision
from scheduling.high_freq_scheduler import HighFreqScheduler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('full_system.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class FullSystem:
    """完整系统控制器"""

    def __init__(self):
        """初始化系统"""
        self.symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
        self.data_fetcher = None
        self.real_trader = None  # ✅ 使用Binance Demo Trading
        self.monitor = None
        self.db = None
        self.running = False

        logger.info("=" * 80)
        logger.info("🚀 Nof1 完整交易系统启动（使用Binance Demo Trading）")
        logger.info("=" * 80)

    async def initialize(self):
        """初始化所有组件"""
        try:
            # 1. 初始化数据库
            logger.info("📦 初始化数据库...")
            self.db = Database()
            logger.info("✅ 数据库初始化完成")

            # 2. 初始化数据获取器
            logger.info("📡 初始化数据获取器...")
            self.data_fetcher = DataFetcher()
            logger.info("✅ 数据获取器初始化完成")

            # 3. 初始化真实交易执行器（Binance Demo Trading）
            logger.info("💰 初始化Binance Demo Trading交易执行器...")
            self.real_trader = RealTrader()
            logger.info("✅ Demo Trading交易执行器初始化完成")

            # 4. 初始化性能监控器
            logger.info("📊 初始化性能监控器...")
            self.monitor = PerformanceMonitor()
            logger.info("✅ 性能监控器初始化完成")

            logger.info("🎉 所有组件初始化完成")
            return True

        except Exception as e:
            logger.error(f"❌ 初始化失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def collect_data_loop(self):
        """数据收集循环（每3分钟）"""
        logger.info("🔄 启动数据收集循环（每3分钟）")

        while self.running:
            try:
                for symbol in self.symbols:
                    logger.info(f"📈 获取 {symbol} 数据...")
                    data = self.data_fetcher.get_market_data(symbol)
                    logger.info(f"✅ {symbol} 数据获取完成: ${data['current_price']:,.2f}")

                # 等待3分钟
                await asyncio.sleep(180)

            except Exception as e:
                logger.error(f"❌ 数据收集错误: {e}")
                await asyncio.sleep(10)  # 错误后等待10秒再重试

    def generate_mock_decisions(self):
        """生成模拟决策（用于演示）"""
        import random

        logger.info("🤖 生成模拟LLM决策...")

        for symbol in self.symbols:
            # 随机生成决策
            actions = ['BUY', 'SELL', 'HOLD']
            action = random.choice(actions)
            confidence = random.uniform(60, 95)
            price = 50000 + random.uniform(-2000, 2000)

            # 创建决策
            decision = TradingDecision(
                action=action,
                confidence=confidence,
                symbol=symbol,
                entry_price=price,
                stop_loss=price * 0.95 if action == 'BUY' else price * 1.05,
                take_profit=price * 1.05 if action == 'BUY' else price * 0.95,
                position_size=random.uniform(5, 15),
                risk_level="MEDIUM",
                reasoning=f"基于技术指标分析的{action}决策",
                timeframe="4h"
            )

            # 执行决策
            result = self.real_trader.execute_decision(decision, price)

            # 记录到监控器
            self.monitor.record_trading_metrics(
                decision=decision,
                pnl=result.get('pnl', 0),
                execution_time=1.5,
                llm_cost=0.02,
                total_cost=0.03
            )

            logger.info(f"✅ {symbol}: {action} {decision.position_size:.1f}% "
                       f"(置信度: {confidence:.1f}%)")

    async def decision_loop(self):
        """决策循环（每5分钟）"""
        logger.info("🔄 启动决策循环（每5分钟）")

        # 等待30秒让数据收集先完成
        await asyncio.sleep(30)

        while self.running:
            try:
                # 1. 生成模拟决策（实际应该是LLM决策）
                self.generate_mock_decisions()

                # 2. 记录系统指标
                self.monitor.record_system_metrics(
                    cpu_usage=50.0,
                    memory_usage=60.0,
                    active_connections=1,
                    response_time=0.3,
                    cache_hit_rate=0.85,
                    error_rate=1.0
                )

                # 3. 获取性能摘要
                summary = self.monitor.get_performance_summary(self.paper_trader)

                logger.info(f"📊 性能摘要:")
                logger.info(f"   总交易: {summary.total_trades}")
                logger.info(f"   胜率: {summary.win_rate:.1f}%")
                logger.info(f"   总PnL: ${summary.total_pnl:.2f}")
                logger.info(f"   总成本: ${summary.total_cost:.4f}")

                # 等待5分钟
                await asyncio.sleep(300)

            except Exception as e:
                logger.error(f"❌ 决策循环错误: {e}")
                await asyncio.sleep(10)

    async def run(self, duration_hours=1):
        """
        运行完整系统

        Args:
            duration_hours: 运行小时数
        """
        # 1. 初始化
        if not await self.initialize():
            logger.error("❌ 初始化失败，退出")
            return False

        # 2. 设置运行标志
        self.running = True
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=duration_hours)

        logger.info(f"⏰ 系统将运行 {duration_hours} 小时")
        logger.info(f"   开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"   结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # 3. 创建任务
        tasks = [
            asyncio.create_task(self.collect_data_loop()),
            asyncio.create_task(self.decision_loop())
        ]

        # 4. 运行直到结束时间
        try:
            while datetime.now() < end_time:
                remaining = end_time - datetime.now()
                hours, remainder = divmod(remaining.total_seconds(), 3600)
                minutes, seconds = divmod(remainder, 60)

                # 每5分钟输出一次状态
                if int(minutes) % 5 == 0 and int(seconds) < 5:
                    logger.info(f"⏱️  剩余运行时间: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")

                await asyncio.sleep(1)

        except KeyboardInterrupt:
            logger.info("⏹️  收到停止信号...")

        finally:
            # 5. 停止所有任务
            self.running = False
            for task in tasks:
                task.cancel()

            # 6. 等待任务结束
            await asyncio.gather(*tasks, return_exceptions=True)

            # 7. 生成最终报告
            await self.generate_final_report()

        return True

    async def generate_final_report(self):
        """生成最终报告"""
        logger.info("=" * 80)
        logger.info("📊 系统运行最终报告")
        logger.info("=" * 80)

        try:
            # 获取性能摘要
            summary = self.monitor.get_performance_summary(self.real_trader)

            logger.info(f"📈 交易统计:")
            logger.info(f"   总决策数: {summary.total_decisions}")
            logger.info(f"   总交易数: {summary.total_trades}")
            logger.info(f"   盈利交易: {summary.winning_trades}")
            logger.info(f"   亏损交易: {summary.losing_trades}")
            logger.info(f"   胜率: {summary.win_rate:.2f}%")

            logger.info(f"💰 财务统计:")
            logger.info(f"   总PnL: ${summary.total_pnl:.2f}")
            logger.info(f"   平均单笔PnL: ${summary.avg_pnl_per_trade:.2f}")
            logger.info(f"   总成本: ${summary.total_cost:.4f}")
            logger.info(f"   ROI: {summary.roi:.2f}%")

            # 查看HTML面板的提示
            logger.info("=" * 80)
            logger.info("🌐 查看结果:")
            logger.info("   HTML面板: trading_dashboard.html")
            logger.info("   API服务器: python3 run_api.py")
            logger.info("   Demo Trading: https://demo.binance.com/")
            logger.info("=" * 80)

        except Exception as e:
            logger.error(f"❌ 生成报告失败: {e}")


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Nof1 完整系统运行')
    parser.add_argument('--hours', type=float, default=1,
                       help='运行小时数 (默认: 1)')
    parser.add_argument('--symbols', nargs='+', default=['BTCUSDT', 'ETHUSDT', 'SOLUSDT'],
                       help='交易对列表')

    args = parser.parse_args()

    system = FullSystem()
    system.symbols = args.symbols

    success = await system.run(duration_hours=args.hours)

    if success:
        logger.info("✅ 系统运行完成")
    else:
        logger.error("❌ 系统运行失败")
        sys.exit(1)


if __name__ == '__main__':
    import argparse
    asyncio.run(main())
