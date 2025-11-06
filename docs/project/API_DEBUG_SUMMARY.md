# API Key 问题调试总结

## 📋 当前状态

✅ **API 可访问**: https://testnet.binance.vision 可以正常访问
✅ **价格查询成功**: 无需认证的 API（如 `/api/v3/ticker/price`）工作正常
❌ **账户查询失败**: 需要认证的 API 返回 -2015 错误

## 🚨 错误分析

### 错误代码: -2015
```
Invalid API-key, IP, or permissions for action.
```

**可能原因**:
1. API Key 不正确或已过期
2. IP 地址被限制
3. 权限未开启或不够

## 🔧 解决方案

### 方案1: 检查 API Key 来源

**问题**: 您可能在错误的地方获取了 API Key

**正确的获取位置**:
- ✅ **正确**: https://testnet.binance.vision/ （这是获取 Testnet API Key 的地方）
- ❌ **错误**: https://demo.binance.com/ （这是 Demo Trading 的 Web 界面，不是 API Key 来源）

### 方案2: 重新获取 API Key

1. 访问: https://testnet.binance.vision/
2. 点击 "Login"（需要 GitHub 账号）
3. 创建新的 API Key
4. 复制 API Key 和 Secret Key

### 方案3: 检查 IP 限制

在 API Key 管理页面，检查是否有 IP 限制：
- 如果设置了 IP 限制，确保当前 IP 在允许列表中
- 建议暂时移除 IP 限制进行测试

### 方案4: 检查权限设置

确保 API Key 开启了以下权限：
- ✅ **Enable Reading** (必需)
- ✅ **Enable Spot Trading** (可选，用于交易)

## 📊 测试结果

### ✅ 成功测试
```bash
# 获取服务器时间
curl https://testnet.binance.vision/api/v3/time
# 返回: {"serverTime": 1762360950071}

# 获取 BTC 价格
curl "https://testnet.binance.vision/api/v3/ticker/price?symbol=BTCUSDT"
# 返回: {"symbol":"BTCUSDT","price":"103574.71000000"}
```

### ❌ 失败测试
```bash
# 获取账户信息
curl -X GET "https://testnet.binance.vision/api/v3/account" \
  -H "X-MBX-APIKEY: YOUR_API_KEY"
# 返回: {"code":-2015,"msg":"Invalid API-key, IP, or permissions for action."}
```

## 🎯 立即行动

### 步骤1: 验证 API Key 来源
```
访问: https://testnet.binance.vision/
检查: 是否是从这里获取的 API Key

如果您是从 https://demo.binance.com/ 获取的，那是 Web 界面的 API Key，
不是用于 API 访问的！
```

### 步骤2: 重新创建 API Key
```
1. 访问 https://testnet.binance.vision/
2. 登录（使用 GitHub 账号）
3. 创建新 API Key
4. 确保开启 "Enable Reading" 权限
5. 复制 API Key 和 Secret Key
```

### 步骤3: 测试新 API Key
```bash
# 使用新的 API Key 测试
python3 debug_signature.py
```

## 💡 关键发现

**重要**: Demo Trading 的 Web 界面是 https://demo.binance.com/，
但 API 端点仍然是 https://testnet.binance.vision/

所以:
- **Web 界面**: https://demo.binance.com/
- **API 端点**: https://testnet.binance.vision/
- **API Key 来源**: https://testnet.binance.vision/

## 📞 需要帮助

如果您需要我帮您验证新的 API Key，请提供：
1. API Key 的前 10 位字符（不要提供完整的 secret key）
2. 新的测试结果

## 🔄 后续步骤

1. ✅ 确认 API Key 来源正确
2. ✅ 重新创建 API Key
3. ✅ 开启正确权限
4. ✅ 测试新 API Key
5. ✅ 更新系统中配置文件
6. ✅ 重新运行交易系统
