"""
Nof1 数据获取系统配置文件

系统配置参数，包括数据库路径、更新间隔、交易品种等设置。
"""

import os
from typing import Dict, List

# 加载.env文件（如果存在）
try:
    from dotenv import load_dotenv
    # 尝试从项目根目录和上级目录加载.env
    if os.path.exists('.env'):
        load_dotenv('.env')
        print("✅ 已加载.env配置文件")
    elif os.path.exists('/home/claude_user/nof1/.env'):
        load_dotenv('/home/claude_user/nof1/.env')
        print("✅ 已加载.env配置文件")
except ImportError:
    print("⚠️  python-dotenv未安装，使用系统环境变量")
    # 用户可以使用: pip install python-dotenv
except Exception as e:
    print(f"⚠️  加载.env文件失败: {e}")

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

# ===== Binance Demo Trading / Testnet 配置 =====
# 设置为 True 使用 Testnet，False 使用真实交易所
USE_TESTNET = os.getenv("USE_TESTNET", "true").lower() == "true"

# Demo Trading API Key（新系统）
DEMO_API_KEY = os.getenv("DEMO_API_KEY", "")
DEMO_SECRET_KEY = os.getenv("DEMO_SECRET_KEY", "")

# Testnet API Key（旧系统，从 testnet.binance.vision 获取）
TESTNET_API_KEY = os.getenv("TESTNET_API_KEY", "")
TESTNET_SECRET_KEY = os.getenv("TESTNET_SECRET_KEY", "")

# 根据模式选择配置
if USE_TESTNET:
    # 优先使用新的 Demo Trading API
    if DEMO_API_KEY and DEMO_SECRET_KEY:
        BINANCE_API_KEY = DEMO_API_KEY
        BINANCE_SECRET_KEY = DEMO_SECRET_KEY
        # 注意: 新 Demo Trading (demo.binance.com) 可能没有公开 API
        # 当前使用 testnet.binance.vision 作为备用方案
        BINANCE_BASE_URL = "https://testnet.binance.vision"
        BINANCE_FUTURES_URL = "https://testnet.binancefuture.com"
        TRADING_MODE_NAME = "Demo Trading (New)"
        print(f"⚠️  注意: demo.binance.com 可能没有公开 API")
        print(f"   当前使用 testnet.binance.vision 作为备用")
    elif TESTNET_API_KEY and TESTNET_SECRET_KEY:
        BINANCE_API_KEY = TESTNET_API_KEY
        BINANCE_SECRET_KEY = TESTNET_SECRET_KEY
        BINANCE_BASE_URL = "https://testnet.binance.vision"
        BINANCE_FUTURES_URL = "https://testnet.binancefuture.com"
        TRADING_MODE_NAME = "Testnet (Legacy)"
        print(f"⚠️  使用旧的 Testnet API（建议升级到 Demo Trading）")
    else:
        BINANCE_API_KEY = BINANCE_API_KEY
        BINANCE_SECRET_KEY = BINANCE_SECRET_KEY
        BINANCE_BASE_URL = "https://testnet.binance.vision"
        BINANCE_FUTURES_URL = "https://testnet.binancefuture.com"
        TRADING_MODE_NAME = "Testnet (Default)"
        print(f"⚠️  未配置 API Key，使用默认 Testnet")
else:
    BINANCE_BASE_URL = "https://api.binance.com"
    BINANCE_FUTURES_URL = "https://fapi.binance.com"
    TRADING_MODE_NAME = "Live Trading"
    print(f"⚠️  LIVE TRADING - 使用真实资金！")

# 交易所配置
EXCHANGE_CONFIG = {
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_SECRET_KEY,
    'sandbox': USE_TESTNET,  # 关键：启用/禁用沙盒模式
    'enableRateLimit': True,
    'baseUrl': BINANCE_BASE_URL if USE_TESTNET else None,
    'options': {
        'defaultType': 'spot',  # 默认现货交易
    }
}

# 期货交易配置
FUTURES_CONFIG = {
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_SECRET_KEY,
    'sandbox': USE_TESTNET,
    'enableRateLimit': True,
    'baseUrl': BINANCE_FUTURES_URL if USE_TESTNET else None,
    'options': {
        'defaultType': 'future',  # 默认期货交易
    }
}

# 交易模式
TRADING_MODE = {
    'PAPER': 'paper',       # 纸交易
    'TESTNET': 'testnet',   # Testnet模拟交易（Legacy）
    'DEMO': 'demo',         # Demo Trading（新系统）
    'LIVE': 'live'          # 实盘交易（高风险！）
}

# 当前交易模式（根据USE_TESTNET和API Key自动选择）
if USE_TESTNET:
    if DEMO_API_KEY and DEMO_SECRET_KEY:
        CURRENT_MODE = TRADING_MODE['DEMO']
    else:
        CURRENT_MODE = TRADING_MODE['TESTNET']
else:
    CURRENT_MODE = TRADING_MODE['PAPER']

print(f"""
═══════════════════════════════════════════════════════
  Trading Mode: {CURRENT_MODE.upper()}
  {'=' * 53}
  {'⚠️  WARNING: This is DEMO TRADING - Virtual money only!' if CURRENT_MODE == 'demo' else ''}
  {'⚠️  WARNING: This is TESTNET - No real money!' if CURRENT_MODE == 'testnet' else ''}
  {'⚠️  WARNING: LIVE TRADING - Real money at risk!' if not USE_TESTNET else ''}
  {'=' * 53}
  Demo API Key: {'✅ Configured' if DEMO_API_KEY else '❌ NOT SET'}
  Testnet API Key: {'✅ Configured' if TESTNET_API_KEY else '❌ NOT SET'}
  {'=' * 53}
  Base URL: {BINANCE_BASE_URL}
  Futures URL: {BINANCE_FUTURES_URL}
═══════════════════════════════════════════════════════
""")

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
