# Nof1 - Binance Testnet 快速开始指南

## 🚀 快速开始（5分钟）

### 步骤1: 获取 Testnet API Key

```bash
# 1. 访问 https://testnet.binance.vision/
# 2. 使用 GitHub 登录
# 3. 复制显示的 API Key 和 Secret Key
```

### 步骤2: 设置环境变量

```bash
export TESTNET_API_KEY="your_api_key_here"
export TESTNET_SECRET_KEY="your_secret_key_here"
export USE_TESTNET="true"
```

### 步骤3: 运行测试

```bash
# 测试所有组件
python testnet_demo.py

# 预期输出：
# ✅ DataFetcher 初始化成功
# ✅ RealTrader 初始化成功
# ✅ 交易执行器测试通过
# ✅ 所有测试通过！
```

### 步骤4: 尝试交易

```python
from trading.real_trader import RealTrader
from models.trading_decision import TradingDecision

trader = RealTrader()

# 查看余额
balance = trader.get_account_balance()
print(f"USDT余额: {balance.get('USDT', 0)}")

# 获取价格
price = trader.get_symbol_price('BTCUSDT')
print(f"BTC价格: ${price:,.2f}")

# 创建小仓位测试决策（1%仓位）
decision = TradingDecision(
    action="BUY",
    confidence=50.0,
    entry_price=price,
    stop_loss=price * 0.99,  # 1%止损
    take_profit=price * 1.02,  # 2%止盈
    position_size=1.0,  # 1%仓位
    risk_level="LOW",
    reasoning="小仓位测试交易",
    timeframe="3m",
    symbol="BTCUSDT"
)

# 执行交易
result = trader.execute_decision(decision)
print(f"交易结果: {result}")

trader.close()
```

## 📁 重要文件

| 文件 | 说明 |
|------|------|
| `config.py` | 全局配置（切换模式） |
| `data_fetcher.py` | 数据获取器（支持Testnet） |
| `trading/real_trader.py` | 真实交易执行器 |
| `testnet_demo.py` | Testnet测试脚本 |
| `docs/user/TESTNET_INTEGRATION.md` | 详细文档 |

## ⚡ 模式切换

```python
# config.py 中切换
USE_TESTNET = True   # Testnet模式（默认）
USE_TESTNET = False  # 实盘模式（高风险！）
```

## 🛠️ 常用操作

### 获取数据
```python
from data_fetcher import DataFetcher

fetcher = DataFetcher()
data = fetcher.get_market_data('BTCUSDT')
fetcher.close()
```

### 执行交易
```python
from trading.real_trader import RealTrader

trader = RealTrader()

# 市价单
result = trader.place_market_order('BTCUSDT', 'buy', 0.001)

# 限价单
result = trader.place_limit_order('BTCUSDT', 'buy', 0.001, 68000)

# 查询订单
status = trader.get_order_status('BTCUSDT', 'order_id')

# 撤单
trader.cancel_order('BTCUSDT', 'order_id')

trader.close()
```

### 查看交易记录
```python
trades = trader.get_trades(limit=10)
for trade in trades:
    print(f"{trade['side']} {trade['amount']} @ ${trade['price']}")
```

## ⚠️ 安全提醒

1. **Testnet Key ≠ 实盘 Key**：永远不要混用
2. **实盘前检查**：
   ```bash
   grep -r "USE_TESTNET = False" config.py
   # 确保没有遗漏
   ```
3. **小仓位测试**：首次实盘使用最小仓位
4. **设置止损**：所有交易必须有止损
5. **监控日志**：检查 `nof1.log` 了解运行状态

## 📊 数据结构

### 市场数据（data_fetcher.py 返回）
```python
{
    "symbol": "BTCUSDT",
    "timestamp": "2025-11-04 10:30:00",
    "current_price": 70000.0,
    "intraday": {
        "prices": [...],
        "ema20": [...],
        "macd": [...],
        "rsi_7": [...],
        "rsi_14": [...]
    },
    "long_term": {
        "ema_20": 69500.0,
        "ema_50": 68000.0,
        "atr_14": 1500.0,
        "volume_current": 1234.5
    },
    "perp_data": {
        "funding_rate": 0.0001,
        "open_interest_latest": 50000000
    }
}
```

### 交易决策（TradingDecision）
```python
{
    "action": "BUY|SELL|HOLD",
    "confidence": 80.0,
    "entry_price": 70000.0,
    "stop_loss": 68600.0,
    "take_profit": 72800.0,
    "position_size": 10.0,  # 百分比
    "risk_level": "MEDIUM",
    "reasoning": "详细分析...",
    "timeframe": "4h"
}
```

## 🔧 故障排除

### 错误：Invalid API key
```bash
# 检查环境变量
echo $TESTNET_API_KEY
echo $TESTNET_SECRET_KEY

# 或检查 config.py
grep "TESTNET_API_KEY" config.py
```

### 错误：Timestamp out of range
```bash
# 同步系统时间
sudo ntpdate -s time.nist.gov
```

### 错误：Network timeout
```python
# 增加超时时间
import ccxt
exchange = ccxt.binance({
    'timeout': 30000,  # 30秒
    'rateLimit': 100,
})
```

### 查看日志
```bash
tail -f nof1.log
```

## 📈 下一步计划

1. ✅ **已完成**：
   - 数据收集模块
   - Testnet集成
   - 真实交易执行器
   - 决策模型
   - 提示生成器

2. 🔄 **进行中**：
   - LLM客户端集成
   - 自动化交易流程
   - 风险管理模块

3. 📋 **待开发**：
   - Web界面
   - 实时监控面板
   - 性能分析工具
   - 回测引擎

## 💡 使用技巧

1. **分阶段测试**：
   ```bash
   # 第1阶段：验证数据
   python -c "from data_fetcher import DataFetcher; f=DataFetcher(); print(f.get_market_data('BTCUSDT')['current_price']); f.close()"

   # 第2阶段：验证交易
   python testnet_demo.py

   # 第3阶段：小仓位实盘
   ```

2. **批量查询**：
   ```python
   symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
   fetcher = DataFetcher()
   data = fetcher.get_multiple_symbols_data(symbols)
   fetcher.close()
   ```

3. **保存历史数据**：
   ```python
   import json
   from datetime import datetime

   data = fetcher.get_market_data('BTCUSDT')
   filename = f"btc_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
   with open(filename, 'w') as f:
       json.dump(data, f, indent=2)
   ```

## 📚 更多资源

- **详细文档**：`docs/user/TESTNET_INTEGRATION.md`
- **API参考**：查看各模块的 docstring
- **示例代码**：`testnet_demo.py`
- **测试用例**：`tests/` 目录

## 🤝 获取帮助

1. 查看日志：`tail -f nof1.log`
2. 运行测试：`python testnet_demo.py`
3. 检查配置：`python -c "import config; print(config.CURRENT_MODE)"`
4. 查看文档：`cat docs/user/TESTNET_INTEGRATION.md`

---

**祝交易愉快！** 🎉

记住：**模拟环境的表现永远不能完全预测实盘结果**。在实盘交易前，请务必：
- 充分测试策略
- 设置合理的风险管理
- 从小仓位开始
- 持续监控和优化
