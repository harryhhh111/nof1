#!/usr/bin/env python3
"""
调试 Binance API 签名生成问题
"""

import hmac
import hashlib
import time
import json
import requests
from urllib.parse import urlencode

# 配置
api_key = "TcBcakgq6HrJ25zVvzVhv3RqTOMFXpwLrBpDDYr0wZINUxp5oamXxKoU67GhvcEV"
secret_key = "GFAFeViRZPemZ1CdqJKhK8wMQxLKqfonlAZ178lHZVit3wFulAX5syIWpVznG1Fp"
base_url = "https://testnet.binance.vision"

def get_server_time():
    """获取服务器时间"""
    url = f"{base_url}/api/v3/time"
    response = requests.get(url)
    data = response.json()
    return data['serverTime']

def create_signature(query_string, secret_key):
    """创建 HMAC SHA256 签名"""
    return hmac.new(
        secret_key.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

def test_account_info():
    """测试账户信息"""
    # 获取服务器时间
    server_time = get_server_time()
    print(f"服务器时间: {server_time}")

    # 生成查询字符串
    query_params = {
        "timestamp": server_time,
        "recvWindow": 10000  # 10秒窗口
    }
    query_string = urlencode(query_params)
    print(f"查询字符串: {query_string}")

    # 生成签名
    signature = create_signature(query_string, secret_key)
    print(f"签名: {signature}")

    # 构建 URL
    url = f"{base_url}/api/v3/account"
    headers = {
        "X-MBX-APIKEY": api_key,
        "Content-Type": "application/json"
    }

    # 发送请求
    print(f"\n发送请求到: {url}")
    print(f"Headers: {headers}")

    try:
        # 手动构建带签名的 URL
        full_url = f"{url}?{query_string}&signature={signature}"
        print(f"完整 URL: {full_url}")

        response = requests.get(full_url, headers=headers)
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")

        if response.status_code == 200:
            data = response.json()
            print("\n✅ 成功！账户信息:")
            balances = data.get('balances', [])
            for balance in balances[:10]:  # 只显示前10个
                asset = balance['asset']
                free = float(balance['free'])
                locked = float(balance['locked'])
                if free > 0 or locked > 0:
                    print(f"  {asset}: free={free}, locked={locked}")
        else:
            print(f"\n❌ 错误: {response.status_code}")

    except Exception as e:
        print(f"\n❌ 请求失败: {e}")
        import traceback
        traceback.print_exc()

def test_price():
    """测试价格查询（无需认证）"""
    print("\n" + "=" * 80)
    print("测试价格查询（无需认证）")
    print("=" * 80)

    url = f"{base_url}/api/v3/ticker/price"
    params = {"symbol": "BTCUSDT"}

    try:
        response = requests.get(url, params=params)
        print(f"响应: {response.text}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ BTC 价格: {data['price']}")
        else:
            print(f"❌ 错误: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")

if __name__ == "__main__":
    print("=" * 80)
    print(" Binance API 调试工具")
    print("=" * 80)

    # 测试价格查询
    test_price()

    # 测试账户信息
    print("\n" + "=" * 80)
    print("测试账户信息（需要认证）")
    print("=" * 80)

    test_account_info()
