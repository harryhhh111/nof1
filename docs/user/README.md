# Nof1 数据获取与交易系统

基于 Nof1 Alpha Arena 的数据获取系统，实现加密货币市场数据的获取、存储、分析和真实交易功能。

## 项目概述

本系统实现了类似 Nof1 Alpha Arena 的数据获取和交易功能，支持：

- 多交易所数据获取（目前支持 Binance）
- 实时市场数据获取
- 技术指标计算（EMA, MACD, RSI, ATR）
- 永续合约数据（资金费率、开放利息）
- 数据持久化存储
- 定时数据更新
- **Binance Testnet 真实模拟交易**
- **纸交易和真实交易模式切换**
- **智能订单管理（市价单、限价单、止损止盈）**

## 系统架构

```
┌─────────────────┐
│   main.py       │  主程序入口
└────────┬────────┘
         │
    ┌────┴────┬─────────────┐
    ▼         ▼             ▼
┌─────────┐ ┌──────────┐ ┌──────────┐
│fetcher  │ │indicators│ │ scheduler│
└─────────┘ └──────────┘ └──────────┘
    │           │           │
    └────┬──────┴────┬──────┘
         ▼           ▼
    ┌──────────────────┐
    │   database.py    │
    └──────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│       Trading Modules           │
│  ┌───────────────────────────┐  │
│  │  Paper Trader (纸交易)     │  │
│  └───────────────────────────┘  │
│  ┌───────────────────────────┐  │
│  │  Real Trader (真实交易)    │  │
│  │  - Testnet 模拟交易        │  │
│  │  - Live 实盘交易          │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

## 数据结构

### 1. 日内数据（3分钟间隔）
- **价格数据**：当前价格 + 历史价格序列（10个数据点）
- **技术指标**：
  - EMA (20-period)
  - MACD
  - RSI (7-period 和 14-period)
- **交易量**：当前交易量 vs 历史平均

### 2. 4小时长期数据
- **移动平均线**：20期 EMA vs 50期 EMA
- **波动率指标**：ATR (3-period 和 14-period)
- **技术指标**：MACD 和 RSI（4小时级别）
- **交易量**：当前交易量 vs 平均交易量

### 3. 永续合约数据
- **开放利息**：Latest 和 Average
- **资金费率**：Funding Rate

## 安装与使用

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置

编辑 `config.py` 文件，设置：
- 交易所 API 配置
- 数据更新间隔
- 数据库路径
- 交易品种列表

### 3. 运行

```bash
python main.py
```

## 项目结构

```
nof1/
├── README.md              # 项目文档
├── CLAUDE.md              # AI 开发指南
├── QUICKSTART.md          # 快速入门指南
├── INSTALL.md             # 安装说明
├── requirements.txt       # Python 依赖
├── config.py              # 配置文件
├── main.py               # 主程序
├── data_fetcher.py       # 数据获取模块
├── indicators.py         # 技术指标计算
├── database.py           # 数据库操作
├── scheduler.py          # 定时任务调度
├── test_basic.py         # 基础功能测试
├── run_tests.py          # 测试运行脚本
└── tests/                # 测试目录
    ├── __init__.py
    ├── test_config.py
    ├── test_indicators.py
    ├── test_database.py
    ├── test_data_fetcher.py
    ├── test_scheduler.py
    └── test_integration.py
```

## 使用示例

### 获取单个交易对数据

```bash
# 获取 BTC 数据（JSON 格式）
python main.py --symbol BTCUSDT

# 以可读格式输出
python main.py --symbol BTCUSDT --output print
```

### 获取多个交易对数据

```bash
python main.py --symbols BTCUSDT ETHUSDT SOLUSDT
```

### 启动定时调度器

```bash
# 启动调度器（默认每 3 分钟更新一次）
python main.py --schedule

# 自定义间隔和交易对
python main.py --schedule --symbols BTCUSDT ETHUSDT --interval 60
```

### 查询数据库中的数据

```bash
python main.py --query --symbols BTCUSDT
```

### 查看系统状态

```bash
python main.py --status
```

### Binance Testnet 真实交易（新增）

#### 配置 Testnet API

**方法 1: .env 文件（推荐）**

创建 `.env` 文件：
```bash
TESTNET_API_KEY=your_testnet_api_key
TESTNET_SECRET_KEY=your_testnet_secret_key
USE_TESTNET=true
```

**方法 2: 环境变量**
```bash
export TESTNET_API_KEY="your_api_key"
export TESTNET_SECRET_KEY="your_secret_key"
export USE_TESTNET="true"
```

#### 运行 Testnet 测试

```bash
# 验证 Testnet 连接
python3 testnet_demo.py

# 查看持仓和交易
python3 testnet_viewer.py
```

#### 真实交易示例

**Python 代码示例:**
```python
from trading.real_trader import RealTrader
from models.trading_decision import TradingDecision

# 初始化交易器
trader = RealTrader()

# 查看账户余额
balance = trader.get_account_balance()
print(f"USDT余额: {balance.get('USDT', 0)}")

# 获取当前价格
btc_price = trader.get_symbol_price('BTCUSDT')
print(f"BTC价格: ${btc_price:,.2f}")

# 市价买入
result = trader.place_market_order(
    symbol='BTCUSDT',
    side='buy',
    amount=0.001,  # 0.001 BTC
    reason="Testnet测试交易"
)

# 限价买入
result = trader.place_limit_order(
    symbol='BTCUSDT',
    side='buy',
    amount=0.001,
    price=95000.0,  # $95,000
    reason="限价买入测试"
)

# 设置止损
result = trader.set_stop_loss(
    symbol='BTCUSDT',
    side='long',
    amount=0.001,
    stop_price=94000.0,
    reason="止损保护"
)

# 查看交易记录
trades = trader.get_trades(100)
for trade in trades[-10:]:
    print(f"{trade['side']} {trade['amount']} {trade['symbol']} @ ${trade['price']}")

trader.close()
```

#### 交易模式切换

在 `config.py` 中：
```python
# 纸交易模式（虚拟资金，完全安全）
USE_TESTNET = False
CURRENT_MODE = 'paper'

# Testnet 模式（真实API，虚拟资金）
USE_TESTNET = True
CURRENT_MODE = 'testnet'

# 实盘模式（真实API，真实资金 - 高风险！）
USE_TESTNET = False
BINANCE_API_KEY = "real_api_key"
CURRENT_MODE = 'live'
```

#### Web 界面查看（推荐）

访问：https://testnet.binance.vision/

- **Portfolio**: 查看余额和价值
- **Orders**: 查看挂单
- **Trade History**: 查看历史交易
- **Fills**: 查看成交记录

## API 参考

### DataFetcher

主要的数据获取类。

```python
from data_fetcher import DataFetcher

# 初始化
fetcher = DataFetcher()

# 获取 K 线数据
klines = fetcher.get_klines('BTCUSDT', '3m', limit=50)

# 获取技术指标
indicators = fetcher.calculate_all_indicators(klines)

# 获取完整市场数据
market_data = fetcher.get_market_data('BTCUSDT')
```

### 计算的技术指标

- **EMA (20-period)**: 指数移动平均线
- **MACD**: 移动平均收敛散度
  - MACD Line
  - Signal Line
  - Histogram
- **RSI (7-period, 14-period)**: 相对强弱指数
- **ATR (3-period, 14-period)**: 平均真实波幅
- **交易量分析**: 当前 vs 平均

### 数据格式

根据 Nof1 Alpha Arena 的数据格式：

```json
{
    "symbol": "BTCUSDT",
    "timestamp": "2025-10-19 10:10:00",
    "current_price": 107982.5,
    "intraday": {
        "prices": [107726.5, 107741.0, ...],
        "ema20": [107540.298, 107556.175, ...],
        "macd": [10.802, 21.816, ...],
        "rsi_7": [73.026, 71.971, ...],
        "rsi_14": [59.393, 59.004, ...]
    },
    "long_term": {
        "ema_20": 107854.332,
        "ema_50": 110571.164,
        "atr_3": 557.797,
        "atr_14": 1145.893,
        "volume_current": 5.495,
        "volume_average": 5047.135,
        "macd": [-1914.209, -1853.793, ...],
        "rsi_14": [35.766, 37.705, ...]
    },
    "perp_data": {
        "open_interest_latest": 25458.85,
        "open_interest_average": 25461.32,
        "funding_rate": 8.2948e-06
    }
}
```

## 配置说明

### config.py

```python
# 数据更新间隔（秒）
UPDATE_INTERVAL = 180  # 3分钟

# 数据库配置
DATABASE_PATH = "market_data.db"

# 交易品种
SYMBOLS = [
    'BTCUSDT',
    'ETHUSDT',
    'SOLUSDT',
    'BNBUSDT',
    'DOGEUSDT',
    'XRPUSDT'
]

# 时间间隔
INTERVALS = {
    'intraday': '3m',
    'long_term': '4h'
}

# 技术指标参数
INDICATOR_PARAMS = {
    'ema_short': 20,
    'ema_long': 50,
    'rsi_short': 7,
    'rsi_long': 14,
    'atr_short': 3,
    'atr_long': 14
}
```

## 技术指标说明

### EMA (指数移动平均线)
- **20期 EMA**: 用于短期趋势分析
- **50期 EMA**: 用于长期趋势分析
- 当价格上穿 EMA 时，可能表示上涨趋势
- 当价格下穿 EMA 时，可能表示下跌趋势

### MACD (移动平均收敛散度)
- **MACD 线**: 快速EMA(12) - 慢速EMA(26)
- **Signal 线**: MACD 线的 9期 EMA
- **Histogram**: MACD 线 - Signal 线
- 金叉：MACD 上穿 Signal，可能买入信号
- 死叉：MACD 下穿 Signal，可能卖出信号

### RSI (相对强弱指数)
- **RSI7**: 短期相对强弱，波动更敏感
- **RSI14**: 长期相对强弱，更稳定
- **RSI > 70**: 可能超买，价格可能下跌
- **RSI < 30**: 可能超卖，价格可能上涨

### ATR (平均真实波幅)
- **ATR3**: 短期波动率，反映近期价格波动
- **ATR14**: 长期波动率，反映整体市场波动
- ATR 值越大，市场波动越剧烈
- 用于设置止损和止盈点位

### 交易量分析
- **当前交易量 vs 平均交易量**
- 交易量放大通常伴随价格突破
- 交易量萎缩可能表示趋势减弱

## 测试

### 运行基础功能测试

```bash
python3 test_basic.py
```

### 运行完整测试套件

```bash
python3 run_tests.py
```

### 使用 pytest

```bash
pip install pytest
pytest tests/ -v
```

## 数据库

系统使用 SQLite 数据库存储数据，主要表：

1. **klines_3m** - 3 分钟 K 线数据
2. **klines_4h** - 4 小时 K 线数据
3. **technical_indicators** - 技术指标数据
4. **perpetual_data** - 永续合约数据

默认数据库文件：`market_data.db`

## 日志

系统运行时会生成日志文件 `nof1.log`：

```bash
# 实时查看日志
tail -f nof1.log

# 查看最近 100 行
tail -100 nof1.log
```

## 交易模式说明

### 1. 纸交易模式（Paper Trading）
- **资金**: 虚拟100,000 USDT
- **特点**: 完全模拟，无风险
- **使用**: `python -c "from trading.paper_trader import PaperTrader; ..."`

### 2. Testnet 模拟交易（推荐测试）
- **资金**: Binance 提供的虚拟资金
- **API**: 使用真实 Binance API（testnet.binance.vision）
- **特点**: 接近真实交易环境，但无资金风险
- **使用**: 需要申请 Testnet API Key
- **Web**: https://testnet.binance.vision/

### 3. 实盘交易（高风险！）
- **资金**: 真实资金
- **API**: 生产环境 Binance API
- **特点**: 真实交易，有盈亏
- **注意**: 务必先在 Testnet 充分测试！

## 交易功能详解

### 支持的订单类型
1. **市价单（Market Order）**
   - 立即以市场价成交
   - 适合快速入场/出场

2. **限价单（Limit Order）**
   - 指定价格成交
   - 适合精确入场点位

3. **止损单（Stop Order）**
   - 触发后以市价或限价成交
   - 用于风险控制

### 自动风险管理
- **止损（Stop Loss）**: 自动限制最大损失
- **止盈（Take Profit）**: 自动锁定利润
- **仓位管理**: 基于百分比计算仓位大小
- **风险评估**: 自动评估交易风险等级

### 交易记录与追踪
- **SQLite 数据库**: 自动保存所有交易记录
- **实时PnL**: 实时计算未实现和已实现损益
- **性能指标**: 胜率、总收益率、最大回撤等
- **历史回测**: 支持基于历史数据的策略回测

## 未来计划

- [x] ✅ 完成 Binance Testnet 集成
- [x] ✅ 实现真实交易执行器
- [x] ✅ 支持多种订单类型
- [ ] 支持更多交易所（Hyperliquid, OKX, Bybit）
- [ ] 添加更多技术指标
- [ ] 实现 WebSocket 实时数据推送
- [ ] 添加数据可视化
- [ ] 实现 LLM 驱动的自动交易
- [ ] 开发 Web 管理界面

## 参考资料

- [Nof1 Alpha Arena](https://nof1.ai)
- [Binance API 文档](https://binance-docs.github.io/apidocs/spot/en/)
- [pandas 技术指标库](https://github.com/twopirllc/pandas-ta)

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题，请通过 GitHub Issues 联系我们。
