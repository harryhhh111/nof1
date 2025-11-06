#!/usr/bin/env python3
"""
完整的Demo Trading测试

验证：
1. CCXT enable_demo_trading()工作正常
2. demo-api.binance.com可以访问
3. API密钥认证成功
4. 获取数据正常
"""

import sys
import os

# 添加项目根目录
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ccxt
from dotenv import load_dotenv
import config

load_dotenv()

print("=" * 80)
print("🎯 Demo Trading 完整测试")
print("=" * 80)
print()

# 1. 检查配置
print("1️⃣ 检查配置:")
print(f"   CURRENT_MODE: {config.CURRENT_MODE}")
print(f"   TRADING_MODE_NAME: {config.TRADING_MODE_NAME}")
print(f"   BINANCE_BASE_URL: {config.BINANCE_BASE_URL}")
print(f"   BINANCE_API_KEY: {config.BINANCE_API_KEY[:20]}...")
print()

# 2. 创建交易所实例
print("2️⃣ 创建交易所实例:")
try:
    exchange = ccxt.binance({
        'apiKey': config.BINANCE_API_KEY,
        'secret': config.BINANCE_SECRET_KEY,
        'sandbox': False,  # 关键：不能使用sandbox！
        'enableRateLimit': True,
    })
    print("   ✅ 交易所实例创建成功")
except Exception as e:
    print(f"   ❌ 创建失败: {e}")
    sys.exit(1)

# 3. 启用Demo Trading
print("\n3️⃣ 启用Demo Trading:")
try:
    exchange.enable_demo_trading(True)
    print("   ✅ Demo Trading已启用")

    # 检查URL变化
    if 'demo' in exchange.urls:
        print("   ✅ Demo URLs已加载:")
        for key in ['public', 'private']:
            if key in exchange.urls['demo']:
                print(f"      {key}: {exchange.urls['demo'][key]}")
except Exception as e:
    print(f"   ❌ 启用失败: {e}")
    sys.exit(1)

# 4. 测试获取服务器时间
print("\n4️⃣ 测试1: 获取服务器时间")
try:
    time = exchange.fetch_time()
    print(f"   ✅ 成功! 服务器时间: {time}")
except Exception as e:
    print(f"   ❌ 失败: {e}")

# 5. 测试获取市场数据
print("\n5️⃣ 测试2: 获取BTCUSDT价格")
try:
    ticker = exchange.fetch_ticker('BTCUSDT')
    print(f"   ✅ 成功!")
    print(f"      当前价格: ${ticker['last']:.2f}")
    print(f"      24h变化: {ticker['change']:.2f}%")
except Exception as e:
    print(f"   ❌ 失败: {e}")

# 6. 测试获取K线数据
print("\n6️⃣ 测试3: 获取K线数据")
try:
    ohlcv = exchange.fetch_ohlcv('BTCUSDT', '3m', limit=5)
    print(f"   ✅ 成功获取 {len(ohlcv)} 条K线")
    print(f"      最新: {ohlcv[-1]}")
except Exception as e:
    print(f"   ❌ 失败: {e}")

# 7. 测试获取账户余额（需要认证）
print("\n7️⃣ 测试4: 获取账户余额")
try:
    balance = exchange.fetch_balance()
    print(f"   ✅ 余额查询成功!")
    print(f"      USDT: {balance['USDT']['total']:.2f}")
    print(f"      BTC: {balance['BTC']['total']:.4f}")
    print(f"      ETH: {balance['ETH']['total']:.4f}")
except Exception as e:
    print(f"   ❌ 失败: {e}")
    print(f"      (如果是用USDT购买的API Key，这是正常的)")

# 8. 测试获取交易对列表
print("\n8️⃣ 测试5: 获取交易对列表")
try:
    markets = exchange.fetch_markets()
    print(f"   ✅ 成功获取 {len(markets)} 个交易对")
    print(f"      示例: {markets[0]['symbol']}")
except Exception as e:
    print(f"   ❌ 失败: {e}")

print()
print("=" * 80)
print("🎉 测试完成！")
print("=" * 80)
print()
print("💡 说明:")
print("   - 如果所有测试都成功，说明Demo Trading配置正确")
print("   - 如果余额查询失败，可能是API Key权限不足（只要Reading权限即可）")
print("   - Demo Trading使用虚拟资金 (5000 USDT等)")
