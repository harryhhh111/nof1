"""
定时任务调度模块

负责定时获取市场数据并更新数据库。
"""

import schedule
import time
import logging
from typing import List, Callable, Optional
from datetime import datetime
from data_fetcher import DataFetcher
from config import SYMBOLS, UPDATE_INTERVAL

logger = logging.getLogger(__name__)


class DataScheduler:
    """数据更新调度器"""

    def __init__(self, symbols: Optional[List[str]] = None,
                 update_interval: Optional[int] = None):
        """
        初始化调度器

        Args:
            symbols: 交易对符号列表
            update_interval: 更新间隔（秒）
        """
        self.symbols = symbols if symbols else SYMBOLS
        self.update_interval = update_interval if update_interval else UPDATE_INTERVAL
        self.data_fetcher = DataFetcher()
        self.is_running = False

    def update_market_data(self):
        """更新所有交易对的市场数据"""
        logger.info("开始更新市场数据...")
        start_time = datetime.now()

        success_count = 0
        fail_count = 0

        for symbol in self.symbols:
            try:
                logger.info(f"更新 {symbol} 数据中...")
                data = self.data_fetcher.get_market_data(symbol)
                logger.info(f"✓ {symbol} 数据更新成功")
                success_count += 1
            except Exception as e:
                logger.error(f"✗ {symbol} 数据更新失败: {e}")
                fail_count += 1

        elapsed_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"数据更新完成，耗时: {elapsed_time:.2f}秒，成功: {success_count}，失败: {fail_count}")

    def start(self):
        """启动调度器"""
        if self.is_running:
            logger.warning("调度器已在运行中")
            return

        # 设置定时任务
        schedule.every(self.update_interval).seconds.do(self.update_market_data)

        self.is_running = True
        logger.info(f"调度器已启动，更新间隔: {self.update_interval}秒，监控交易对: {', '.join(self.symbols)}")

        # 立即执行一次
        self.update_market_data()

        # 运行调度器
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("接收到中断信号，正在停止调度器...")
            self.stop()

    def stop(self):
        """停止调度器"""
        self.is_running = False
        schedule.clear()
        self.data_fetcher.close()
        logger.info("调度器已停止")

    def get_status(self) -> dict:
        """
        获取调度器状态

        Returns:
            状态信息字典
        """
        return {
            'is_running': self.is_running,
            'symbols': self.symbols,
            'update_interval': self.update_interval,
            'pending_jobs': len(schedule.get_jobs())
        }


class ScheduledTask:
    """定时任务包装类"""

    def __init__(self, func: Callable, *args, **kwargs):
        """
        初始化定时任务

        Args:
            func: 要执行的函数
            *args: 位置参数
            **kwargs: 关键字参数
        """
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.is_running = False

    def run(self):
        """执行任务"""
        try:
            self.is_running = True
            result = self.func(*self.args, **self.kwargs)
            logger.debug(f"任务 {self.func.__name__} 执行完成")
            return result
        except Exception as e:
            logger.error(f"任务 {self.func.__name__} 执行失败: {e}")
            raise
        finally:
            self.is_running = False


def run_scheduler(symbols: Optional[List[str]] = None,
                  update_interval: Optional[int] = None):
    """
    运行数据更新调度器

    Args:
        symbols: 交易对符号列表
        update_interval: 更新间隔（秒）
    """
    scheduler = DataScheduler(symbols, update_interval)
    scheduler.start()


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 运行调度器
    run_scheduler()
