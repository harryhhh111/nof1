#!/usr/bin/env python3
"""
生成 Binance API 签名
用于 Postman 测试
"""

import hmac
import hashlib
import time
import sys
import os

# 从环境变量或直接设置
try:
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("DEMO_API_KEY")
    secret_key = os.getenv("DEMO_SECRET_KEY")
except:
    api_key = None
    secret_key = None

if not api_key or not secret_key:
    print("❌ 错误: 请在 .env 文件中设置 DEMO_API_KEY 和 DEMO_SECRET_KEY")
    print("\n或直接编辑此文件，在第10-11行设置:")
    print("  api_key = 'your_api_key_here'")
    print("  secret_key = 'your_secret_key_here'")
    sys.exit(1)

# 生成时间戳
timestamp = int(time.time() * 1000)

# 生成查询字符串
query_string = f"timestamp={timestamp}"

# 生成签名
signature = hmac.new(
    secret_key.encode('utf-8'),
    query_string.encode('utf-8'),
    hashlib.sha256
).hexdigest()

print("=" * 80)
print(" Binance Demo Trading API 签名生成")
print("=" * 80)
print(f"\nAPI Key: {api_key[:20]}...")
print(f"时间戳: {timestamp}")
print(f"\n查询字符串: {query_string}")
print(f"签名: {signature}")
print("\n" + "=" * 80)
print(" Postman 配置:")
print("=" * 80)
print(f"""
Headers:
  X-MBX-APIKEY: {api_key}

Params:
  timestamp: {timestamp}
  signature: {signature}
""")
print("=" * 80)

# 完整 curl 命令
print("\n完整 curl 命令:")
print("=" * 80)
print(f"""curl -X GET \\
  "https://testnet.binance.vision/api/v3/account" \\
  -H "X-MBX-APIKEY: {api_key}" \\
  -H "Content-Type: application/json" \\
  -G \\
  -d "timestamp={timestamp}" \\
  -d "signature={signature}" """)
