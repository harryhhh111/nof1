#!/usr/bin/env python3
"""
Nof1 数据获取系统演示脚本

演示系统的主要功能和使用方法。
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database

print("=" * 70)
print(" Nof1 数据获取系统 - 功能演示")
print("=" * 70)

print("\n📊 系统概述")
print("-" * 70)
print("""
本系统是一个基于 Python 的加密货币市场数据获取和分析系统。
它能够从 Binance 交易所获取实时市场数据，计算技术指标，并将
数据存储到 SQLite 数据库中进行持久化。

主要功能：
  ✓ 多交易所数据获取（目前支持 Binance via CCXT）
  ✓ 实时市场数据获取（OHLCV K 线数据）
  ✓ 技术指标计算（EMA, MACD, RSI, ATR）
  ✓ 永续合约数据（资金费率、开放利息）
  ✓ 数据持久化存储（SQLite）
  ✓ 定时数据更新调度器
""")

print("\n🏗️ 系统架构")
print("-" * 70)
print("""
系统采用模块化架构：

┌─────────────────┐
│   main.py       │  ← CLI 入口，命令行接口
└────────┬────────┘
         │
    ┌────┴────┬─────────────┐
    ▼         ▼             ▼
┌─────────┐ ┌──────────┐ ┌──────────┐
│data_    │ │indicators│ │scheduler │
│fetcher  │ │    计算  │ │ 调度器   │
└─────────┘ └──────────┘ └──────────┘
    │           │           │
    └────┬──────┴────┬──────┘
         ▼           ▼
    ┌──────────────────┐
    │  database.py     │  ← SQLite 数据库
    └──────────────────┘
""")

print("\n💻 使用方法")
print("-" * 70)
print("""
# 1. 安装依赖
pip install -r requirements.txt

# 2. 获取单个交易对数据
python main.py --symbol BTCUSDT

# 3. 获取多个交易对数据
python main.py --symbols BTCUSDT ETHUSDT SOLUSDT

# 4. 启动定时调度器（每 3 分钟更新一次）
python main.py --schedule

# 5. 启动调度器并指定交易对和间隔
python main.py --schedule --symbols BTCUSDT ETHUSDT --interval 60

# 6. 查询数据库中的最新数据
python main.py --query --symbols BTCUSDT

# 7. 显示系统状态
python main.py --status

# 8. 以可读格式输出
python main.py --symbol BTCUSDT --output print
""")

print("\n📈 数据结构")
print("-" * 70)
print("""
系统输出的 JSON 数据格式符合 Nof1 Alpha Arena 标准：

{
    "symbol": "BTCUSDT",              # 交易对符号
    "timestamp": "2025-11-02 10:30:00",  # 时间戳
    "current_price": 67500.50,        # 当前价格

    "intraday": {                     # 日内数据（3分钟）
        "prices": [...],              # 最近10个价格点
        "ema20": [...],               # EMA20 指标序列
        "macd": [...],                # MACD 指标序列
        "rsi_7": [...],               # RSI7 指标序列
        "rsi_14": [...]               # RSI14 指标序列
    },

    "long_term": {                    # 长期数据（4小时）
        "ema_20": 67200.50,           # EMA20 最新值
        "ema_50": 66800.25,           # EMA50 最新值
        "atr_3": 150.75,              # ATR3 最新值
        "atr_14": 285.50,             # ATR14 最新值
        "volume_current": 1250.30,    # 当前交易量
        "volume_average": 1180.45,    # 平均交易量
        "macd": [...],                # MACD 序列
        "rsi_14": [...]               # RSI14 序列
    },

    "perp_data": {                    # 永续合约数据
        "open_interest_latest": 50000.0,    # 最新开放利息
        "open_interest_average": 48500.0,   # 平均开放利息
        "funding_rate": 0.00015             # 资金费率
    }
}
""")

print("\n🔧 配置参数 (config.py)")
print("-" * 70)
print("""
# 更新间隔（秒）
UPDATE_INTERVAL = 180  # 3分钟

# 监控的交易对
SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'DOGEUSDT', 'XRPUSDT']

# 技术指标参数
INDICATOR_PARAMS = {
    'ema_short': 20,    # EMA 短周期
    'ema_long': 50,     # EMA 长周期
    'rsi_short': 7,     # RSI 短周期
    'rsi_long': 14,     # RSI 长周期
    'atr_short': 3,     # ATR 短周期
    'atr_long': 14      # ATR 长周期
}
""")

print("\n📊 技术指标说明")
print("-" * 70)
print("""
EMA (指数移动平均线)
  - 20期 EMA: 用于短期趋势分析
  - 50期 EMA: 用于长期趋势分析
  - 当价格上穿 EMA 时，可能表示上涨趋势
  - 当价格下穿 EMA 时，可能表示下跌趋势

MACD (移动平均收敛散度)
  - MACD 线: 快速EMA(12) - 慢速EMA(26)
  - Signal 线: MACD 线的 9期 EMA
  - Histogram: MACD 线 - Signal 线
  - 金叉：MACD 上穿 Signal，可能买入信号
  - 死叉：MACD 下穿 Signal，可能卖出信号

RSI (相对强弱指数)
  - RSI7: 短期相对强弱，波动更敏感
  - RSI14: 长期相对强弱，更稳定
  - RSI > 70: 可能超买，价格可能下跌
  - RSI < 30: 可能超卖，价格可能上涨

ATR (平均真实波幅)
  - ATR3: 短期波动率，反映近期价格波动
  - ATR14: 长期波动率，反映整体市场波动
  - ATR 值越大，市场波动越剧烈
  - 用于设置止损和止盈点位

交易量分析
  - 当前交易量 vs 平均交易量
  - 交易量放大通常伴随价格突破
  - 交易量萎缩可能表示趋势减弱
""")

print("\n📁 项目文件结构")
print("-" * 70)
print("""
nof1/
├── README.md              # 项目文档
├── CLAUDE.md              # Claude AI 指导文件
├── requirements.txt       # 依赖包列表
├── config.py              # 配置文件
├── main.py               # 主程序入口
├── data_fetcher.py       # 数据获取模块
├── indicators.py         # 技术指标计算
├── database.py           # 数据库操作
├── scheduler.py          # 定时调度器
├── test_basic.py         # 基础功能测试
├── run_tests.py          # 测试运行脚本
└── tests/                # 测试目录
    ├── __init__.py
    ├── test_config.py
    ├── test_indicators.py
    ├── test_database.py
    ├── test_data_fetcher.py
    ├── test_scheduler.py
    └── test_integration.py
""")

print("\n🚀 下一步操作")
print("-" * 70)
print("""
1. 安装依赖：
   pip install -r requirements.txt

2. 运行基础测试：
   python3 test_basic.py

3. 获取实时数据：
   python3 main.py --symbol BTCUSDT

4. 启动持续数据获取：
   python3 main.py --schedule

5. 查看系统状态：
   python3 main.py --status

更多使用方法请参考 README.md 文件。
""")

print("\n" + "=" * 70)
print(" 感谢使用 Nof1 数据获取系统！")
print("=" * 70)
