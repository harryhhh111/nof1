#!/usr/bin/env python3
"""
Nof1 数据收集系统 - 纯数据收集版

仅负责数据获取、存储和技术指标计算，不涉及任何交易功能。
适合需要长期数据收集而不想使用交易功能的场景。

使用方法:
    python3 data_collector_only.py              # 使用默认配置运行
    python3 data_collector_only.py --hours 2   # 运行2小时后退出
    python3 data_collector_only.py --interval 60  # 设置为60秒更新一次
"""

import sys
import os
import time
import argparse
import signal
import logging
from datetime import datetime
from typing import List, Optional

# 添加项目根目录
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database

from data_fetcher import DataFetcher
from config import SYMBOLS, UPDATE_INTERVAL, LOG_LEVEL, LOG_FORMAT

# 配置日志
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('data_collection.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class DataCollectorOnly:
    """纯数据收集器（无交易功能）"""

    def __init__(self,
                 symbols: Optional[List[str]] = None,
                 update_interval: Optional[int] = None):
        """
        初始化数据收集器

        Args:
            symbols: 交易对列表
            update_interval: 更新间隔（秒）
        """
        self.symbols = symbols if symbols else SYMBOLS
        self.update_interval = update_interval if update_interval else UPDATE_INTERVAL
        self.data_fetcher = None
        self.db = None
        self.running = False
        self.logger = logging.getLogger(__name__)

        # 注册信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """处理中断信号"""
        self.logger.info(f"\n收到信号 {signum}，正在关闭数据收集器...")
        self.stop()
        sys.exit(0)

    def initialize(self):
        """初始化数据收集器"""
        try:
            self.logger.info("=" * 80)
            self.logger.info("🚀 Nof1 纯数据收集系统启动")
            self.logger.info("=" * 80)
            self.logger.info(f"监控交易对: {', '.join(self.symbols)}")
            self.logger.info(f"更新间隔: {self.update_interval} 秒")
            self.logger.info(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # 初始化数据获取器
            self.logger.info("\n📡 初始化数据获取器...")
            self.data_fetcher = DataFetcher()
            self.logger.info("✅ 数据获取器初始化完成")

            # 初始化数据库
            self.logger.info("\n📦 初始化数据库...")
            self.db = Database()
            self.logger.info("✅ 数据库初始化完成")

            self.logger.info("\n" + "=" * 80)
            self.logger.info("✅ 数据收集系统准备就绪（仅数据收集，无交易功能）")
            self.logger.info("=" * 80)

            return True

        except Exception as e:
            self.logger.error(f"初始化失败: {e}", exc_info=True)
            return False

    def collect_once(self):
        """执行一次数据收集"""
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"开始数据收集 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"{'='*80}")

        success_count = 0
        failed_count = 0

        for symbol in self.symbols:
            try:
                self.logger.info(f"\n📊 正在获取 {symbol} 数据...")

                # 获取市场数据
                data = self.data_fetcher.get_market_data(symbol)

                if data:
                    self.logger.info(f"  ✅ {symbol} 数据获取成功 - 当前价格: ${data['current_price']:,.2f}")
                    success_count += 1
                else:
                    self.logger.warning(f"  ⚠️  {symbol} 数据获取失败")
                    failed_count += 1

            except Exception as e:
                self.logger.error(f"  ❌ {symbol} 数据获取出错: {e}")
                failed_count += 1

        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"数据收集完成 - 成功: {success_count}, 失败: {failed_count}")
        self.logger.info(f"{'='*80}")

        return success_count > 0

    def run_continuous(self, duration_hours: Optional[float] = None):
        """
        持续运行数据收集

        Args:
            duration_hours: 运行时间（小时），None表示持续运行
        """
        self.running = True
        start_time = time.time()

        self.logger.info(f"\n🔄 开始持续数据收集...")

        if duration_hours:
            self.logger.info(f"⏰ 将在 {duration_hours} 小时后自动停止")
            end_time = start_time + duration_hours * 3600
        else:
            self.logger.info("⏰ 持续运行（按 Ctrl+C 停止）")
            end_time = None

        cycle_count = 0

        try:
            while self.running:
                cycle_count += 1

                # 执行数据收集
                self.collect_once()

                # 检查是否超时
                if end_time and time.time() >= end_time:
                    self.logger.info(f"\n⏰ 达到指定运行时间，自动停止")
                    break

                # 等待下次更新
                remaining = self.update_interval
                self.logger.info(f"\n⏳ 等待 {remaining} 秒后进行下次收集...")
                time.sleep(remaining)

        except KeyboardInterrupt:
            self.logger.info("\n⚠️  收到中断信号，正在停止...")
        except Exception as e:
            self.logger.error(f"\n❌ 运行出错: {e}", exc_info=True)
        finally:
            self.stop()
            elapsed = time.time() - start_time
            self.logger.info(f"\n{'='*80}")
            self.logger.info(f"数据收集完成")
            self.logger.info(f"总运行时间: {elapsed/60:.1f} 分钟")
            self.logger.info(f"总循环次数: {cycle_count}")
            self.logger.info(f"{'='*80}")

    def stop(self):
        """停止数据收集器"""
        if not self.running:
            return

        self.running = False

        if self.data_fetcher:
            try:
                self.data_fetcher.close()
                self.logger.info("🔌 数据获取器已关闭")
            except:
                pass

        if self.db:
            try:
                self.db.close()
                self.logger.info("💾 数据库连接已关闭")
            except:
                pass


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Nof1 纯数据收集系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python data_collector_only.py              # 使用默认配置持续运行
  python data_collector_only.py --hours 2   # 运行2小时后自动退出
  python data_collector_only.py --interval 60  # 设置为60秒更新一次
  python data_collector_only.py --symbols BTCUSDT ETHUSDT  # 只监控这两个交易对

注意事项:
  - 仅进行数据收集和存储，不涉及任何交易功能
  - 数据存储在 market_data.db 数据库中
  - 可使用 quick_query.py 查看收集的数据
  - 按 Ctrl+C 可安全停止
        """
    )

    parser.add_argument(
        '--hours',
        type=float,
        help='运行时间（小时），不指定则持续运行'
    )

    parser.add_argument(
        '--interval',
        type=int,
        help=f'更新间隔（秒），默认: {UPDATE_INTERVAL}'
    )

    parser.add_argument(
        '--symbols',
        nargs='+',
        help='监控的交易对列表，不指定则使用默认配置'
    )

    args = parser.parse_args()

    # 创建数据收集器
    collector = DataCollectorOnly(
        symbols=args.symbols,
        update_interval=args.interval
    )

    # 初始化
    if not collector.initialize():
        logger.error("初始化失败，退出程序")
        sys.exit(1)

    # 运行
    try:
        collector.run_continuous(duration_hours=args.hours)
    except Exception as e:
        logger.error(f"运行失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
