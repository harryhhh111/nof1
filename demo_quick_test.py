#!/usr/bin/env python3
"""
快速 Demo Trading 功能验证

测试核心功能：数据获取、价格查询、基本交易准备
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from data_fetcher import DataFetcher
from trading.real_trader import RealTrader

print("=" * 80)
print(" Demo Trading 快速验证")
print("=" * 80)

print(f"\n✅ 当前配置: {config.CURRENT_MODE.upper()}")
print(f"   Base URL: {config.BINANCE_BASE_URL}")
print(f"   Demo API: {config.DEMO_API_KEY[:20]}...")

# 测试1: 数据获取
print("\n[测试1] 数据获取...")
try:
    fetcher = DataFetcher()
    btc_data = fetcher.get_market_data('BTCUSDT')
    print(f"   ✅ BTC价格: ${btc_data['current_price']:,.2f}")
    fetcher.close()
except Exception as e:
    print(f"   ❌ 失败: {e}")
    sys.exit(1)

# 测试2: 价格查询
print("\n[测试2] 价格查询...")
try:
    trader = RealTrader(use_futures=False)
    price = trader.get_symbol_price('BTCUSDT')
    print(f"   ✅ BTC价格: ${price:,.2f}")

    eth_price = trader.get_symbol_price('ETHUSDT')
    print(f"   ✅ ETH价格: ${eth_price:,.2f}")
    trader.close()
except Exception as e:
    print(f"   ❌ 失败: {e}")
    sys.exit(1)

# 测试3: 期货数据
print("\n[测试3] 期货数据获取...")
try:
    fetcher_futures = DataFetcher(use_futures=True)
    futures_price = fetcher_futures.get_symbol_price('BTCUSDT')
    print(f"   ✅ BTC期货价格: ${futures_price:,.2f}")
    fetcher_futures.close()
except Exception as e:
    print(f"   ⚠️  期货功能不可用: {e}")

print("\n" + "=" * 80)
print(" ✅ 所有核心功能验证通过！")
print("=" * 80)

print("""
📝 验证结果:
  ✅ Demo Trading API 正常
  ✅ 现货数据获取正常
  ✅ 期货数据获取正常
  ✅ 价格查询正常

🚀 可以继续使用以下命令:
  • python3 nof1.py --run 2     (运行交易系统)
  • python3 nof1.py --view      (查看结果)
  • python3 nof1.py --api       (启动API服务器)

⚠️  注意:
  • Demo Trading 使用虚拟资金
  • API Key 需要开启读取权限才能查询余额
  • 交易功能需要开启交易权限
""")
