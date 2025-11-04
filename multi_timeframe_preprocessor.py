"""
多时间框架数据预处理器

将原始市场数据转换为 LLM 可理解的结构化特征
支持 4小时趋势分析 和 3分钟动量分析
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from database import Database

logger = logging.getLogger(__name__)


class MultiTimeframeProcessor:
    """多时间框架数据处理器"""

    def __init__(self, db_path: Optional[str] = None):
        """初始化处理器"""
        self.db = Database(db_path) if db_path else Database()

    def process_4h_data(self, symbol: str) -> Dict:
        """
        处理4小时数据，提取长期趋势特征

        Args:
            symbol: 交易对符号，如 BTCUSDT

        Returns:
            包含长期趋势特征的字典
        """
        try:
            # 获取4小时K线数据
            df = self.db.get_klines(symbol, '4h', limit=100)

            if df.empty:
                logger.warning(f"未找到 {symbol} 的 4h 数据")
                return self._empty_4h_result(symbol)

            # 计算趋势
            trend = self._analyze_trend_4h(df)

            # 计算支撑/阻力位
            support_resistance = self._find_support_resistance(df)

            # 计算长期动量
            momentum = self._calculate_long_momentum(df)

            # 计算波动率
            volatility = self._calculate_volatility(df)

            # 生成文本描述
            description = self._generate_4h_description({
                'trend': trend,
                'support_resistance': support_resistance,
                'momentum': momentum,
                'volatility': volatility
            })

            # 计算价格变化（有安全检查）
            price_change_24h = None
            price_change_7d = None
            if len(df) >= 7:
                price_change_24h = float((df.iloc[-1]['close'] - df.iloc[-7]['close']) / df.iloc[-7]['close'] * 100)
            if len(df) >= 42:
                price_change_7d = float((df.iloc[-1]['close'] - df.iloc[-42]['close']) / df.iloc[-42]['close'] * 100)

            # 计算成交量趋势
            volume_trend = 'unknown'
            if len(df) >= 14:
                vol_ma_7 = df.tail(7)['volume'].mean()
                vol_ma_14 = df.tail(14).head(7)['volume'].mean()
                volume_trend = 'increasing' if vol_ma_7 > vol_ma_14 else 'decreasing'

            return {
                'symbol': symbol,
                'timeframe': '4h',
                'timestamp': datetime.now().isoformat(),
                'current_price': float(df.iloc[-1]['close']),
                'trend': trend,
                'support_resistance': support_resistance,
                'momentum': momentum,
                'volatility': volatility,
                'description': description,
                'raw_data': {
                    'price_change_24h': price_change_24h,
                    'price_change_7d': price_change_7d,
                    'volume_ma_7': float(df.tail(7)['volume'].mean()) if len(df) >= 7 else None,
                    'volume_trend': volume_trend
                }
            }

        except Exception as e:
            logger.error(f"处理 {symbol} 4h 数据失败: {e}")
            return self._empty_4h_result(symbol)

    def process_3m_data(self, symbol: str) -> Dict:
        """
        处理3分钟数据，提取短期入场特征

        Args:
            symbol: 交易对符号，如 BTCUSDT

        Returns:
            包含短期入场特征的字典
        """
        try:
            # 获取3分钟K线数据
            df = self.db.get_klines(symbol, '3m', limit=200)

            if df.empty:
                logger.warning(f"未找到 {symbol} 的 3m 数据")
                return self._empty_3m_result(symbol)

            # 计算动量
            momentum = self._analyze_momentum_3m(df)

            # 检测突破
            breakout = self._detect_breakout(df)

            # 计算超买超卖
            oversold_overbought = self._calculate_oversold_overbought(df)

            # 计算微趋势
            micro_trend = self._analyze_micro_trend(df)

            # 生成文本描述
            description = self._generate_3m_description({
                'momentum': momentum,
                'breakout': breakout,
                'oversold_overbought': oversold_overbought,
                'micro_trend': micro_trend
            })

            return {
                'symbol': symbol,
                'timeframe': '3m',
                'timestamp': datetime.now().isoformat(),
                'current_price': float(df.iloc[-1]['close']),
                'momentum': momentum,
                'breakout': breakout,
                'oversold_overbought': oversold_overbought,
                'micro_trend': micro_trend,
                'description': description,
                'raw_data': {
                    'price_change_15m': float((df.iloc[-1]['close'] - df.iloc[-5]['close']) / df.iloc[-5]['close'] * 100),
                    'price_change_1h': float((df.iloc[-1]['close'] - df.iloc[-20]['close']) / df.iloc[-20]['close'] * 100),
                    'volume_surge': bool(df.tail(5)['volume'].mean() > df.tail(20)['volume'].mean() * 1.5),
                    'volatility': float(df.tail(20)['close'].std())
                }
            }

        except Exception as e:
            logger.error(f"处理 {symbol} 3m 数据失败: {e}")
            return self._empty_3m_result(symbol)

    def _analyze_trend_4h(self, df: pd.DataFrame) -> Dict:
        """分析4小时趋势"""
        closes = df['close']
        sma_20 = closes.rolling(20).mean()
        sma_50 = closes.rolling(50).mean()

        # 当前价格位置
        current_price = closes.iloc[-1]
        sma_20_val = sma_20.iloc[-1]
        sma_50_val = sma_50.iloc[-1]

        # 趋势方向
        if current_price > sma_20_val > sma_50_val:
            direction = "STRONG_UP"
            strength = "STRONG"
        elif current_price > sma_20_val:
            direction = "UP"
            strength = "MEDIUM"
        elif current_price < sma_20_val < sma_50_val:
            direction = "STRONG_DOWN"
            strength = "STRONG"
        elif current_price < sma_20_val:
            direction = "DOWN"
            strength = "MEDIUM"
        else:
            direction = "SIDEWAYS"
            strength = "WEAK"

        # 趋势角度
        price_change = (current_price - closes.iloc[-7]) / closes.iloc[-7] * 100

        return {
            'direction': direction,
            'strength': strength,
            'price_change_24h': float(price_change),
            'sma_20': float(sma_20_val) if not pd.isna(sma_20_val) else None,
            'sma_50': float(sma_50_val) if not pd.isna(sma_50_val) else None,
            'position_vs_sma20': 'above' if current_price > sma_20_val else 'below',
            'position_vs_sma50': 'above' if current_price > sma_50_val else 'below'
        }

    def _find_support_resistance(self, df: pd.DataFrame, window: int = 20) -> Dict:
        """找到支撑和阻力位"""
        highs = df['high'].rolling(window, center=True).max()
        lows = df['low'].rolling(window, center=True).min()

        # 找到最近的支撑和阻力
        current_price = df.iloc[-1]['close']

        # 阻力位：最近的局部最高点
        resistance_levels = []
        for i in range(len(df) - 50, len(df)):
            if abs(df.iloc[i]['high'] - highs.iloc[i]) < 0.01:
                resistance_levels.append(df.iloc[i]['high'])

        # 支撑位：最近的局部最低点
        support_levels = []
        for i in range(len(df) - 50, len(df)):
            if abs(df.iloc[i]['low'] - lows.iloc[i]) < 0.01:
                support_levels.append(df.iloc[i]['low'])

        nearest_resistance = min([r for r in resistance_levels if r > current_price], default=None)
        nearest_support = max([s for s in support_levels if s < current_price], default=None)

        return {
            'nearest_resistance': float(nearest_resistance) if nearest_resistance else None,
            'nearest_support': float(nearest_support) if nearest_support else None,
            'resistance_distance_pct': float((nearest_resistance - current_price) / current_price * 100) if nearest_resistance else None,
            'support_distance_pct': float((current_price - nearest_support) / current_price * 100) if nearest_support else None
        }

    def _calculate_long_momentum(self, df: pd.DataFrame) -> Dict:
        """计算长期动量"""
        closes = df['close']

        # RSI
        delta = closes.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        # MACD
        ema_12 = closes.ewm(span=12).mean()
        ema_26 = closes.ewm(span=26).mean()
        macd = ema_12 - ema_26
        macd_signal = macd.ewm(span=9).mean()

        current_rsi = rsi.iloc[-1]
        current_macd = macd.iloc[-1]
        current_signal = macd_signal.iloc[-1]

        # 动量强度
        if current_rsi > 70:
            momentum = "OVERBOUGHT"
        elif current_rsi < 30:
            momentum = "OVERSOLD"
        elif current_macd > current_signal:
            momentum = "POSITIVE"
        else:
            momentum = "NEGATIVE"

        return {
            'rsi': float(current_rsi) if not pd.isna(current_rsi) else None,
            'macd': float(current_macd) if not pd.isna(current_macd) else None,
            'macd_signal': float(current_signal) if not pd.isna(current_signal) else None,
            'macd_histogram': float(current_macd - current_signal) if not pd.isna(current_macd) and not pd.isna(current_signal) else None,
            'momentum_direction': momentum,
            'rsi_signal': 'BUY' if current_rsi < 30 else 'SELL' if current_rsi > 70 else 'NEUTRAL'
        }

    def _calculate_volatility(self, df: pd.DataFrame, period: int = 20) -> Dict:
        """计算波动率"""
        returns = df['close'].pct_change()
        volatility = returns.rolling(period).std() * np.sqrt(365) * 100

        current_vol = volatility.iloc[-1]

        return {
            'current_volatility_pct': float(current_vol) if not pd.isna(current_vol) else None,
            'volatility_level': 'HIGH' if current_vol > 50 else 'MEDIUM' if current_vol > 30 else 'LOW'
        }

    def _analyze_momentum_3m(self, df: pd.DataFrame) -> Dict:
        """分析3分钟动量"""
        closes = df['close']

        # 短期RSI
        delta = closes.diff()
        gain = (delta.where(delta > 0, 0)).rolling(7).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(7).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        # 价格动量
        momentum_5 = (closes.iloc[-1] - closes.iloc[-5]) / closes.iloc[-5] * 100
        momentum_20 = (closes.iloc[-1] - closes.iloc[-20]) / closes.iloc[-20] * 100

        return {
            'rsi_7': float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None,
            'momentum_5m': float(momentum_5),
            'momentum_20m': float(momentum_20),
            'momentum_strength': 'STRONG' if abs(momentum_5) > 1 else 'MEDIUM' if abs(momentum_5) > 0.5 else 'WEAK',
            'momentum_direction': 'UP' if momentum_5 > 0 else 'DOWN'
        }

    def _detect_breakout(self, df: pd.DataFrame, window: int = 20) -> Dict:
        """检测突破"""
        highs = df['high']
        lows = df['low']

        # 最近20期的最高和最低
        recent_high = highs.tail(window).max()
        recent_low = lows.tail(window).min()

        current_price = df.iloc[-1]['close']

        # 突破检测
        is_upside_breakout = current_price > recent_high
        is_downside_breakout = current_price < recent_low

        # 成交量确认
        avg_volume = df.tail(window)['volume'].mean()
        current_volume = df.iloc[-1]['volume']
        volume_confirmation = current_volume > avg_volume * 1.5

        return {
            'is_upside_breakout': bool(is_upside_breakout),
            'is_downside_breakout': bool(is_downside_breakout),
            'resistance_level': float(recent_high),
            'support_level': float(recent_low),
            'breakout_strength': 'STRONG' if volume_confirmation else 'WEAK',
            'distance_from_resistance_pct': float((current_price - recent_low) / recent_low * 100) if recent_low else None
        }

    def _calculate_oversold_overbought(self, df: pd.DataFrame) -> Dict:
        """计算超买超卖"""
        closes = df['close']

        # 快速RSI
        delta = closes.diff()
        gain = (delta.where(delta > 0, 0)).rolling(7).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(7).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        current_rsi = rsi.iloc[-1]

        if current_rsi > 80:
            signal = 'EXTREME_OVERBOUGHT'
        elif current_rsi > 70:
            signal = 'OVERBOUGHT'
        elif current_rsi < 20:
            signal = 'EXTREME_OVERSOLD'
        elif current_rsi < 30:
            signal = 'OVERSOLD'
        else:
            signal = 'NEUTRAL'

        return {
            'rsi_7': float(current_rsi) if not pd.isna(current_rsi) else None,
            'signal': signal,
            'signal_strength': 'STRONG' if current_rsi > 80 or current_rsi < 20 else 'MEDIUM',
            'reversal_probability': float(abs(current_rsi - 50) / 50 * 100)
        }

    def _analyze_micro_trend(self, df: pd.DataFrame) -> Dict:
        """分析微趋势"""
        closes = df['close']

        # 最近10期EMA
        ema_10 = closes.ewm(span=10).mean()
        current_price = closes.iloc[-1]
        ema_10_val = ema_10.iloc[-1]

        # 微趋势方向
        micro_trend = 'UP' if current_price > ema_10_val else 'DOWN'

        # 趋势一致性（过去10期）
        trend_consistency = 0
        for i in range(1, min(11, len(closes))):
            if (closes.iloc[-i] > closes.iloc[-i-1]) == (current_price > closes.iloc[-i]):
                trend_consistency += 1

        return {
            'direction': micro_trend,
            'ema_10': float(ema_10_val) if not pd.isna(ema_10_val) else None,
            'price_vs_ema10': 'above' if current_price > ema_10_val else 'below',
            'trend_consistency_pct': float(trend_consistency / 10 * 100),
            'trend_strength': 'STRONG' if trend_consistency >= 8 else 'MEDIUM' if trend_consistency >= 6 else 'WEAK'
        }

    def _generate_4h_description(self, features: Dict) -> str:
        """生成4小时数据文本描述"""
        trend = features['trend']
        momentum = features['momentum']

        # 从 raw_data 获取补充数据（如果存在）
        raw_data = features.get('raw_data', {})
        current_price = raw_data.get('current_price', trend.get('sma_20', 0))
        price_change_24h = raw_data.get('price_change_24h', trend.get('price_change_24h', 0))
        volume_trend = raw_data.get('volume_trend', 'unknown')

        desc = f"""
当前价格：${current_price:.2f}

4小时趋势分析：
- 趋势方向：{trend['direction']} ({trend['strength']} 强度)
- 24小时涨跌：{price_change_24h:+.2f}%
- 价格相对SMA20：{'上方' if trend['position_vs_sma20'] == 'above' else '下方'} (${trend.get('sma_20', 'N/A')})

动量指标：
- RSI14：{momentum['rsi']:.2f} ({momentum['momentum_direction']})
- MACD：{momentum['macd']:.4f}
- 信号：{momentum['rsi_signal']}

成交量趋势：{'增加' if volume_trend == 'increasing' else '减少'}
        """.strip()

        return desc

    def _generate_3m_description(self, features: Dict) -> Dict:
        """生成3分钟数据文本描述"""
        momentum = features['momentum']
        breakout = features['breakout']
        oversold_overbought = features['oversold_overbought']

        desc = f"""
3分钟短期分析：
- 动量方向：{momentum['momentum_direction']} ({momentum['momentum_strength']} 强度)
- 5分钟涨跌：{momentum['momentum_5m']:+.2f}%
- RSI7：{momentum['rsi_7']:.2f} ({oversold_overbought['signal']})

突破信号：
- {'向上突破' if breakout['is_upside_breakout'] else '向下突破' if breakout['is_downside_breakout'] else '无突破'}
- 阻力位：${breakout['resistance_level']:.2f}
- 支撑位：${breakout['support_level']:.2f}
        """.strip()

        return desc

    def _empty_4h_result(self, symbol: str) -> Dict:
        """空结果"""
        return {
            'symbol': symbol,
            'timeframe': '4h',
            'error': 'No data available',
            'trend': None,
            'momentum': None,
            'support_resistance': None
        }

    def _empty_3m_result(self, symbol: str) -> Dict:
        """空结果"""
        return {
            'symbol': symbol,
            'timeframe': '3m',
            'error': 'No data available',
            'momentum': None,
            'breakout': None,
            'oversold_overbought': None
        }

    def close(self):
        """关闭数据库连接"""
        self.db.close()


if __name__ == '__main__':
    # 测试代码
    processor = MultiTimeframeProcessor()

    # 测试处理
    result_4h = processor.process_4h_data('BTCUSDT')
    result_3m = processor.process_3m_data('BTCUSDT')

    print("4小时数据分析:")
    print(result_4h)
    print("\n3分钟数据分析:")
    print(result_3m)

    processor.close()
