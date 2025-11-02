"""
数据库模块测试
"""

import unittest
import os
import tempfile
import sqlite3
from database import Database


class TestDatabase(unittest.TestCase):
    """数据库操作测试"""

    def setUp(self):
        """设置测试环境"""
        # 创建临时数据库
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = Database(self.temp_db.name)

    def tearDown(self):
        """清理测试环境"""
        self.db.close()
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)

    def test_database_initialization(self):
        """测试数据库初始化"""
        # 检查数据库文件是否创建
        self.assertTrue(os.path.exists(self.temp_db.name))

        # 检查表是否创建
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table'
            """)
            tables = [row[0] for row in cursor.fetchall()]

            self.assertIn('klines_3m', tables)
            self.assertIn('klines_4h', tables)
            self.assertIn('technical_indicators', tables)
            self.assertIn('perpetual_data', tables)

    def test_insert_klines(self):
        """测试插入 K 线数据"""
        symbol = 'BTCUSDT'
        klines = [
            [1640995200000, 100.0, 101.0, 99.0, 100.5, 1000.0, 1640995299999],
            [1640995300000, 100.5, 102.0, 99.5, 101.0, 1100.0, 1640995399999],
        ]

        # 插入数据
        self.db.insert_klines(symbol, klines, '3m')

        # 验证数据
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM klines_3m WHERE symbol = ?", (symbol,))
            rows = cursor.fetchall()

            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0][1], symbol)
            self.assertEqual(rows[0][2], 1640995200000)

    def test_insert_indicators(self):
        """测试插入技术指标数据"""
        import pandas as pd

        symbol = 'BTCUSDT'
        timestamp = 1640995200000
        timeframe = '3m'

        # 创建模拟指标数据
        indicators = {
            'ema_20': pd.Series([100.5], index=[timestamp]),
            'ema_50': pd.Series([99.5], index=[timestamp]),
            'macd': pd.Series([0.5], index=[timestamp]),
            'macd_signal': pd.Series([0.3], index=[timestamp]),
            'macd_histogram': pd.Series([0.2], index=[timestamp]),
            'rsi_7': pd.Series([55.0], index=[timestamp]),
            'rsi_14': pd.Series([52.0], index=[timestamp]),
            'atr_3': pd.Series([1.5], index=[timestamp]),
            'atr_14': pd.Series([2.0], index=[timestamp]),
            'current_volume': 1000.0,
            'average_volume': 950.0
        }

        # 插入数据
        self.db.insert_indicators(symbol, timestamp, timeframe, indicators)

        # 验证数据
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM technical_indicators
                WHERE symbol = ? AND timestamp = ? AND timeframe = ?
            """, (symbol, timestamp, timeframe))
            row = cursor.fetchone()

            self.assertIsNotNone(row)
            self.assertEqual(row[1], symbol)
            self.assertEqual(row[2], timestamp)
            self.assertEqual(row[3], '3m')

    def test_insert_perp_data(self):
        """测试插入永续合约数据"""
        symbol = 'BTCUSDT'
        timestamp = 1640995200000
        perp_data = {
            'open_interest_latest': 50000.0,
            'open_interest_average': 48000.0,
            'funding_rate': 0.0001
        }

        # 插入数据
        self.db.insert_perp_data(symbol, timestamp, perp_data)

        # 验证数据
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM perpetual_data
                WHERE symbol = ? AND timestamp = ?
            """, (symbol, timestamp))
            row = cursor.fetchone()

            self.assertIsNotNone(row)
            self.assertEqual(row[1], symbol)
            self.assertEqual(row[2], timestamp)
            self.assertEqual(row[3], 50000.0)
            self.assertEqual(row[5], 0.0001)

    def test_get_latest_data(self):
        """测试获取最新数据"""
        symbol = 'BTCUSDT'

        # 插入测试数据
        klines = [
            [1640995200000, 100.0, 101.0, 99.0, 100.5, 1000.0, 1640995299999],
        ]
        self.db.insert_klines(symbol, klines, '3m')

        # 获取数据
        data = self.db.get_latest_data(symbol)

        self.assertIsNotNone(data)
        self.assertEqual(data['symbol'], symbol)
        self.assertIn('current_price', data)
        self.assertIn('intraday', data)
        self.assertIn('long_term', data)
        self.assertIn('perp_data', data)

    def test_get_klines(self):
        """测试获取 K 线数据"""
        symbol = 'BTCUSDT'
        klines = [
            [1640995200000, 100.0, 101.0, 99.0, 100.5, 1000.0, 1640995299999],
            [1640995300000, 100.5, 102.0, 99.5, 101.0, 1100.0, 1640995399999],
        ]
        self.db.insert_klines(symbol, klines, '3m')

        # 获取数据
        df = self.db.get_klines(symbol, '3m', limit=10)

        self.assertIsInstance(df, type(pd.DataFrame()))
        self.assertEqual(len(df), 2)


if __name__ == '__main__':
    import pandas as pd
    unittest.main()
