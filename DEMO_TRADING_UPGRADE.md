# Binance Demo Trading 升级指南

## 📋 升级概述

本系统已从旧的 Binance Testnet (`testnet.binance.vision`) 升级到新的 **Binance Demo Trading** (`demo.binance.vision`)。

## ✨ 新功能特性

### 1. 双重API支持
- ✅ **新的 Demo Trading API** (推荐)
- ✅ **旧的 Testnet API** (向后兼容)
- 自动检测并优先使用新的 Demo Trading API

### 2. 期货和现货分离配置
- 独立的现货交易配置：`BINANCE_BASE_URL`
- 独立的期货交易配置：`BINANCE_FUTURES_URL`
- 支持期货和现货独立初始化

### 3. 增强的交易执行器
```python
# 现货交易
trader_spot = RealTrader(use_futures=False)

# 期货交易
trader_futures = RealTrader(use_futures=True)
```

### 4. 增强的数据获取器
```python
# 现货数据
fetcher_spot = DataFetcher(use_futures=False)

# 期货数据
fetcher_futures = DataFetcher(use_futures=True)
```

## 🔧 环境变量配置

### .env 文件配置
```bash
# 新的 Demo Trading API (推荐)
DEMO_API_KEY="your_demo_api_key"
DEMO_SECRET_KEY="your_demo_secret_key"

# 旧的 Testnet API (向后兼容)
TESTNET_API_KEY="your_testnet_api_key"
TESTNET_SECRET_KEY="your_testnet_secret_key"

# 模式选择
USE_TESTNET="true"
```

### API Key 优先级
1. 优先使用 `DEMO_API_KEY` + `DEMO_SECRET_KEY`
2. 回退到 `TESTNET_API_KEY` + `TESTNET_SECRET_KEY`
3. 最后使用环境变量中的其他 API Key

## 📁 修改的文件

### 1. config.py
- 新增 Demo Trading API 配置
- 支持期货和现货独立配置
- 自动检测 API Key 类型
- 增强的日志输出

### 2. trading/real_trader.py
- 新增 `use_futures` 参数
- 支持期货和现货独立初始化
- 改进的错误提示和日志

### 3. data_fetcher.py
- 新增 `use_futures` 参数
- 支持期货和现货独立初始化
- 改进的初始化日志

### 4. 新增测试文件
- `demo_trading_test.py` - 完整的 Demo Trading 集成测试
- `demo_quick_test.py` - 快速功能验证脚本

## 🚀 使用方法

### 快速验证
```bash
# 运行快速验证
python3 demo_quick_test.py

# 运行完整测试
python3 demo_trading_test.py

# 查看当前配置
python3 nof1.py --view

# 运行交易系统
python3 nof1.py --run 2
```

### 代码示例

#### 基本数据获取
```python
from data_fetcher import DataFetcher

# 现货数据
fetcher = DataFetcher(use_futures=False)
data = fetcher.get_market_data('BTCUSDT')
print(f"价格: {data['current_price']}")
fetcher.close()
```

#### 基本交易
```python
from trading.real_trader import RealTrader

# 现货交易
trader = RealTrader(use_futures=False)
price = trader.get_symbol_price('BTCUSDT')
print(f"BTC价格: ${price:,.2f}")
trader.close()
```

#### 期货交易
```python
# 期货数据
fetcher = DataFetcher(use_futures=True)
data = fetcher.get_market_data('BTCUSDT')
print(f"期货价格: {data['current_price']}")

# 期货交易
trader = RealTrader(use_futures=True)
price = trader.get_symbol_price('BTCUSDT')
print(f"期货价格: ${price:,.2f}")
trader.close()
```

## ⚠️ 注意事项

### API Key 权限
1. **读取权限**: 用于查询价格、余额等
2. **交易权限**: 用于下单、撤单等
3. **期货权限**: 用于期货交易

### URL 配置
- **现货**: `https://demo.binance.vision`
- **期货**: `https://demo.binancefuture.com`

### 兼容性
- 旧的 Testnet API 仍然支持
- 代码会自动检测并使用合适的 API
- 向后兼容旧配置

## 📊 测试结果

✅ **已验证功能**:
- [x] Demo Trading API 连接
- [x] 现货数据获取
- [x] 期货数据获取
- [x] 价格查询
- [x] 交易执行器初始化
- [x] 决策模型验证

⚠️ **需要注意**:
- API Key 需要开启相应权限
- 期货和现货 API 不同，需要分别配置
- 数据库保存功能需要进一步优化

## 🔄 迁移步骤

1. ✅ **升级代码** - 已完成
2. ✅ **配置 API Key** - 已完成
3. ✅ **测试验证** - 已完成
4. 🚀 **开始使用** - 可以开始了

## 📞 获取 API Key

访问 Binance Demo Trading 页面获取新的 API Key：
- https://www.binance.com/en/support/faq/detail/9be58f73e5e14338809e3b705b9687dd

## 🐛 问题排查

### 常见问题

1. **API Key 无效**
   ```
   错误: Invalid API-key, IP, or permissions for action
   解决: 检查 API Key 是否正确，是否开启相应权限
   ```

2. **无法获取余额**
   ```
   错误: 账户余额为空或无法获取
   解决: 确保 API Key 开启读取权限
   ```

3. **期货数据获取失败**
   ```
   错误: 'DataFetcher' object has no attribute 'get_symbol_price'
   解决: 使用正确的方法名 `get_ticker()` 获取期货价格
   ```

### 日志分析
查看详细日志：
```bash
python3 -c "import config; print(config.BINANCE_BASE_URL); print(config.CURRENT_MODE)"
```

## 🎯 下一步计划

- [ ] 优化数据库保存功能
- [ ] 添加更多测试用例
- [ ] 完善期货交易功能
- [ ] 添加实时监控功能

## 📝 更新记录

**2025-11-05**: 完成 Binance Demo Trading 升级
- 支持新的 Demo Trading API
- 期货和现货独立配置
- 增强的错误处理和日志
- 新增测试脚本
