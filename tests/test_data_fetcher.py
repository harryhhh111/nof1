"""
数据获取模块测试
"""

import unittest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from data_fetcher import DataFetcher


class TestDataFetcher(unittest.TestCase):
    """数据获取器测试"""

    def setUp(self):
        """设置测试环境"""
        # 创建临时数据库
        import tempfile
        import os
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name

    def tearDown(self):
        """清理测试环境"""
        import os
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    @patch('data_fetcher.ccxt.binance')
    def test_init(self, mock_binance):
        """测试初始化"""
        mock_exchange = MagicMock()
        mock_binance.return_value = mock_exchange

        fetcher = DataFetcher(self.db_path)

        self.assertIsNotNone(fetcher.exchange)
        self.assertIsNotNone(fetcher.db)
        self.assertIsNotNone(fetcher.ti)

    @patch('data_fetcher.ccxt.binance')
    def test_calculate_all_indicators(self, mock_binance):
        """测试技术指标计算"""
        mock_exchange = MagicMock()
        mock_binance.return_value = mock_exchange

        fetcher = DataFetcher(self.db_path)

        # 创建测试 K 线数据
        klines = [
            [1640995200000 + i * 180000, 100.0 + i, 101.0 + i, 99.0 + i,
             100.5 + i, 1000.0 + i] for i in range(50)
        ]

        # 计算指标
        indicators = fetcher.calculate_all_indicators(klines)

        # 验证指标
        self.assertIn('ema_20', indicators)
        self.assertIn('ema_50', indicators)
        self.assertIn('macd', indicators)
        self.assertIn('rsi_7', indicators)
        self.assertIn('rsi_14', indicators)
        self.assertIn('atr_3', indicators)
        self.assertIn('atr_14', indicators)

        # 验证指标是 pandas Series
        self.assertIsInstance(indicators['ema_20'], pd.Series)

    def test_format_intraday_data(self):
        """测试日内数据格式化"""
        # 创建测试数据
        klines = [[1640995200000 + i * 180000, 100.0 + i, 101.0 + i,
                   99.0 + i, 100.5 + i, 1000.0 + i] for i in range(20)]

        import pandas as pd
        indicators = {
            'ema_20': pd.Series([100.5 + i for i in range(20)],
                               index=[k[0] for k in klines]),
            'macd': pd.Series([0.5 + i * 0.01 for i in range(20)],
                              index=[k[0] for k in klines]),
            'rsi_7': pd.Series([50.0 + i for i in range(20)],
                               index=[k[0] for k in klines]),
            'rsi_14': pd.Series([52.0 + i for i in range(20)],
                                index=[k[0] for k in klines])
        }

        fetcher = DataFetcher(self.db_path)
        intraday_data = fetcher._format_intraday_data(klines, indicators)

        # 验证格式化结果
        self.assertIn('prices', intraday_data)
        self.assertIn('ema20', intraday_data)
        self.assertIn('macd', intraday_data)
        self.assertIn('rsi_7', intraday_data)
        self.assertIn('rsi_14', intraday_data)

        # 验证数据长度（最近10个点）
        self.assertEqual(len(intraday_data['prices']), 10)
        self.assertEqual(len(intraday_data['ema20']), 10)

    def test_format_long_term_data(self):
        """测试长期数据格式化"""
        klines = [[1640995200000 + i * 14400000, 100.0 + i, 101.0 + i,
                   99.0 + i, 100.5 + i, 1000.0 + i] for i in range(20)]

        import pandas as pd
        indicators = {
            'ema_20': pd.Series([100.5 + i for i in range(20)],
                               index=[k[0] for k in klines]),
            'ema_50': pd.Series([99.5 + i for i in range(20)],
                                index=[k[0] for k in klines]),
            'atr_3': pd.Series([1.5 + i * 0.1 for i in range(20)],
                               index=[k[0] for k in klines]),
            'atr_14': pd.Series([2.0 + i * 0.1 for i in range(20)],
                                index=[k[0] for k in klines]),
            'current_volume': 1000.0,
            'average_volume': 950.0,
            'macd': pd.Series([0.5 + i * 0.01 for i in range(20)],
                              index=[k[0] for k in klines]),
            'rsi_14': pd.Series([52.0 + i for i in range(20)],
                                index=[k[0] for k in klines])
        }

        fetcher = DataFetcher(self.db_path)
        long_term_data = fetcher._format_long_term_data(klines, indicators)

        # 验证格式化结果
        self.assertIn('ema_20', long_term_data)
        self.assertIn('ema_50', long_term_data)
        self.assertIn('atr_3', long_term_data)
        self.assertIn('atr_14', long_term_data)
        self.assertIn('volume_current', long_term_data)
        self.assertIn('volume_average', long_term_data)
        self.assertIn('macd', long_term_data)
        self.assertIn('rsi_14', long_term_data)

        # 验证最新值
        self.assertIsNotNone(long_term_data['ema_20'])
        self.assertIsNotNone(long_term_data['ema_50'])
        self.assertEqual(long_term_data['volume_current'], 1000.0)
        self.assertEqual(long_term_data['volume_average'], 950.0)


if __name__ == '__main__':
    unittest.main()
