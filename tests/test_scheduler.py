"""
调度器模块测试
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from scheduler import DataScheduler, ScheduledTask
from datetime import datetime


class TestDataScheduler(unittest.TestCase):
    """数据调度器测试"""

    def setUp(self):
        """设置测试环境"""
        self.test_symbols = ['BTCUSDT', 'ETHUSDT']
        self.test_interval = 10

    @patch('scheduler.DataFetcher')
    def test_init(self, mock_fetcher):
        """测试初始化"""
        scheduler = DataScheduler(self.test_symbols, self.test_interval)

        self.assertEqual(scheduler.symbols, self.test_symbols)
        self.assertEqual(scheduler.update_interval, self.test_interval)
        self.assertIsNotNone(scheduler.data_fetcher)
        self.assertFalse(scheduler.is_running)

    @patch('scheduler.DataFetcher')
    def test_update_market_data(self, mock_fetcher):
        """测试更新市场数据"""
        # 创建模拟数据
        mock_data = {'symbol': 'BTCUSDT', 'price': 50000}
        mock_fetcher_instance = MagicMock()
        mock_fetcher_instance.get_market_data.return_value = mock_data
        mock_fetcher.return_value = mock_fetcher_instance

        scheduler = DataScheduler(self.test_symbols, self.test_interval)

        # 执行更新（不应该抛出异常）
        try:
            scheduler.update_market_data()
            success = True
        except Exception as e:
            print(f"Error: {e}")
            success = False

        self.assertTrue(success)

    @patch('scheduler.DataFetcher')
    def test_start_stop(self, mock_fetcher):
        """测试启动和停止调度器"""
        mock_fetcher_instance = MagicMock()
        mock_fetcher.return_value = mock_fetcher_instance

        scheduler = DataScheduler(['BTCUSDT'], 60)

        # 测试初始状态
        self.assertFalse(scheduler.is_running)

        # 注意：由于调度器会进入循环，我们只测试状态更新
        # 实际测试中会使用更复杂的mock来避免无限循环
        scheduler.is_running = True

        # 测试停止
        scheduler.stop()

        self.assertFalse(scheduler.is_running)
        self.assertTrue(mock_fetcher_instance.close.called)

    @patch('scheduler.DataFetcher')
    def test_get_status(self, mock_fetcher):
        """测试获取调度器状态"""
        scheduler = DataScheduler(self.test_symbols, self.test_interval)

        status = scheduler.get_status()

        self.assertIn('is_running', status)
        self.assertIn('symbols', status)
        self.assertIn('update_interval', status)
        self.assertIn('pending_jobs', status)

        self.assertEqual(status['symbols'], self.test_symbols)
        self.assertEqual(status['update_interval'], self.test_interval)


class TestScheduledTask(unittest.TestCase):
    """定时任务测试"""

    def test_init(self):
        """测试初始化"""
        def test_func():
            return "test"

        task = ScheduledTask(test_func, "arg1", "arg2", key="value")

        self.assertEqual(task.func, test_func)
        self.assertEqual(task.args, ("arg1", "arg2"))
        self.assertEqual(task.kwargs, {'key': 'value'})
        self.assertFalse(task.is_running)

    def test_run(self):
        """测试任务执行"""
        self.executed = False
        self.result = None

        def test_func(arg1, arg2, key=None):
            self.executed = True
            self.result = f"{arg1}-{arg2}-{key}"
            return self.result

        task = ScheduledTask(test_func, "a", "b", key="c")
        result = task.run()

        self.assertTrue(self.executed)
        self.assertEqual(self.result, "a-b-c")
        self.assertEqual(result, "a-b-c")
        self.assertFalse(task.is_running)


if __name__ == '__main__':
    unittest.main()
