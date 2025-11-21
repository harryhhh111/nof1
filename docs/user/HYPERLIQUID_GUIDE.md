# Hyperliquid 交易指南

本指南介绍如何在 nof1 项目中使用 Hyperliquid DEX 进行交易。

## 🚨 安全警告

**Hyperliquid 是真实去中心化交易所，所有交易都涉及真实资金！**

- ⚠️ **永远不要暴露私钥**
- ⚠️ **建议使用 Agent Wallet 模式**
- ⚠️ **先在测试网充分测试**
- ⚠️ **小额资金开始交易**

## 📋 目录

1. [Agent Wallet 安全模式](#agent-wallet-安全模式)
2. [环境配置](#环境配置)
3. [使用方法](#使用方法)
4. [测试网体验](#测试网体验)
5. [API 参考](#api-参考)
6. [故障排除](#故障排除)

## 🔐 Agent Wallet 安全模式

Hyperliquid 推荐使用 **Agent Wallet** 安全模式，将签名权限和资金分离：

### 安全架构

```
┌─────────────────┐    签名交易    ┌──────────────────┐
│   Agent Wallet  │ ──────────────→ │ Hyperliquid DEX  │
│ (私钥, ~0余额)   │               │                  │
└─────────────────┘               └──────────────────┘
       ▲                                   ▲
       │ 授权交易                           │ 持有资金
       │                                   │
┌─────────────────┐               ┌──────────────────┐
│  Main Wallet    │ ──────────────→ │  用户资金 USDC   │
│ (仅地址, 资金)   │   API授权      │                  │
└─────────────────┘               └──────────────────┘
```

### 创建 Agent Wallet

1. **访问 Hyperliquid 官网**: https://app.hyperliquid.xyz/
2. **创建 Agent Wallet**:
   - 设置 → API Wallets → Create API Wallet
   - 生成新的私钥（Agent Wallet）
   - 设置授权限额和权限
3. **获取配置信息**:
   - Agent Wallet 私钥（用于签名）
   - Main Wallet 地址（持有资金）

## ⚙️ 环境配置

### 1. 安装依赖

```bash
# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 环境变量配置

复制环境变量示例文件：
```bash
cp .env.example .env
```

编辑 `.env` 文件，添加 Hyperliquid 配置：

```bash
# Hyperliquid 配置
# Agent钱包私钥（仅用于签名，余额应接近0）
HYPERLIQUID_PRIVATE_KEY=your_agent_private_key_here

# 主钱包地址（持有资金，永不暴露私钥）
HYPERLIQUID_WALLET_ADDRESS=your_main_wallet_address_here

# 是否使用测试网 (推荐先测试)
HYPERLIQUID_USE_TESTNET=true
```

### 3. 验证配置

运行配置验证：
```bash
python3 -c "
import config
print(f'Agent Key configured: {bool(config.HYPERLIQUID_PRIVATE_KEY)}')
print(f'Wallet Address: {config.HYPERLIQUID_WALLET_ADDRESS}')
print(f'Use Testnet: {config.HYPERLIQUID_USE_TESTNET}')
"
```

## 🚀 使用方法

### 1. 直接使用 Hyperliquid 交易器

```python
from trading.hyperliquid_trader import HyperliquidTrader

# 创建交易器实例
trader = HyperliquidTrader(
    use_testnet=True,  # 先用测试网
    agent_private_key=os.getenv("HYPERLIQUID_PRIVATE_KEY"),
    main_wallet_address=os.getenv("HYPERLIQUID_WALLET_ADDRESS")
)

# 获取账户余额
balance = trader.get_account_balance()
print(f"账户余额: {balance}")

# 获取当前价格
price = trader.get_symbol_price("BTCUSDT")
print(f"BTC 价格: {price}")

# 下市价单
result = trader.place_market_order(
    symbol="BTCUSDT",
    side="buy",
    amount=0.001,
    reason="测试买入"
)
print(f"交易结果: {result}")
```

### 2. 通过交易工厂使用

```python
from trading.trading_factory import TradingFactory
import config

# 设置当前模式为 Hyperliquid
config.CURRENT_MODE = 'hyperliquid'

# 创建交易器
trader = TradingFactory.create_trader('hyperliquid')

# 执行交易决策
from models.trading_decision import TradingDecision

decision = TradingDecision(
    symbol="BTCUSDT",
    action="BUY",
    position_size=10,  # 10% 仓位
    reasoning="技术分析买入信号"
)

result = trader.execute_decision(decision)
print(f"执行结果: {result}")
```

### 3. 多账户交易配置

```python
# 在 config.py 中配置 Hyperliquid 账户
ACCOUNT_CONFIGS = {
    'account_hyperliquid_1': {
        'llm_model': 'deepseek',
        'symbols': ['BTCUSDT', 'ETHUSDT'],
        'exchange': 'hyperliquid',
        'description': 'Hyperliquid 主账户'
    }
}
```

## 🧪 测试网体验

Hyperliquid 提供测试网环境，可以安全地测试交易功能：

### 测试网配置

```bash
# 设置为测试网
HYPERLIQUID_USE_TESTNET=true
```

### 获取测试网资金

1. 访问 [Hyperliquid 测试网](https://testnet.hyperliquid.xyz/)
2. 连接钱包
3. 使用测试网水龙头获取测试 USDC

### 测试网功能

- ✅ 所有交易功能
- ✅ 模拟资金
- ✅ 无真实风险
- ✅ API 调试

## 📚 API 参考

### HyperliquidTrader 类

#### 初始化参数

```python
def __init__(
    self,
    database_path: Optional[str] = None,
    use_testnet: bool = False,
    agent_private_key: Optional[str] = None,
    main_wallet_address: Optional[str] = None
)
```

#### 主要方法

| 方法 | 描述 | 参数 | 返回 |
|------|------|------|------|
| `get_account_balance()` | 获取账户余额 | - | `Dict[str, float]` |
| `get_symbol_price(symbol)` | 获取价格 | `symbol: str` | `float` |
| `place_market_order(...)` | 下市价单 | `symbol, side, amount, reason` | `Dict[str, Any]` |
| `place_limit_order(...)` | 下限价单 | `symbol, side, amount, price, reason` | `Dict[str, Any]` |
| `set_stop_loss(...)` | 设置止损 | `symbol, side, amount, stop_price, reason` | `Dict[str, Any]` |
| `get_open_positions()` | 获取持仓 | - | `List[Dict[str, Any]]` |
| `execute_decision(decision)` | 执行交易决策 | `decision: TradingDecision` | `Dict[str, Any]` |

### Symbol 转换

Hyperliquid 使用简化的币种名称：

| 标准格式 | Hyperliquid 格式 |
|----------|------------------|
| BTCUSDT | BTC |
| ETHUSDT | ETH |
| SOLUSDT | SOL |

系统会自动处理格式转换。

## 🔧 故障排除

### 常见问题

#### 1. SDK 导入错误

```bash
# 错误: ImportError: No module named 'hyperliquid'
# 解决: 激活虚拟环境并安装依赖
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. 私钥格式错误

```bash
# 错误: ValueError: 主钱包地址格式错误
# 解决: 确保地址以 0x 开头且长度为 42 字符
export HYPERLIQUID_WALLET_ADDRESS="0x1234567890abcdef1234567890abcdef12345678"
```

#### 3. API 权限错误

```bash
# 错误: 权限不足
# 解决: 检查 Agent Wallet 授权设置
# 1. 访问 Hyperliquid 设置 → API Wallets
# 2. 确保 Agent Wallet 已授权
# 3. 检查权限设置（交易、读取等）
```

#### 4. 连接超时

```python
# 解决: 增加重试机制和超时设置
import time

max_retries = 3
for i in range(max_retries):
    try:
        result = trader.place_market_order(...)
        break
    except Exception as e:
        if i == max_retries - 1:
            raise
        time.sleep(2 ** i)  # 指数退避
```

### 调试模式

启用详细日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 或设置环境变量
export LOG_LEVEL=DEBUG
```

### 测试验证

运行测试套件：

```bash
# 运行 Hyperliquid 测试
python3 -m pytest tests/test_hyperliquid_trader.py -v

# 运行集成测试（需要真实 API）
python3 tests/test_hyperliquid_trader.py
```

## 📞 支持

- **官方文档**: https://hyperliquid.gitbook.io/hyperliquid-docs/
- **Python SDK**: https://github.com/hyperliquid-dex/hyperliquid-python-sdk
- **社区支持**: Hyperliquid Discord
- **项目问题**: 提交 GitHub Issue

## ⚠️ 免责声明

使用 Hyperliquid 进行交易涉及真实资金风险：

- 本软件仅作为工具提供，不承担任何交易损失责任
- 用户应充分理解去中心化交易的风险
- 建议先在测试网充分测试
- 仅投入可承受损失的资金
- 遵守当地法律法规

**交易有风险，入市需谨慎！**