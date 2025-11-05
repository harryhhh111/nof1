#!/bin/bash
# Binance Demo Trading API Debug Curl Commands
# 在 Postman 中使用这些请求进行调试

echo "=========================================="
echo " Binance Demo Trading API Debug"
echo "=========================================="
echo ""
echo "请在 Postman 中设置以下变量:"
echo "  - baseUrl: https://demo.binance.vision"
echo "  - apiKey: 你的 DEMO_API_KEY"
echo "  - secretKey: 你的 DEMO_SECRET_KEY"
echo ""

# 1. 测试服务器时间
echo "=========================================="
echo "1. 测试服务器时间 (GET /api/v3/time)"
echo "=========================================="
echo "curl -X GET \"https://demo.binance.vision/api/v3/time\""
echo ""

# 2. 获取交易规则和交易对信息
echo "=========================================="
echo "2. 获取交易规则 (GET /api/v3/exchangeInfo)"
echo "=========================================="
echo "curl -X GET \"https://demo.binance.vision/api/v3/exchangeInfo?symbol=BTCUSDT\""
echo ""

# 3. 获取 ticker 价格 (不需要认证)
echo "=========================================="
echo "3. 获取 BTCUSDT 价格 (GET /api/v3/ticker/price)"
echo "=========================================="
echo "curl -X GET \"https://demo.binance.vision/api/v3/ticker/price?symbol=BTCUSDT\""
echo ""

# 4. 测试服务器状态
echo "=========================================="
echo "4. 测试服务器状态 (GET /api/v3/ping)"
echo "=========================================="
echo "curl -X GET \"https://demo.binance.vision/api/v3/ping\""
echo ""

# 5. 获取账户信息 (需要 HMAC 签名认证)
echo "=========================================="
echo "5. 获取账户信息 (需要 HMAC 签名)"
echo "=========================================="
echo "Method: GET"
echo "URL: https://demo.binance.vision/api/v3/account"
echo ""
echo "Headers:"
echo "  X-MBX-APIKEY: {{apiKey}}"
echo ""
echo "Query Parameters:"
echo "  timestamp: (当前时间戳)"
echo "  signature: (使用 secretKey 对 query string 进行 HMAC SHA256 签名)"
echo ""
echo "示例签名生成 (Python):"
cat << 'EOF'
import hmac
import hashlib
import time

api_key = "YOUR_API_KEY"
secret_key = "YOUR_SECRET_KEY"
timestamp = int(time.time() * 1000)
query_string = f"timestamp={timestamp}"
signature = hmac.new(
    secret_key.encode('utf-8'),
    query_string.encode('utf-8'),
    hashlib.sha256
).hexdigest()

print(f"Query String: {query_string}")
print(f"Signature: {signature}")
EOF
echo ""

# 6. 获取账户余额 (需要认证)
echo "=========================================="
echo "6. 获取账户余额 (需要 HMAC 签名)"
echo "=========================================="
echo "Method: GET"
echo "URL: https://demo.binance.vision/api/v3/account"
echo ""
echo "Headers:"
echo "  X-MBX-APIKEY: {{apiKey}}"
echo ""
echo "Query Parameters:"
echo "  timestamp: 1733472000000"
echo "  signature: (签名)"
echo ""

# 7. 完整请求示例
echo "=========================================="
echo "7. Postman 完整配置示例"
echo "=========================================="
echo ""
echo "创建新的 API Request:"
echo "  Name: Binance Demo - Get Account"
echo "  Method: GET"
echo "  URL: https://demo.binance.vision/api/v3/account"
echo ""
echo "Headers:"
echo "  Key: X-MBX-APIKEY"
echo "  Value: {{apiKey}}"
echo ""
echo "Params (Query):"
echo "  Key: timestamp"
echo "  Value: 1733472000000"
echo ""
echo "Params (Query):"
echo "  Key: signature"
echo "  Value: (运行上面的 Python 脚本生成)"
echo ""
echo "Pre-request Script (Postman):"
cat << 'EOF'
// 生成时间戳和签名
const apiKey = pm.environment.get("apiKey");
const secretKey = pm.environment.get("secretKey");
const timestamp = Date.now();
pm.request.url.query.add({key: "timestamp", value: timestamp.toString()});

// 生成签名
const queryString = pm.request.url.query.toString();
const signature = CryptoJS.HmacSHA256(queryString, secretKey).toString(CryptoJS.enc.Hex);
pm.request.url.query.add({key: "signature", value: signature});
EOF
echo ""

# 8. 快速测试所有交易对价格
echo "=========================================="
echo "8. 获取所有交易对价格 (GET /api/v3/ticker/price)"
echo "=========================================="
echo "curl -X GET \"https://demo.binance.vision/api/v3/ticker/price\""
echo ""

# 9. 获取 24hr 价格变动统计
echo "=========================================="
echo "9. 获取 24hr 统计 (GET /api/v3/ticker/24hr)"
echo "=========================================="
echo "curl -X GET \"https://demo.binance.vision/api/v3/ticker/24hr?symbol=BTCUSDT\""
echo ""

# 10. 测试订单 (如果权限足够)
echo "=========================================="
echo "10. 下单测试 (POST /api/v3/order/test)"
echo "=========================================="
echo "Method: POST"
echo "URL: https://demo.binance.vision/api/v3/order/test"
echo ""
echo "Headers:"
echo "  X-MBX-APIKEY: {{apiKey}}"
echo "  Content-Type: application/x-www-form-urlencoded"
echo ""
echo "Body (form-data):"
echo "  symbol: BTCUSDT"
echo "  side: BUY"
echo "  type: MARKET"
echo "  quantity: 0.001"
echo "  timestamp: 1733472000000"
echo "  signature: (签名)"
echo ""

echo "=========================================="
echo " Postman 环境变量设置"
echo "=========================================="
echo ""
echo "在 Postman 中创建环境 'Binance Demo Trading':"
echo ""
echo "Variables:"
echo "  - baseUrl: https://demo.binance.vision"
echo "  - apiKey: (你的 DEMO_API_KEY)"
echo "  - secretKey: (你的 DEMO_SECRET_KEY)"
echo ""

echo "=========================================="
echo " 常见错误排查"
echo "=========================================="
echo ""
echo "1. 错误 -2015 (Invalid API-key, IP, or permissions):"
echo "   • 检查 API Key 是否正确"
echo "   • 检查 IP 是否被限制"
echo "   • 检查权限是否开启"
echo ""
echo "2. 错误 -1021 (Timestamp out of allowed range):"
echo "   • 服务器时间偏差超过 5 秒"
echo "   • 检查本地时间"
echo "   • 重新生成时间戳"
echo ""
echo "3. 错误 -1022 (Signature for this request is not valid):"
echo "   • 签名生成错误"
echo "   • 检查 secretKey 是否正确"
echo "   • 检查 query string 是否正确"
echo ""
echo "4. 无响应:"
echo "   • 检查网络连接"
echo "   • 检查 baseUrl 是否正确"
echo "   • 检查防火墙设置"
echo ""

echo "=========================================="
echo " 测试完成"
echo "=========================================="
