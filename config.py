"""
Nof1 数据获取系统配置文件

系统配置参数，包括数据库路径、更新间隔、交易品种等设置。
"""

import os
from typing import Dict, List

# 数据更新间隔（秒）
UPDATE_INTERVAL = 180  # 3分钟

# 数据库配置
DATABASE_PATH = os.getenv("DATABASE_PATH", "market_data.db")

# 交易品种
SYMBOLS = [
    'BTCUSDT',
    'ETHUSDT',
    'SOLUSDT',
    'BNBUSDT',
    'DOGEUSDT',
    'XRPUSDT'
]

# 时间间隔
INTERVALS = {
    'intraday': '3m',
    'long_term': '4h'
}

# 技术指标参数
INDICATOR_PARAMS = {
    'ema_short': 20,
    'ema_long': 50,
    'rsi_short': 7,
    'rsi_long': 14,
    'atr_short': 3,
    'atr_long': 14
}

# 数据库表名
TABLES = {
    'klines_intraday': 'klines_3m',
    'klines_long_term': 'klines_4h',
    'indicators': 'technical_indicators',
    'perp_data': 'perpetual_data'
}

# Binance API 配置（可选，如果需要私有接口）
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY", "")

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
