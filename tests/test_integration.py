"""
集成测试

测试整个系统的工作流程，包括数据获取、存储和查询。
"""

import unittest
import tempfile
import os
import pandas as pd
from unittest.mock import Mock, patch, MagicMock


class TestSystemIntegration(unittest.TestCase):
    """系统集成测试"""

    def setUp(self):
        """设置测试环境"""
        # 创建临时数据库
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name

    def tearDown(self):
        """清理测试环境"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    @patch('data_fetcher.ccxt.binance')
    def test_single_symbol_data_flow(self, mock_binance):
        """测试单个交易对数据流程"""
        # 配置模拟
        mock_exchange = MagicMock()
        mock_binance.return_value = mock_exchange

        # 模拟 ticker 数据
        mock_exchange.fetch_ticker.return_value = {
            'last': 50000.0,
            'timestamp': 1640995200000
        }

        # 模拟 K 线数据
        mock_exchange.fetch_ohlcv.side_effect = lambda symbol, timeframe, limit: [
            [1640995200000 + i * 180000, 50000.0 + i, 50100.0 + i, 49900.0 + i,
             50050.0 + i, 1000.0 + i] for i in range(50)
        ] if timeframe == '3m' else [
            [1640995200000 + i * 14400000, 50000.0 + i, 50100.0 + i, 49900.0 + i,
             50050.0 + i, 1000.0 + i] for i in range(50)
        ]

        # 模拟资金费率
        mock_exchange.fetch_funding_rate.return_value = {'fundingRate': 0.0001}

        # 模拟开放利息
        mock_exchange.fetch_open_interest.return_value = {'openInterest': 50000.0}

        # 从 data_fetcher 导入
        from data_fetcher import DataFetcher

        # 执行数据获取
        fetcher = DataFetcher(self.db_path)
        data = fetcher.get_market_data('BTCUSDT')
        fetcher.close()

        # 验证数据结构
        self.assertIn('symbol', data)
        self.assertIn('timestamp', data)
        self.assertIn('current_price', data)
        self.assertIn('intraday', data)
        self.assertIn('long_term', data)
        self.assertIn('perp_data', data)

        # 验证日内数据
        self.assertIn('prices', data['intraday'])
        self.assertIn('ema20', data['intraday'])
        self.assertIn('macd', data['intraday'])
        self.assertIn('rsi_7', data['intraday'])
        self.assertIn('rsi_14', data['intraday'])

        # 验证长期数据
        self.assertIn('ema_20', data['long_term'])
        self.assertIn('ema_50', data['long_term'])
        self.assertIn('atr_3', data['long_term'])
        self.assertIn('atr_14', data['long_term'])

        # 验证永续合约数据
        self.assertIn('funding_rate', data['perp_data'])
        self.assertIn('open_interest_latest', data['perp_data'])

    @patch('data_fetcher.ccxt.binance')
    def test_database_storage(self, mock_binance):
        """测试数据库存储功能"""
        # 配置模拟
        mock_exchange = MagicMock()
        mock_binance.return_value = mock_exchange

        mock_exchange.fetch_ticker.return_value = {
            'last': 50000.0,
            'timestamp': 1640995200000
        }

        mock_exchange.fetch_ohlcv.return_value = [
            [1640995200000 + i * 180000, 50000.0 + i, 50100.0 + i, 49900.0 + i,
             50050.0 + i, 1000.0 + i] for i in range(50)
        ]

        mock_exchange.fetch_funding_rate.return_value = {'fundingRate': 0.0001}
        mock_exchange.fetch_open_interest.return_value = {'openInterest': 50000.0}

        from data_fetcher import DataFetcher
        from database import Database

        # 存储数据
        fetcher = DataFetcher(self.db_path)
        fetcher.get_market_data('BTCUSDT')
        fetcher.close()

        # 从数据库验证数据
        db = Database(self.db_path)
        data = db.get_latest_data('BTCUSDT')
        db.close()

        # 验证数据库中有数据
        self.assertIsNotNone(data)
        self.assertEqual(data['symbol'], 'BTCUSDT')
        self.assertEqual(data['current_price'], 50000.0)

    @patch('data_fetcher.ccxt.binance')
    def test_multiple_symbols(self, mock_binance):
        """测试多个交易对数据获取"""
        # 配置模拟
        mock_exchange = MagicMock()
        mock_binance.return_value = mock_exchange

        mock_exchange.fetch_ticker.return_value = {
            'last': 50000.0,
            'timestamp': 1640995200000
        }

        mock_exchange.fetch_ohlcv.return_value = [
            [1640995200000 + i * 180000, 50000.0 + i, 50100.0 + i, 49900.0 + i,
             50050.0 + i, 1000.0 + i] for i in range(50)
        ]

        mock_exchange.fetch_funding_rate.return_value = {'fundingRate': 0.0001}
        mock_exchange.fetch_open_interest.return_value = {'openInterest': 50000.0}

        from data_fetcher import DataFetcher

        # 获取多个交易对数据
        fetcher = DataFetcher(self.db_path)
        results = fetcher.get_multiple_symbols_data(['BTCUSDT', 'ETHUSDT'])
        fetcher.close()

        # 验证结果
        self.assertIn('BTCUSDT', results)
        self.assertIn('ETHUSDT', results)
        self.assertEqual(len(results), 2)

        for symbol in ['BTCUSDT', 'ETHUSDT']:
            self.assertEqual(results[symbol]['symbol'], symbol)
            self.assertIn('current_price', results[symbol])

    @patch('data_fetcher.ccxt.binance')
    def test_error_handling(self, mock_binance):
        """测试错误处理"""
        # 配置模拟 - 让一个交易对成功，一个失败
        mock_exchange = MagicMock()
        mock_binance.return_value = mock_exchange

        def fetch_ohlcv_with_error(symbol, timeframe, limit):
            if symbol == 'BTCUSDT':
                return [
                    [1640995200000, 50000.0, 50100.0, 49900.0, 50050.0, 1000.0]
                ]
            else:
                raise Exception(f"API error for {symbol}")

        mock_exchange.fetch_ohlcv.side_effect = fetch_ohlcv_with_error
        mock_exchange.fetch_ticker.side_effect = fetch_ohlcv_with_error

        from data_fetcher import DataFetcher

        fetcher = DataFetcher(self.db_path)
        results = fetcher.get_multiple_symbols_data(['BTCUSDT', 'INVALID'])
        fetcher.close()

        # 验证只有成功的交易对在结果中
        self.assertIn('BTCUSDT', results)
        self.assertNotIn('INVALID', results)
        self.assertEqual(len(results), 1)


if __name__ == '__main__':
    unittest.main()
