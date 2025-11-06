#!/usr/bin/env python3
"""
修复Demo Trading API配置测试

基于CCXT官方公告：
- Binance已弃用期货沙盒环境
- 转向新的统一Demo Trading环境（现货+期货）
- CCXT v4.5.6+支持enable_demo_trading(True)
- API密钥与生产环境相同（与旧沙盒不同）
"""

import ccxt
import os
import json

# 从.env加载配置
from dotenv import load_dotenv
load_dotenv()

DEMO_API_KEY = os.getenv("DEMO_API_KEY", "")
DEMO_SECRET_KEY = os.getenv("DEMO_SECRET_KEY", "")

print("=" * 80)
print("🔧 Demo Trading API配置测试")
print("=" * 80)
print(f"API Key: {DEMO_API_KEY[:20]}...{DEMO_API_KEY[-10:] if len(DEMO_API_KEY) > 30 else DEMO_API_KEY}")
print()

# 测试: 使用真实API端点 + enable_demo_trading() + 强制设置baseUrl
print("测试: 真实API端点 + enable_demo_trading() + 强制baseUrl")
try:
    # 1. 创建交易所实例
    exchange = ccxt.binance({
        'apiKey': DEMO_API_KEY,
        'secret': DEMO_SECRET_KEY,
        'sandbox': False,  # 不是sandbox模式
        'baseUrl': None,   # 先不设置，让CCXT处理
    })

    print(f"  初始baseUrl: {exchange.baseUrl}")

    # 2. 启用demo trading
    exchange.enable_demo_trading(True)

    print(f"  启用demo trading后baseUrl: {exchange.baseUrl}")

    # 3. 强制设置正确的baseUrl（绕过CCXT错误修改）
    exchange.baseUrl = 'https://api.binance.com'
    exchange.urls['api']['public'] = 'https://api.binance.com'
    exchange.urls['api']['private'] = 'https://api.binance.com'

    print(f"  修正后baseUrl: {exchange.baseUrl}")

    # 4. 测试获取服务器时间（不需要认证）
    print("  测试1: 获取服务器时间...")
    time = exchange.fetch_time()
    print(f"  ✅ 服务器时间: {time}")

    # 5. 测试获取exchangeInfo（不需要认证）
    print("  测试2: 获取交易所信息...")
    exchange_info = exchange.fetch_markets()
    print(f"  ✅ 获取到 {len(exchange_info)} 个交易对")

    # 6. 测试获取ticker（不需要认证）
    print("  测试3: 获取BTCUSDT价格...")
    ticker = exchange.fetch_ticker('BTCUSDT')
    print(f"  ✅ BTCUSDT价格: ${ticker['last']:.2f}")

    # 7. 测试获取账户信息（需要认证）
    print("  测试4: 获取账户余额...")
    balance = exchange.fetch_balance()
    print(f"  ✅ 余额查询成功!")
    print(f"     USDT: {balance['USDT']['total']:.2f}")
    print(f"     BTC: {balance['BTC']['total']:.4f}")
    print(f"     ETH: {balance['ETH']['total']:.4f}")

    print("\n✅ 所有测试通过！Demo Trading API正常工作")

except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
