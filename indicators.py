"""
技术指标计算模块

实现各种技术指标的计算，包括 EMA、MACD、RSI、ATR 等。
使用纯 pandas 实现，不依赖第三方库。
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


class TechnicalIndicators:
    """技术指标计算类"""

    @staticmethod
    def calculate_ema(data: pd.DataFrame, period: int = 20) -> pd.Series:
        """
        计算指数移动平均线 (EMA)

        Args:
            data: 包含价格数据的 DataFrame
            period: 周期数

        Returns:
            EMA 值序列
        """
        return data['close'].ewm(span=period, adjust=False).mean()

    @staticmethod
    def calculate_sma(data: pd.DataFrame, period: int = 20) -> pd.Series:
        """
        计算简单移动平均线 (SMA)

        Args:
            data: 包含价格数据的 DataFrame
            period: 周期数

        Returns:
            SMA 值序列
        """
        return data['close'].rolling(window=period).mean()

    @staticmethod
    def calculate_macd(data: pd.DataFrame,
                       fast: int = 12,
                       slow: int = 26,
                       signal: int = 9) -> Dict[str, pd.Series]:
        """
        计算 MACD (移动平均收敛散度)

        Args:
            data: 包含价格数据的 DataFrame
            fast: 快线周期
            slow: 慢线周期
            signal: 信号线周期

        Returns:
            包含 MACD、信号线和柱状图的字典
        """
        # 计算快速和慢速 EMA
        ema_fast = data['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = data['close'].ewm(span=slow, adjust=False).mean()

        # 计算 MACD 线
        macd_line = ema_fast - ema_slow

        # 计算信号线
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()

        # 计算柱状图
        histogram = macd_line - signal_line

        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }

    @staticmethod
    def calculate_rsi(data: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        计算相对强弱指数 (RSI)

        Args:
            data: 包含价格数据的 DataFrame
            period: 周期数

        Returns:
            RSI 值序列
        """
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    @staticmethod
    def calculate_atr(data: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        计算平均真实波幅 (ATR)

        Args:
            data: 包含 OHLC 数据的 DataFrame
            period: 周期数

        Returns:
            ATR 值序列
        """
        high = data['high']
        low = data['low']
        close = data['close']

        # 计算 True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())

        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # 计算 ATR
        atr = true_range.rolling(window=period).mean()

        return atr

    @staticmethod
    def calculate_volume_analysis(data: pd.DataFrame,
                                  window: int = 20) -> Tuple[float, float]:
        """
        计算交易量分析

        Args:
            data: 包含交易量数据的 DataFrame
            window: 计算平均交易量的窗口期

        Returns:
            当前交易量和平均交易量的元组
        """
        current_volume = float(data['volume'].iloc[-1])
        avg_volume = float(data['volume'].tail(window).mean())
        return current_volume, avg_volume

    @staticmethod
    def calculate_all_indicators(data: pd.DataFrame,
                                 params: Dict[str, int] = None) -> Dict:
        """
        计算所有技术指标

        Args:
            data: 包含 OHLCV 数据的 DataFrame
            params: 指标参数字典

        Returns:
            包含所有技术指标的字典
        """
        if params is None:
            params = {
                'ema_short': 20,
                'ema_long': 50,
                'rsi_short': 7,
                'rsi_long': 14,
                'atr_short': 3,
                'atr_long': 14
            }

        result = {}

        # EMA 指标
        result['ema_20'] = TechnicalIndicators.calculate_ema(data, params['ema_short'])
        result['ema_50'] = TechnicalIndicators.calculate_ema(data, params['ema_long'])

        # MACD 指标
        macd = TechnicalIndicators.calculate_macd(data)
        result['macd'] = macd['macd']
        result['macd_signal'] = macd['signal']
        result['macd_histogram'] = macd['histogram']

        # RSI 指标
        result['rsi_7'] = TechnicalIndicators.calculate_rsi(data, params['rsi_short'])
        result['rsi_14'] = TechnicalIndicators.calculate_rsi(data, params['rsi_long'])

        # ATR 指标
        result['atr_3'] = TechnicalIndicators.calculate_atr(data, params['atr_short'])
        result['atr_14'] = TechnicalIndicators.calculate_atr(data, params['atr_long'])

        # 交易量分析
        current_vol, avg_vol = TechnicalIndicators.calculate_volume_analysis(data)
        result['current_volume'] = current_vol
        result['average_volume'] = avg_vol

        return result

    @staticmethod
    def format_indicators_for_output(indicators: Dict) -> Dict:
        """
        格式化指标数据用于输出

        Args:
            indicators: 原始指标数据

        Returns:
            格式化后的指标数据
        """
        formatted = {}

        # 将 pandas Series 转换为列表，移除 NaN 值
        for key, value in indicators.items():
            if isinstance(value, pd.Series):
                formatted[key] = value.dropna().tolist()
            else:
                formatted[key] = value

        return formatted


def calculate_single_indicator(data: pd.DataFrame, indicator_type: str, **kwargs):
    """
    计算单个技术指标

    Args:
        data: OHLCV 数据
        indicator_type: 指标类型 ('ema', 'macd', 'rsi', 'atr')
        **kwargs: 指标参数

    Returns:
        计算结果
    """
    ti = TechnicalIndicators()

    if indicator_type == 'ema':
        period = kwargs.get('period', 20)
        return ti.calculate_ema(data, period)
    elif indicator_type == 'macd':
        fast = kwargs.get('fast', 12)
        slow = kwargs.get('slow', 26)
        signal = kwargs.get('signal', 9)
        return ti.calculate_macd(data, fast, slow, signal)
    elif indicator_type == 'rsi':
        period = kwargs.get('period', 14)
        return ti.calculate_rsi(data, period)
    elif indicator_type == 'atr':
        period = kwargs.get('period', 14)
        return ti.calculate_atr(data, period)
    else:
        raise ValueError(f"Unsupported indicator type: {indicator_type}")
