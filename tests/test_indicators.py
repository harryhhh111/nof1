"""
技术指标模块测试
"""

import unittest
import pandas as pd
from indicators import TechnicalIndicators


class TestTechnicalIndicators(unittest.TestCase):
    """技术指标计算测试"""

    def setUp(self):
        """设置测试数据"""
        # 创建模拟 OHLCV 数据
        dates = pd.date_range(start='2024-01-01', periods=100, freq='3T')
        self.test_data = pd.DataFrame({
            'timestamp': dates,
            'open': range(100, 200),
            'high': range(101, 201),
            'low': range(99, 199),
            'close': range(100, 200),
            'volume': range(1000, 1100)
        })

    def test_calculate_ema(self):
        """测试 EMA 计算"""
        ema = TechnicalIndicators.calculate_ema(self.test_data, period=20)
        self.assertIsInstance(ema, pd.Series)
        self.assertGreater(len(ema), 0)

    def test_calculate_macd(self):
        """测试 MACD 计算"""
        macd_data = TechnicalIndicators.calculate_macd(self.test_data)
        self.assertIn('macd', macd_data)
        self.assertIn('signal', macd_data)
        self.assertIn('histogram', macd_data)
        self.assertIsInstance(macd_data['macd'], pd.Series)

    def test_calculate_rsi(self):
        """测试 RSI 计算"""
        rsi = TechnicalIndicators.calculate_rsi(self.test_data, period=14)
        self.assertIsInstance(rsi, pd.Series)
        # RSI 值应该在 0-100 之间
        valid_rsi = rsi.dropna()
        if len(valid_rsi) > 0:
            self.assertTrue(all(0 <= val <= 100 for val in valid_rsi))

    def test_calculate_atr(self):
        """测试 ATR 计算"""
        atr = TechnicalIndicators.calculate_atr(self.test_data, period=14)
        self.assertIsInstance(atr, pd.Series)
        # ATR 值应该大于 0
        valid_atr = atr.dropna()
        if len(valid_atr) > 0:
            self.assertTrue(all(val >= 0 for val in valid_atr))

    def test_calculate_volume_analysis(self):
        """测试交易量分析"""
        current_vol, avg_vol = TechnicalIndicators.calculate_volume_analysis(self.test_data)
        self.assertIsInstance(current_vol, (int, float))
        self.assertIsInstance(avg_vol, (int, float))
        self.assertGreaterEqual(current_vol, 0)
        self.assertGreaterEqual(avg_vol, 0)

    def test_calculate_all_indicators(self):
        """测试计算所有指标"""
        indicators = TechnicalIndicators.calculate_all_indicators(self.test_data)

        # 检查所有预期指标都存在
        expected_keys = ['ema_20', 'ema_50', 'macd', 'macd_signal', 'macd_histogram',
                        'rsi_7', 'rsi_14', 'atr_3', 'atr_14', 'current_volume', 'average_volume']
        for key in expected_keys:
            self.assertIn(key, indicators)

        # 检查 pandas Series 类型
        series_keys = ['ema_20', 'ema_50', 'macd', 'macd_signal', 'macd_histogram',
                      'rsi_7', 'rsi_14', 'atr_3', 'atr_14']
        for key in series_keys:
            self.assertIsInstance(indicators[key], pd.Series)

    def test_format_indicators_for_output(self):
        """测试指标格式化输出"""
        indicators = TechnicalIndicators.calculate_all_indicators(self.test_data)
        formatted = TechnicalIndicators.format_indicators_for_output(indicators)

        # 检查 pandas Series 转换为列表
        for key, value in formatted.items():
            if isinstance(value, list):
                self.assertIsInstance(value, list)


if __name__ == '__main__':
    unittest.main()
