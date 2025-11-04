"""
数据获取模块

从交易所 API 获取市场数据，并计算技术指标。
"""

import ccxt
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from indicators import TechnicalIndicators
from database import Database
import config

logger = logging.getLogger(__name__)


class DataFetcher:
    """数据获取类"""

    def __init__(self, db_path: Optional[str] = None):
        """
        初始化数据获取器

        Args:
            db_path: 数据库路径
        """
        # 使用配置文件中的交易所配置
        import config
        self.exchange = ccxt.binance(config.EXCHANGE_CONFIG)
        self.db = Database(db_path) if db_path else Database()
        self.ti = TechnicalIndicators()
        self.use_testnet = config.USE_TESTNET

        # 记录当前模式
        mode = "Testnet" if self.use_testnet else "Real"
        logger.info(f"数据获取器已初始化 - 模式: {mode}")

    def get_klines(self, symbol: str, timeframe: str = '3m', limit: int = 100) -> List:
        """
        获取 K 线数据

        Args:
            symbol: 交易对符号
            timeframe: 时间框架 ('1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d')
            limit: 返回数据条数

        Returns:
            K 线数据列表
        """
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            logger.info(f"获取 {symbol} {timeframe} K 线数据 {len(ohlcv)} 条")
            return ohlcv
        except Exception as e:
            logger.error(f"获取 {symbol} {timeframe} K 线数据失败: {e}")
            raise

    def get_ticker(self, symbol: str) -> Dict:
        """
        获取交易对 ticker 信息

        Args:
            symbol: 交易对符号

        Returns:
            ticker 数据字典
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            logger.debug(f"获取 {symbol} ticker 数据成功")
            return ticker
        except Exception as e:
            logger.error(f"获取 {symbol} ticker 数据失败: {e}")
            raise

    def get_funding_rate(self, symbol: str) -> Optional[float]:
        """
        获取永续合约资金费率

        Args:
            symbol: 交易对符号

        Returns:
            资金费率
        """
        try:
            funding_rate = self.exchange.fetch_funding_rate(symbol)
            rate = funding_rate.get('fundingRate')
            logger.debug(f"获取 {symbol} 资金费率: {rate}")
            return rate
        except Exception as e:
            logger.warning(f"获取 {symbol} 资金费率失败 (可能不是永续合约): {e}")
            return None

    def get_open_interest(self, symbol: str) -> Optional[Dict]:
        """
        获取开放利息数据

        Args:
            symbol: 交易对符号

        Returns:
            开放利息数据字典
        """
        try:
            # 尝试从 Futures API 获取开放利息
            if hasattr(self.exchange, 'fetch_open_interest'):
                oi_data = self.exchange.fetch_open_interest(symbol)
                logger.debug(f"获取 {symbol} 开放利息数据成功")
                return oi_data
            else:
                logger.warning("交易所不支持开放利息查询")
                return None
        except Exception as e:
            logger.warning(f"获取 {symbol} 开放利息失败: {e}")
            return None

    def calculate_all_indicators(self, klines: List) -> Dict:
        """
        计算所有技术指标

        Args:
            klines: K 线数据列表

        Returns:
            技术指标数据字典
        """
        try:
            df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

            # 确保数据类型正确
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col])

            indicators = self.ti.calculate_all_indicators(df, config.INDICATOR_PARAMS)
            logger.debug(f"计算完成技术指标: {list(indicators.keys())}")
            return indicators
        except Exception as e:
            logger.error(f"计算技术指标失败: {e}")
            raise

    def get_market_data(self, symbol: str) -> Dict:
        """
        获取完整市场数据

        Args:
            symbol: 交易对符号

        Returns:
            完整市场数据字典
        """
        try:
            # 获取当前价格
            ticker = self.get_ticker(symbol)
            current_price = ticker['last']
            timestamp = int(ticker['timestamp'])

            # 获取 3 分钟 K 线数据 (用于日内数据)
            klines_3m = self.get_klines(symbol, '3m', limit=50)

            # 获取 4 小时 K 线数据 (用于长期数据)
            klines_4h = self.get_klines(symbol, '4h', limit=50)

            # 计算技术指标
            indicators_3m = self.calculate_all_indicators(klines_3m)
            indicators_4h = self.calculate_all_indicators(klines_4h)

            # 获取永续合约数据
            funding_rate = self.get_funding_rate(symbol)
            oi_data = self.get_open_interest(symbol)

            # 构建返回数据
            market_data = {
                'symbol': symbol,
                'timestamp': datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                'current_price': current_price,
                'intraday': self._format_intraday_data(klines_3m, indicators_3m),
                'long_term': self._format_long_term_data(klines_4h, indicators_4h),
                'perp_data': {
                    'open_interest_latest': oi_data.get('openInterest') if oi_data else None,
                    'open_interest_average': self._calculate_average_oi(symbol) if oi_data else None,
                    'funding_rate': funding_rate
                }
            }

            # 保存到数据库
            self._save_to_database(symbol, klines_3m, klines_4h, indicators_3m, indicators_4h,
                                 market_data['perp_data'])

            logger.info(f"获取 {symbol} 完整市场数据成功")
            return market_data

        except Exception as e:
            logger.error(f"获取 {symbol} 市场数据失败: {e}")
            raise

    def _format_intraday_data(self, klines: List, indicators: Dict) -> Dict:
        """
        格式化日内数据

        Args:
            klines: K 线数据
            indicators: 技术指标数据

        Returns:
            格式化后的日内数据
        """
        # 价格数据（最近10个数据点）
        prices = [float(k[4]) for k in klines[-10:]]

        # EMA 20 数据
        ema20_values = []
        if 'ema_20' in indicators and isinstance(indicators['ema_20'], pd.Series):
            ema20_values = indicators['ema_20'].dropna().tolist()[-10:]

        # MACD 数据
        macd_values = []
        if 'macd' in indicators and isinstance(indicators['macd'], pd.Series):
            macd_values = indicators['macd'].dropna().tolist()[-10:]

        # RSI 7 数据
        rsi_7_values = []
        if 'rsi_7' in indicators and isinstance(indicators['rsi_7'], pd.Series):
            rsi_7_values = indicators['rsi_7'].dropna().tolist()[-10:]

        # RSI 14 数据
        rsi_14_values = []
        if 'rsi_14' in indicators and isinstance(indicators['rsi_14'], pd.Series):
            rsi_14_values = indicators['rsi_14'].dropna().tolist()[-10:]

        return {
            'prices': prices,
            'ema20': ema20_values,
            'macd': macd_values,
            'rsi_7': rsi_7_values,
            'rsi_14': rsi_14_values
        }

    def _format_long_term_data(self, klines: List, indicators: Dict) -> Dict:
        """
        格式化长期数据

        Args:
            klines: K 线数据
            indicators: 技术指标数据

        Returns:
            格式化后的长期数据
        """
        # 获取最新的指标值
        ema_20 = indicators.get('ema_20', pd.Series()).iloc[-1] if 'ema_20' in indicators else None
        ema_50 = indicators.get('ema_50', pd.Series()).iloc[-1] if 'ema_50' in indicators else None
        atr_3 = indicators.get('atr_3', pd.Series()).iloc[-1] if 'atr_3' in indicators else None
        atr_14 = indicators.get('atr_14', pd.Series()).iloc[-1] if 'atr_14' in indicators else None
        volume_current = indicators.get('current_volume')
        volume_average = indicators.get('average_volume')

        # MACD 数据
        macd_values = []
        if 'macd' in indicators and isinstance(indicators['macd'], pd.Series):
            macd_values = indicators['macd'].dropna().tolist()[-20:]

        # RSI 14 数据
        rsi_14_values = []
        if 'rsi_14' in indicators and isinstance(indicators['rsi_14'], pd.Series):
            rsi_14_values = indicators['rsi_14'].dropna().tolist()[-20:]

        return {
            'ema_20': float(ema_20) if ema_20 is not None and not pd.isna(ema_20) else None,
            'ema_50': float(ema_50) if ema_50 is not None and not pd.isna(ema_50) else None,
            'atr_3': float(atr_3) if atr_3 is not None and not pd.isna(atr_3) else None,
            'atr_14': float(atr_14) if atr_14 is not None and not pd.isna(atr_14) else None,
            'volume_current': float(volume_current) if volume_current is not None else None,
            'volume_average': float(volume_average) if volume_average is not None else None,
            'macd': macd_values,
            'rsi_14': rsi_14_values
        }

    def _calculate_average_oi(self, symbol: str) -> Optional[float]:
        """
        计算平均开放利息

        Args:
            symbol: 交易对符号

        Returns:
            平均开放利息
        """
        # 这里可以实现从数据库查询历史开放利息并计算平均值
        # 目前返回 None，等待完整实现
        return None

    def _save_to_database(self, symbol: str, klines_3m: List, klines_4h: List,
                         indicators_3m: Dict, indicators_4h: Dict, perp_data: Dict):
        """
        保存数据到数据库

        Args:
            symbol: 交易对符号
            klines_3m: 3分钟 K 线数据
            klines_4h: 4小时 K 线数据
            indicators_3m: 3分钟技术指标
            indicators_4h: 4小时技术指标
            perp_data: 永续合约数据
        """
        try:
            # 保存 K 线数据
            self.db.insert_klines(symbol, klines_3m, '3m')
            self.db.insert_klines(symbol, klines_4h, '4h')

            # 保存技术指标（3分钟）
            if klines_3m:
                latest_timestamp = klines_3m[-1][0]
                self.db.insert_indicators(symbol, latest_timestamp, '3m', indicators_3m)

            # 保存技术指标（4小时）
            if klines_4h:
                latest_timestamp = klines_4h[-1][0]
                self.db.insert_indicators(symbol, latest_timestamp, '4h', indicators_4h)

            # 保存永续合约数据
            if klines_3m:
                latest_timestamp = klines_3m[-1][0]
                self.db.insert_perp_data(symbol, latest_timestamp, perp_data)

            logger.debug(f"保存 {symbol} 数据到数据库成功")
        except Exception as e:
            logger.error(f"保存 {symbol} 数据到数据库失败: {e}")

    def get_multiple_symbols_data(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        获取多个交易对的市场数据

        Args:
            symbols: 交易对符号列表

        Returns:
            多个交易对的市场数据字典
        """
        results = {}
        for symbol in symbols:
            try:
                data = self.get_market_data(symbol)
                results[symbol] = data
            except Exception as e:
                logger.error(f"获取 {symbol} 数据失败，跳过: {e}")
                continue

        return results

    def close(self):
        """关闭资源"""
        self.db.close()
        logger.info("数据获取器已关闭")
