"""
多时间框架数据预处理器测试
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from multi_timeframe_preprocessor import MultiTimeframeProcessor
from database import Database


class TestMultiTimeframeProcessor(unittest.TestCase):
    """多时间框架处理器测试"""

    def setUp(self):
        """测试前准备"""
        self.processor = MultiTimeframeProcessor()
        self.test_symbol = 'BTCUSDT'

    def tearDown(self):
        """测试后清理"""
        self.processor.close()

    def _create_sample_klines(self, timeframe: str, count: int = 100) -> pd.DataFrame:
        """创建模拟K线数据"""
        np.random.seed(42)
        base_price = 50000
        data = []

        for i in range(count):
            # 生成模拟OHLCV数据
            open_price = base_price + np.random.normal(0, 100)
            high_price = open_price + abs(np.random.normal(0, 50))
            low_price = open_price - abs(np.random.normal(0, 50))
            close_price = open_price + np.random.normal(0, 30)
            volume = np.random.uniform(100, 1000)

            timestamp = datetime.now() - timedelta(hours=count-i)

            data.append({
                'timestamp': timestamp,
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': volume
            })

            base_price = close_price

        df = pd.DataFrame(data)
        if timeframe == '3m':
            df['timestamp'] = datetime.now() - timedelta(minutes=3*count)
        elif timeframe == '4h':
            df['timestamp'] = datetime.now() - timedelta(hours=4*count)

        return df

    @patch('multi_timeframe_preprocessor.Database')
    def test_process_4h_data_success(self, mock_db):
        """测试4小时数据处理成功"""
        # 模拟数据库返回
        mock_db.return_value.get_klines.return_value = self._create_sample_klines('4h', 100)

        result = self.processor.process_4h_data(self.test_symbol)

        # 验证基本结构
        self.assertEqual(result['symbol'], self.test_symbol)
        self.assertEqual(result['timeframe'], '4h')
        self.assertIn('current_price', result)
        self.assertIn('trend', result)
        self.assertIn('momentum', result)
        self.assertIn('support_resistance', result)
        self.assertIn('description', result)

        # 验证趋势结构
        trend = result['trend']
        self.assertIn('direction', trend)
        self.assertIn('strength', trend)
        self.assertIn('price_change_24h', trend)

    def test_process_4h_data_empty(self):
        """测试4小时数据为空"""
        # 使用真实的Database类，但传入不存在的符号
        processor = MultiTimeframeProcessor()
        result = processor.process_4h_data('NONEXISTENT')

        self.assertEqual(result['symbol'], 'NONEXISTENT')
        self.assertEqual(result['timeframe'], '4h')
        self.assertIn('error', result)
        processor.close()

    @patch('multi_timeframe_preprocessor.Database')
    def test_process_3m_data_success(self, mock_db):
        """测试3分钟数据处理成功"""
        mock_db.return_value.get_klines.return_value = self._create_sample_klines('3m', 200)

        result = self.processor.process_3m_data(self.test_symbol)

        # 验证基本结构
        self.assertEqual(result['symbol'], self.test_symbol)
        self.assertEqual(result['timeframe'], '3m')
        self.assertIn('current_price', result)
        self.assertIn('momentum', result)
        self.assertIn('breakout', result)
        self.assertIn('oversold_overbought', result)
        self.assertIn('description', result)

        # 验证动量结构
        momentum = result['momentum']
        self.assertIn('rsi_7', momentum)
        self.assertIn('momentum_5m', momentum)
        self.assertIn('momentum_direction', momentum)

    @patch('multi_timeframe_preprocessor.Database')
    def test_analyze_trend_4h(self, mock_db):
        """测试4小时趋势分析"""
        df = self._create_sample_klines('4h', 50)
        trend = self.processor._analyze_trend_4h(df)

        self.assertIn('direction', trend)
        self.assertIn('strength', trend)
        self.assertIn('sma_20', trend)
        self.assertIn('sma_50', trend)
        self.assertIn('position_vs_sma20', trend)
        self.assertIn('position_vs_sma50', trend)

        # 验证趋势方向枚举
        valid_directions = ['STRONG_UP', 'UP', 'STRONG_DOWN', 'DOWN', 'SIDEWAYS']
        self.assertIn(trend['direction'], valid_directions)

        # 验证强度枚举
        valid_strengths = ['STRONG', 'MEDIUM', 'WEAK']
        self.assertIn(trend['strength'], valid_strengths)

    @patch('multi_timeframe_preprocessor.Database')
    def test_find_support_resistance(self, mock_db):
        """测试支撑阻力位检测"""
        df = self._create_sample_klines('4h', 50)
        sr = self.processor._find_support_resistance(df)

        self.assertIn('nearest_resistance', sr)
        self.assertIn('nearest_support', sr)
        self.assertIn('resistance_distance_pct', sr)
        self.assertIn('support_distance_pct', sr)

        # 如果找到支撑/阻力位，应为数值类型
        if sr['nearest_resistance'] is not None:
            self.assertIsInstance(sr['nearest_resistance'], (int, float))
        if sr['nearest_support'] is not None:
            self.assertIsInstance(sr['nearest_support'], (int, float))

    @patch('multi_timeframe_preprocessor.Database')
    def test_calculate_long_momentum(self, mock_db):
        """测试长期动量计算"""
        df = self._create_sample_klines('4h', 50)
        momentum = self.processor._calculate_long_momentum(df)

        self.assertIn('rsi', momentum)
        self.assertIn('macd', momentum)
        self.assertIn('macd_signal', momentum)
        self.assertIn('momentum_direction', momentum)
        self.assertIn('rsi_signal', momentum)

        # 验证RSI在合理范围
        if momentum['rsi'] is not None:
            self.assertGreaterEqual(momentum['rsi'], 0)
            self.assertLessEqual(momentum['rsi'], 100)

        # 验证动量方向
        valid_momentum = ['OVERBOUGHT', 'OVERSOLD', 'POSITIVE', 'NEGATIVE']
        self.assertIn(momentum['momentum_direction'], valid_momentum)

    @patch('multi_timeframe_preprocessor.Database')
    def test_analyze_momentum_3m(self, mock_db):
        """测试3分钟动量分析"""
        df = self._create_sample_klines('3m', 50)
        momentum = self.processor._analyze_momentum_3m(df)

        self.assertIn('rsi_7', momentum)
        self.assertIn('momentum_5m', momentum)
        self.assertIn('momentum_20m', momentum)
        self.assertIn('momentum_direction', momentum)
        self.assertIn('momentum_strength', momentum)

        # 验证动量强度
        valid_strengths = ['STRONG', 'MEDIUM', 'WEAK']
        self.assertIn(momentum['momentum_strength'], valid_strengths)

        # 验证方向
        self.assertIn(momentum['momentum_direction'], ['UP', 'DOWN'])

    @patch('multi_timeframe_preprocessor.Database')
    def test_detect_breakout(self, mock_db):
        """测试突破检测"""
        df = self._create_sample_klines('3m', 50)
        breakout = self.processor._detect_breakout(df)

        self.assertIn('is_upside_breakout', breakout)
        self.assertIn('is_downside_breakout', breakout)
        self.assertIn('resistance_level', breakout)
        self.assertIn('support_level', breakout)
        self.assertIn('breakout_strength', breakout)

        # 验证布尔值
        self.assertIsInstance(breakout['is_upside_breakout'], bool)
        self.assertIsInstance(breakout['is_downside_breakout'], bool)

        # 不能同时向上和向下突破
        if breakout['is_upside_breakout']:
            self.assertFalse(breakout['is_downside_breakout'])

    @patch('multi_timeframe_preprocessor.Database')
    def test_calculate_oversold_overbought(self, mock_db):
        """测试超买超卖计算"""
        df = self._create_sample_klines('3m', 50)
        oo = self.processor._calculate_oversold_overbought(df)

        self.assertIn('rsi_7', oo)
        self.assertIn('signal', oo)
        self.assertIn('signal_strength', oo)
        self.assertIn('reversal_probability', oo)

        # 验证信号类型
        valid_signals = ['EXTREME_OVERBOUGHT', 'OVERBOUGHT', 'EXTREME_OVERSOLD', 'OVERSOLD', 'NEUTRAL']
        self.assertIn(oo['signal'], valid_signals)

        # 验证RSI范围
        if oo['rsi_7'] is not None:
            self.assertGreaterEqual(oo['rsi_7'], 0)
            self.assertLessEqual(oo['rsi_7'], 100)

    @patch('multi_timeframe_preprocessor.Database')
    def test_analyze_micro_trend(self, mock_db):
        """测试微趋势分析"""
        df = self._create_sample_klines('3m', 50)
        micro = self.processor._analyze_micro_trend(df)

        self.assertIn('direction', micro)
        self.assertIn('ema_10', micro)
        self.assertIn('price_vs_ema10', micro)
        self.assertIn('trend_consistency_pct', micro)
        self.assertIn('trend_strength', micro)

        # 验证方向
        self.assertIn(micro['direction'], ['UP', 'DOWN'])

        # 验证位置
        self.assertIn(micro['price_vs_ema10'], ['above', 'below'])

    @patch('multi_timeframe_preprocessor.Database')
    def test_calculate_volatility(self, mock_db):
        """测试波动率计算"""
        df = self._create_sample_klines('4h', 50)
        vol = self.processor._calculate_volatility(df)

        self.assertIn('current_volatility_pct', vol)
        self.assertIn('volatility_level', vol)

        # 验证波动率级别
        valid_levels = ['HIGH', 'MEDIUM', 'LOW']
        self.assertIn(vol['volatility_level'], valid_levels)

    @patch('multi_timeframe_preprocessor.Database')
    def test_generate_4h_description(self, mock_db):
        """测试4小时描述生成"""
        features = {
            'trend': self.processor._analyze_trend_4h(self._create_sample_klines('4h', 50)),
            'momentum': self.processor._calculate_long_momentum(self._create_sample_klines('4h', 50)),
            'raw_data': {
                'current_price': 50000,
                'price_change_24h': 2.5,
                'volume_trend': 'increasing'
            }
        }

        desc = self.processor._generate_4h_description(features)

        self.assertIsInstance(desc, str)
        self.assertIn('当前价格', desc)
        self.assertIn('趋势分析', desc)
        self.assertIn('动量指标', desc)

    @patch('multi_timeframe_preprocessor.Database')
    def test_generate_3m_description(self, mock_db):
        """测试3分钟描述生成"""
        df = self._create_sample_klines('3m', 50)
        features = {
            'momentum': self.processor._analyze_momentum_3m(df),
            'breakout': self.processor._detect_breakout(df),
            'oversold_overbought': self.processor._calculate_oversold_overbought(df)
        }

        desc = self.processor._generate_3m_description(features)

        self.assertIsInstance(desc, str)
        self.assertIn('短期分析', desc)
        self.assertIn('突破信号', desc)

    @patch('multi_timeframe_preprocessor.Database')
    def test_empty_results(self, mock_db):
        """测试空结果"""
        result_4h = self.processor._empty_4h_result(self.test_symbol)
        result_3m = self.processor._empty_3m_result(self.test_symbol)

        self.assertEqual(result_4h['symbol'], self.test_symbol)
        self.assertEqual(result_4h['timeframe'], '4h')
        self.assertIn('error', result_4h)

        self.assertEqual(result_3m['symbol'], self.test_symbol)
        self.assertEqual(result_3m['timeframe'], '3m')
        self.assertIn('error', result_3m)


if __name__ == '__main__':
    unittest.main()
