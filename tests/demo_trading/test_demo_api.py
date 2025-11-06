#!/usr/bin/env python3
"""
测试Demo Trading API密钥
"""

import ccxt
import os

# 从.env加载配置
from dotenv import load_dotenv
load_dotenv()

DEMO_API_KEY = os.getenv("DEMO_API_KEY", "")
DEMO_SECRET_KEY = os.getenv("DEMO_SECRET_KEY", "")

print("=" * 80)
print("🔑 Demo Trading API密钥测试")
print("=" * 80)
print(f"API Key: {DEMO_API_KEY[:20]}...{DEMO_API_KEY[-10:] if len(DEMO_API_KEY) > 30 else DEMO_API_KEY}")
print(f"Secret: {DEMO_SECRET_KEY[:10]}...{DEMO_SECRET_KEY[-10:] if len(DEMO_SECRET_KEY) > 20 else DEMO_SECRET_KEY}")
print()

# 测试1: 使用真实API端点（不启用demo trading）
print("测试1: 真实API端点 + enable_demo_trading()")
try:
    exchange = ccxt.binance({
        'apiKey': DEMO_API_KEY,
        'secret': DEMO_SECRET_KEY,
        'sandbox': False,
        'baseUrl': 'https://api.binance.com',
    })
    exchange.enable_demo_trading(True)

    # 获取服务器时间（不需要认证）
    time = exchange.fetch_time()
    print(f"✅ 成功! 服务器时间: {time}")

    # 尝试获取账户信息（需要认证）
    balance = exchange.fetch_balance()
    print(f"✅ 账户信息获取成功!")
    print(f"   USDT余额: {balance['USDT']['total']}")
    print(f"   BTC余额: {balance['BTC']['total']}")

except Exception as e:
    print(f"❌ 失败: {e}")

print()

# 测试2: 使用testnet端点（对比）
print("测试2: Testnet端点（参考）")
try:
    exchange2 = ccxt.binance({
        'apiKey': DEMO_API_KEY,
        'secret': DEMO_SECRET_KEY,
        'sandbox': True,
        'baseUrl': 'https://testnet.binance.vision',
    })

    time2 = exchange2.fetch_time()
    print(f"✅ 服务器时间: {time2}")

    balance2 = exchange2.fetch_balance()
    print(f"❌ 意外成功: {balance2}")

except Exception as e:
    print(f"❌ 失败 (预期): {e}")

print()
print("=" * 80)
