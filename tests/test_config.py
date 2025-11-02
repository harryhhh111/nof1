"""
配置模块测试
"""

import unittest
from config import SYMBOLS, UPDATE_INTERVAL, INTERVALS, INDICATOR_PARAMS, DATABASE_PATH, TABLES


class TestConfig(unittest.TestCase):
    """配置参数测试"""

    def test_symbols_not_empty(self):
        """测试交易对列表不为空"""
        self.assertIsInstance(SYMBOLS, list)
        self.assertGreater(len(SYMBOLS), 0)

    def test_update_interval(self):
        """测试更新间隔设置"""
        self.assertIsInstance(UPDATE_INTERVAL, int)
        self.assertGreater(UPDATE_INTERVAL, 0)

    def test_intervals(self):
        """测试时间间隔配置"""
        self.assertIn('intraday', INTERVALS)
        self.assertIn('long_term', INTERVALS)
        self.assertEqual(INTERVALS['intraday'], '3m')
        self.assertEqual(INTERVALS['long_term'], '4h')

    def test_indicator_params(self):
        """测试技术指标参数"""
        self.assertIn('ema_short', INDICATOR_PARAMS)
        self.assertIn('ema_long', INDICATOR_PARAMS)
        self.assertIn('rsi_short', INDICATOR_PARAMS)
        self.assertIn('rsi_long', INDICATOR_PARAMS)

    def test_database_path(self):
        """测试数据库路径"""
        self.assertIsInstance(DATABASE_PATH, str)
        self.assertTrue(DATABASE_PATH)

    def test_tables(self):
        """测试数据库表名"""
        self.assertIn('klines_intraday', TABLES)
        self.assertIn('klines_long_term', TABLES)
        self.assertIn('indicators', TABLES)
        self.assertIn('perp_data', TABLES)


if __name__ == '__main__':
    unittest.main()
