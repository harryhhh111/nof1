# Binance Testnet 集成指南

## 概述

本指南详细说明如何集成 Binance Testnet 进行真实的模拟交易测试。Testnet 提供了接近真实交易环境的体验，但使用虚拟资金，适合安全地测试交易策略。

## 目录

- [获取 Testnet 账号](#获取-testnet-账号)
- [配置 API Key](#配置-api-key)
- [系统架构](#系统架构)
- [使用指南](#使用指南)
- [API 参考](#api-参考)
- [注意事项](#注意事项)
- [常见问题](#常见问题)

---

## 获取 Testnet 账号

### 步骤 1: 访问 Testnet 网站

打开浏览器，访问：https://testnet.binance.vision/

### 步骤 2: 登录

- **推荐方式**：使用 GitHub 账号登录（最快）
- **替代方式**：使用 Binance 账号登录

### 步骤 3: 获取 API Key

登录成功后，页面顶部会显示：

```
Testnet API Key: abc123def456...
Testnet Secret Key: xyz789uvw012...
```

**⚠️ 重要**：请妥善保管这些密钥，不要分享给他人！

### 步骤 4: 检查虚拟资金

Testnet 默认提供虚拟资金：
- BTC: ~1000
- USDT: ~10000
- ETH: ~100
- 其他主流币种若干

如需更多资金，点击 **"Faucet"** 按钮申请。

---

## 配置 API Key

### 方法 1: 环境变量（推荐）

在终端中执行：

```bash
export TESTNET_API_KEY="your_testnet_api_key_here"
export TESTNET_SECRET_KEY="your_testnet_secret_key_here"
export USE_TESTNET="true"
```

为了让设置永久生效，添加到 `~/.bashrc` 或 `~/.zshrc`：

```bash
echo 'export TESTNET_API_KEY="your_testnet_api_key_here"' >> ~/.bashrc
echo 'export TESTNET_SECRET_KEY="your_testnet_secret_key_here"' >> ~/.bashrc
echo 'export USE_TESTNET="true"' >> ~/.bashrc
source ~/.bashrc
```

### 方法 2: 修改 config.py

编辑 `/home/claude_user/nof1/config.py`：

```python
# Testnet API Key
TESTNET_API_KEY = "your_testnet_api_key_here"
TESTNET_SECRET_KEY = "your_testnet_secret_key_here"
USE_TESTNET = True
```

### 方法 3: .env 文件

创建 `.env` 文件：

```bash
TESTNET_API_KEY=your_testnet_api_key_here
TESTNET_SECRET_KEY=your_testnet_secret_key_here
USE_TESTNET=true
```

然后安装 python-dotenv：

```bash
pip install python-dotenv
```

在 `config.py` 顶部添加：

```python
from dotenv import load_dotenv
load_dotenv()
```

---

## 系统架构

### 交易模式

系统支持三种交易模式：

| 模式 | 环境 | 资金 | API Key | 风险 |
|------|------|------|---------|------|
| PAPER | 虚拟 | 虚拟100k USDT | ❌ 无需 | 🟢 零风险 |
| TESTNET | Binance Testnet | 虚拟资金 | ✅ 需要 | 🟡 低风险 |
| LIVE | Binance 实盘 | 真实资金 | ✅ 需要 | 🔴 高风险 |

### 核心组件

```
┌─────────────────────────────────────────────────────────┐
│                    config.py                            │
│  - EXCHANGE_CONFIG: 交易所配置                          │
│  - USE_TESTNET: Testnet 开关                            │
│  - CURRENT_MODE: 当前模式                               │
└─────────────────┬───────────────────────────────────────┘
                  │
      ┌───────────┴───────────┐
      ▼                       ▼
┌─────────────┐       ┌──────────────────┐
│DataFetcher  │       │   RealTrader     │
│数据获取器   │       │  真实交易执行器   │
│ - 实时数据  │       │ - 市价单/限价单  │
│ - 技术指标  │       │ - 止损止盈       │
│ - 多时间框架│       │ - 订单管理       │
└─────────────┘       └──────────────────┘
```

---

## 使用指南

### 1. 基础测试

运行测试脚本验证集成：

```bash
python testnet_demo.py
```

期望输出：

```
✅ DataFetcher 初始化成功
✅ RealTrader 初始化成功
✅ 交易执行器测试通过
✅ 所有测试通过！
```

### 2. 数据获取

```python
from data_fetcher import DataFetcher

# 初始化数据获取器
fetcher = DataFetcher()

# 获取单个交易对数据
btc_data = fetcher.get_market_data('BTCUSDT')
print(f"BTC价格: ${btc_data['current_price']:,.2f}")

# 获取多个交易对数据
symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
data = fetcher.get_multiple_symbols_data(symbols)

fetcher.close()
```

### 3. 真实交易

```python
from trading.real_trader import RealTrader
from models.trading_decision import TradingDecision

# 初始化交易执行器
trader = RealTrader()

# 检查账户余额
balance = trader.get_account_balance()
print(f"USDT余额: {balance.get('USDT', 0)}")

# 获取当前价格
price = trader.get_symbol_price('BTCUSDT')
print(f"BTC价格: ${price:,.2f}")

# 创建交易决策
decision = TradingDecision(
    action="BUY",
    confidence=80.0,
    entry_price=price,
    stop_loss=price * 0.98,  # 2% 止损
    take_profit=price * 1.05,  # 5% 止盈
    position_size=10.0,  # 10% 仓位
    risk_level="MEDIUM",
    reasoning="Testnet测试交易",
    timeframe="4h",
    symbol="BTCUSDT"
)

# 执行交易
result = trader.execute_decision(decision)
print(f"交易结果: {result}")

trader.close()
```

### 4. 下单类型

#### 市价单

```python
# 市价买入
result = trader.place_market_order(
    symbol='BTCUSDT',
    side='buy',
    amount=0.001,  # BTC数量
    reason="市价买入测试"
)

# 市价卖出
result = trader.place_market_order(
    symbol='BTCUSDT',
    side='sell',
    amount=0.001,
    reason="市价卖出测试"
)
```

#### 限价单

```python
# 限价买入（当前价格下方）
result = trader.place_limit_order(
    symbol='BTCUSDT',
    side='buy',
    amount=0.001,
    price=68000.0,  # 指定价格
    reason="限价买入测试"
)

# 限价卖出（当前价格上方）
result = trader.place_limit_order(
    symbol='BTCUSDT',
    side='sell',
    amount=0.001,
    price=72000.0,
    reason="限价卖出测试"
)
```

#### 止损单

```python
# 设置多头止损（价格下跌时触发卖出）
result = trader.set_stop_loss(
    symbol='BTCUSDT',
    side='long',
    amount=0.001,
    stop_price=65000.0,
    reason="多头止损保护"
)
```

### 5. 订单管理

```python
# 查询订单状态
status = trader.get_order_status('BTCUSDT', 'order_id_123')
print(f"订单状态: {status}")

# 撤单
result = trader.cancel_order('BTCUSDT', 'order_id_123')
print(f"撤单结果: {result}")

# 获取持仓
positions = trader.get_open_positions()
for pos in positions:
    print(f"{pos['symbol']}: {pos['contracts']} @ {pos['entryPrice']}")
```

### 6. 模式切换

在 `config.py` 中切换模式：

```python
# 启用 Testnet
USE_TESTNET = True  # 自动切换到 TESTNET 模式

# 禁用 Testnet（切换到实盘）
USE_TESTNET = False  # 切换到实盘（高风险！）

# 或使用环境变量
export USE_TESTNET=false
```

---

## API 参考

### config.py

#### EXCHANGE_CONFIG

交易所配置字典，包含 API Key、Secret 和模式设置。

```python
EXCHANGE_CONFIG = {
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_SECRET_KEY,
    'sandbox': USE_TESTNET,  # 关键：启用/禁用沙盒模式
    'enableRateLimit': True,
}
```

#### CURRENT_MODE

当前交易模式字符串：
- `'paper'`: 纸交易模式
- `'testnet'`: Testnet 模拟交易模式
- `'live'`: 实盘交易模式

### RealTrader

#### 初始化

```python
trader = RealTrader(database_path=None, fee_rate=0.001)
```

参数：
- `database_path`: 数据库文件路径（可选）
- `fee_rate`: 手续费率（默认 0.001 = 0.1%）

#### 方法

| 方法 | 说明 | 返回值 |
|------|------|--------|
| `get_account_balance()` | 获取账户余额 | Dict[str, float] |
| `get_symbol_price(symbol)` | 获取当前价格 | float |
| `place_market_order()` | 下市价单 | Dict |
| `place_limit_order()` | 下限价单 | Dict |
| `set_stop_loss()` | 设置止损单 | Dict |
| `execute_decision()` | 执行交易决策 | Dict |
| `cancel_order()` | 撤单 | Dict |
| `get_order_status()` | 查询订单状态 | Dict |
| `get_open_positions()` | 获取持仓 | List |
| `get_trades()` | 获取交易记录 | List |

---

## 注意事项

### ⚠️ 安全注意事项

1. **绝对不要**在实盘环境使用 Testnet API Key
2. **绝对不要**将 API Key 提交到 Git 或其他版本控制系统
3. 在生产环境部署前，**务必删除**或**禁用**Testnet 相关配置
4. 定期**轮换 API Key**，尤其是在测试环境变化时

### ⚠️ 交易注意事项

1. **Testnet 是模拟环境**，但使用真实 API 调用
2. Testnet 的市场数据**可能与实盘略有差异**
3. Testnet 的撮合逻辑可能**不如实盘精准**
4. **不要依赖**Testnet 的结果预测实盘表现
5. Testnet 可能**不稳定**或**间歇性故障**

### ⚠️ 代码注意事项

1. **始终检查**`config.CURRENT_MODE` 或 `config.USE_TESTNET` 确认当前模式
2. **实盘交易前**，务必彻底测试所有逻辑
3. **设置合理的止损**，避免模拟环境的意外损失
4. **监控余额**，避免模拟资金不足

### ⚠️ 性能注意事项

1. Testnet API 响应可能**比实盘慢**
2. Testnet 的撮合**可能延迟**
3. 建议在 Testnet 使用的**请求频率**低于实盘
4. 为网络问题**准备重试机制**

---

## 常见问题

### Q1: 报错 "Invalid API key"

**A**: 检查 API Key 是否正确设置：
```bash
echo $TESTNET_API_KEY
echo $TESTNET_SECRET_KEY
```

确保密钥完整且没有多余的空格。

### Q2: 报错 "Timestamp" 相关错误

**A**: 可能是因为：
- 系统时间不同步
- Testnet 服务器延迟

解决：
```python
# 检查时间同步
from datetime import datetime
print(f"当前时间: {datetime.now()}")
```

### Q3: 市价单立即成交但价格不是当前价格

**A**: 这是正常的！Testnet 的撮合逻辑基于订单簿深度，会产生滑点。

### Q4: 订单一直处于 "pending" 状态

**A**:
- 限价单可能价格不合适
- Testnet 服务器可能延迟
- 检查订单状态：
```python
status = trader.get_order_status(symbol, order_id)
print(status)
```

### Q5: 如何在实盘和 Testnet 之间切换？

**A**:
```python
# 修改 config.py
USE_TESTNET = False  # 切换到实盘

# 或使用环境变量
export USE_TESTNET=false

# 重新启动程序
python your_script.py
```

⚠️ **实盘交易前，务必：**
1. 仔细检查所有配置
2. 设置合理的仓位大小
3. 准备止损策略
4. 熟悉实盘交易规则

### Q6: Testnet 支持哪些交易对？

**A**: 大部分主流交易对都支持，但请检查：
```python
# 尝试获取 ticker
ticker = exchange.fetch_ticker('BTCUSDT')
```

如果成功，说明支持该交易对。

### Q7: 如何监控交易表现？

**A**:
```python
# 获取交易记录
trades = trader.get_trades(limit=50)
for trade in trades:
    print(f"{trade['symbol']}: {trade['side']} {trade['amount']} @ {trade['price']}")

# 获取账户价值
balance = trader.get_account_balance()
total_value = sum(amount for asset, amount in balance.items() if asset == 'USDT')
print(f"总价值 (USDT): {total_value}")
```

### Q8: 如何备份交易数据？

**A**: 数据已自动保存到 SQLite 数据库：
```bash
# 备份数据库
cp real_trading.db real_trading_backup_$(date +%Y%m%d).db

# 查看数据库内容
sqlite3 real_trading.db "SELECT * FROM orders LIMIT 10;"
```

---

## 总结

Binance Testnet 提供了一个安全、真实的模拟交易环境。通过本指南，你应该能够：

✅ 成功获取 Testnet 账号和 API Key
✅ 配置系统集成 Testnet
✅ 执行真实模拟交易
✅ 管理订单和持仓
✅ 监控交易表现
✅ 理解安全注意事项

**下一步**：

1. 在 Testnet 中充分测试你的交易策略
2. 优化风险管理逻辑
3. 确保代码在模拟环境中稳定运行
4. 实盘交易前进行最终检查

**记住**：Testnet 是学习和测试的好工具，但**永远无法完全替代实盘**。最终的策略表现需要在真实市场中验证。

---

## 支持

如果遇到问题：

1. 查看本文档的常见问题部分
2. 检查 GitHub Issues：https://github.com/your-repo/issues
3. 查看日志文件：`nof1.log`
4. 联系维护团队

---

**更新时间**：2025-11-04
**版本**：v1.0
**作者**：Claude Code
