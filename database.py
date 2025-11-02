"""
数据库操作模块

负责数据的持久化存储，包括 K 线数据、技术指标和永续合约数据。
"""

import sqlite3
import pandas as pd
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging
from config import DATABASE_PATH, TABLES

logger = logging.getLogger(__name__)


class Database:
    """数据库操作类"""

    def __init__(self, db_path: str = DATABASE_PATH):
        """
        初始化数据库连接

        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """初始化数据库表结构"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # K 线数据表（3分钟）
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {TABLES['klines_intraday']} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timestamp INTEGER NOT NULL,
                    open REAL NOT NULL,
                    high REAL NOT NULL,
                    low REAL NOT NULL,
                    close REAL NOT NULL,
                    volume REAL NOT NULL,
                    close_time INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, timestamp)
                )
            """)

            # K 线数据表（4小时）
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {TABLES['klines_long_term']} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timestamp INTEGER NOT NULL,
                    open REAL NOT NULL,
                    high REAL NOT NULL,
                    low REAL NOT NULL,
                    close REAL NOT NULL,
                    volume REAL NOT NULL,
                    close_time INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, timestamp)
                )
            """)

            # 技术指标表
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {TABLES['indicators']} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timestamp INTEGER NOT NULL,
                    timeframe TEXT NOT NULL,
                    ema_20 REAL,
                    ema_50 REAL,
                    macd REAL,
                    macd_signal REAL,
                    macd_histogram REAL,
                    rsi_7 REAL,
                    rsi_14 REAL,
                    atr_3 REAL,
                    atr_14 REAL,
                    current_volume REAL,
                    average_volume REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, timestamp, timeframe)
                )
            """)

            # 永续合约数据表
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {TABLES['perp_data']} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timestamp INTEGER NOT NULL,
                    open_interest_latest REAL,
                    open_interest_average REAL,
                    funding_rate REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, timestamp)
                )
            """)

            # 创建索引
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_{TABLES['klines_intraday']}_symbol_timestamp
                ON {TABLES['klines_intraday']}(symbol, timestamp)
            """)

            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_{TABLES['klines_long_term']}_symbol_timestamp
                ON {TABLES['klines_long_term']}(symbol, timestamp)
            """)

            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_{TABLES['indicators']}_symbol_timestamp
                ON {TABLES['indicators']}(symbol, timestamp)
            """)

            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_{TABLES['perp_data']}_symbol_timestamp
                ON {TABLES['perp_data']}(symbol, timestamp)
            """)

            conn.commit()
            logger.info("数据库初始化完成")

    def insert_klines(self, symbol: str, klines: List, timeframe: str = '3m'):
        """
        插入 K 线数据

        Args:
            symbol: 交易对符号
            klines: K 线数据列表
            timeframe: 时间框架 ('3m' 或 '4h')
        """
        table_name = TABLES['klines_intraday'] if timeframe == '3m' else TABLES['klines_long_term']

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            for kline in klines:
                cursor.execute(f"""
                    INSERT OR REPLACE INTO {table_name}
                    (symbol, timestamp, open, high, low, close, volume, close_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    symbol,
                    kline[0],  # Open time
                    float(kline[1]),  # Open price
                    float(kline[2]),  # High price
                    float(kline[3]),  # Low price
                    float(kline[4]),  # Close price
                    float(kline[5]),  # Volume
                    kline[6]  # Close time
                ))

            conn.commit()
            logger.info(f"插入 {len(klines)} 条 {symbol} {timeframe} K 线数据")

    def insert_indicators(self, symbol: str, timestamp: int,
                         timeframe: str, indicators: Dict):
        """
        插入技术指标数据

        Args:
            symbol: 交易对符号
            timestamp: 时间戳
            timeframe: 时间框架
            indicators: 技术指标数据
        """
        import pandas as pd

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 从 pandas Series 中获取指定 timestamp 的值
            def get_series_value(series, ts):
                if series is None or not isinstance(series, pd.Series):
                    return None
                # 尝试通过索引匹配
                if ts in series.index:
                    return series.get(ts)
                # 否则获取最后一个非NaN值
                return series.dropna().iloc[-1] if len(series.dropna()) > 0 else None

            # 获取各指标值
            ema_20 = get_series_value(indicators.get('ema_20'), timestamp)
            ema_50 = get_series_value(indicators.get('ema_50'), timestamp)
            macd = get_series_value(indicators.get('macd'), timestamp)
            macd_signal = get_series_value(indicators.get('macd_signal'), timestamp)
            macd_histogram = get_series_value(indicators.get('macd_histogram'), timestamp)
            rsi_7 = get_series_value(indicators.get('rsi_7'), timestamp)
            rsi_14 = get_series_value(indicators.get('rsi_14'), timestamp)
            atr_3 = get_series_value(indicators.get('atr_3'), timestamp)
            atr_14 = get_series_value(indicators.get('atr_14'), timestamp)
            current_volume = indicators.get('current_volume')
            average_volume = indicators.get('average_volume')

            cursor.execute(f"""
                INSERT OR REPLACE INTO {TABLES['indicators']}
                (symbol, timestamp, timeframe, ema_20, ema_50, macd, macd_signal,
                 macd_histogram, rsi_7, rsi_14, atr_3, atr_14, current_volume,
                 average_volume)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol,
                timestamp,
                timeframe,
                ema_20,
                ema_50,
                macd,
                macd_signal,
                macd_histogram,
                rsi_7,
                rsi_14,
                atr_3,
                atr_14,
                current_volume,
                average_volume
            ))

            conn.commit()
            logger.info(f"插入 {symbol} {timeframe} 技术指标数据")

    def insert_perp_data(self, symbol: str, timestamp: int, perp_data: Dict):
        """
        插入永续合约数据

        Args:
            symbol: 交易对符号
            timestamp: 时间戳
            perp_data: 永续合约数据
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(f"""
                INSERT OR REPLACE INTO {TABLES['perp_data']}
                (symbol, timestamp, open_interest_latest, open_interest_average, funding_rate)
                VALUES (?, ?, ?, ?, ?)
            """, (
                symbol,
                timestamp,
                perp_data.get('open_interest_latest'),
                perp_data.get('open_interest_average'),
                perp_data.get('funding_rate')
            ))

            conn.commit()
            logger.info(f"插入 {symbol} 永续合约数据")

    def get_klines(self, symbol: str, timeframe: str = '3m',
                   limit: int = 100) -> pd.DataFrame:
        """
        获取 K 线数据

        Args:
            symbol: 交易对符号
            timeframe: 时间框架
            limit: 返回记录数限制

        Returns:
            K 线数据 DataFrame
        """
        table_name = TABLES['klines_intraday'] if timeframe == '3m' else TABLES['klines_long_term']

        with sqlite3.connect(self.db_path) as conn:
            query = f"""
                SELECT timestamp, open, high, low, close, volume, close_time
                FROM {table_name}
                WHERE symbol = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """
            df = pd.read_sql_query(query, conn, params=(symbol, limit))
            return df

    def get_latest_data(self, symbol: str) -> Optional[Dict]:
        """
        获取指定交易对的最新数据

        Args:
            symbol: 交易对符号

        Returns:
            最新数据字典
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 获取最新 K 线数据
            cursor.execute(f"""
                SELECT * FROM {TABLES['klines_intraday']}
                WHERE symbol = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (symbol,))

            kline_row = cursor.fetchone()
            if not kline_row:
                return None

            # 获取最新技术指标
            cursor.execute(f"""
                SELECT * FROM {TABLES['indicators']}
                WHERE symbol = ? AND timeframe = '3m'
                ORDER BY timestamp DESC
                LIMIT 1
            """, (symbol,))

            indicator_row = cursor.fetchone()

            # 获取最新永续合约数据
            cursor.execute(f"""
                SELECT * FROM {TABLES['perp_data']}
                WHERE symbol = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (symbol,))

            perp_row = cursor.fetchone()

            # 构建返回数据
            result = {
                'symbol': symbol,
                'timestamp': datetime.fromtimestamp(kline_row[2] / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                'current_price': kline_row[5],
                'intraday': {
                    'prices': [],  # 需要从历史数据构建
                    'ema20': [],  # 需要从历史数据构建
                    'macd': [],  # 需要从历史数据构建
                    'rsi_7': [],  # 需要从历史数据构建
                    'rsi_14': []  # 需要从历史数据构建
                },
                'long_term': {
                    'ema_20': indicator_row[4] if indicator_row else None,
                    'ema_50': indicator_row[5] if indicator_row else None,
                    'atr_3': indicator_row[11] if indicator_row else None,
                    'atr_14': indicator_row[12] if indicator_row else None,
                    'volume_current': indicator_row[13] if indicator_row else None,
                    'volume_average': indicator_row[14] if indicator_row else None,
                    'macd': indicator_row[7] if indicator_row else None,
                    'rsi_14': indicator_row[10] if indicator_row else None
                },
                'perp_data': {
                    'open_interest_latest': perp_row[3] if perp_row else None,
                    'open_interest_average': perp_row[4] if perp_row else None,
                    'funding_rate': perp_row[5] if perp_row else None
                }
            }

            return result

    def close(self):
        """关闭数据库连接"""
        logger.info("数据库连接已关闭")
