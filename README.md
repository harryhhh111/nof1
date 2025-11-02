# Nof1 数据获取系统                                                                                                         │
│                                                                                                                             │
│ 基于 Nof1 Alpha Arena 的数据获取系统，实现加密货币市场数据的获取、存储和分析功能。                                          │
│                                                                                                                             │
│ ## 项目概述                                                                                                                 │
│                                                                                                                             │
│ 本系统实现了类似 Nof1 Alpha Arena 的数据获取功能，支持：                                                                    │
│                                                                                                                             │
│ - 多交易所数据获取（目前支持 Binance）                                                                                      │
│ - 实时市场数据获取                                                                                                          │
│ - 技术指标计算（EMA, MACD, RSI, ATR）                                                                                       │
│ - 永续合约数据（资金费率、开放利息）                                                                                        │
│ - 数据持久化存储                                                                                                            │
│ - 定时数据更新                                                                                                              │
│                                                                                                                             │
│ ## 系统架构                                                                                                                 │
│                                                                                                                             │
│ ```                                                                                                                         │
│ ┌─────────────────┐                                                                                                         │
│ │   main.py       │  主程序入口                                                                                             │
│ └────────┬────────┘                                                                                                         │
│          │                                                                                                                  │
│     ┌────┴────┬─────────────┐                                                                                               │
│     ▼         ▼             ▼                                                                                               │
│ ┌─────────┐ ┌──────────┐ ┌──────────┐                                                                                       │
│ │fetcher  │ │indicators│ │ scheduler│                                                                                       │
│ └─────────┘ └──────────┘ └──────────┘                                                                                       │
│     │           │           │                                                                                               │
│     └────┬──────┴────┬──────┘                                                                                               │
│          ▼           ▼                                                                                                      │
│     ┌──────────────────┐                                                                                                    │
│     │   database.py    │                                                                                                    │
│     └──────────────────┘                                                                                                    │
│ ```                                                                                                                         │
│                                                                                                                             │
│ ## 数据结构                                                                                                                 │
│                                                                                                                             │
│ ### 1. 日内数据（3分钟间隔）                                                                                                │
│ - **价格数据**：当前价格 + 历史价格序列（10个数据点）                                                                       │
│ - **技术指标**：                                                                                                            │
│   - EMA (20-period)                                                                                                         │
│   - MACD                                                                                                                    │
│   - RSI (7-period 和 14-period)                                                                                             │
│ - **交易量**：当前交易量 vs 历史平均                                                                                        │
│                                                                                                                             │
│ ### 2. 4小时长期数据                                                                                                        │
│ - **移动平均线**：20期 EMA vs 50期 EMA                                                                                      │
│ - **波动率指标**：ATR (3-period 和 14-period)                                                                               │
│ - **技术指标**：MACD 和 RSI（4小时级别）                                                                                    │
│ - **交易量**：当前交易量 vs 平均交易量                                                                                      │
│                                                                                                                             │
│ ### 3. 永续合约数据                                                                                                         │
│ - **开放利息**：Latest 和 Average                                                                                           │
│ - **资金费率**：Funding Rate                                                                                                │
│                                                                                                                             │
│ ## 安装与使用                                                                                                               │
│                                                                                                                             │
│ ### 1. 安装依赖                                                                                                             │
│                                                                                                                             │
│ ```bash                                                                                                                     │
│ pip install -r requirements.txt                                                                                             │
│ ```                                                                                                                         │
│                                                                                                                             │
│ ### 2. 配置                                                                                                                 │
│                                                                                                                             │
│ 编辑 `config.py` 文件，设置：                                                                                               │
│ - 交易所 API 配置                                                                                                           │
│ - 数据更新间隔                                                                                                              │
│ - 数据库路径                                                                                                                │
│ - 交易品种列表                                                                                                              │
│                                                                                                                             │
│ ### 3. 运行                                                                                                                 │
│                                                                                                                             │
│ ```bash                                                                                                                     │
│ python main.py                                                                                                              │
│ ```                                                                                                                         │
│                                                                                                                             │
│ ## 项目结构                                                                                                                 │
│                                                                                                                             │
│ ```                                                                                                                         │
│ nof1/                                                                                                                       │
│ ├── README.md              # 项目文档                                                                                       │
│ ├── requirements.txt       # Python 依赖                                                                                    │
│ ├── config.py              # 配置文件                                                                                       │
│ ├── main.py               # 主程序                                                                                          │
│ ├── data_fetcher.py       # 数据获取模块                                                                                    │
│ ├── indicators.py         # 技术指标计算                                                                                    │
│ ├── database.py           # 数据库操作                                                                                      │
│ └── scheduler.py          # 定时任务调度                                                                                    │
│ ```                                                                                                                         │
│                                                                                                                             │
│ ## API 参考                                                                                                                 │
│                                                                                                                             │
│ ### DataFetcher                                                                                                             │
│                                                                                                                             │
│ 主要的数据获取类。                                                                                                          │
│                                                                                                                             │
│ ```python                                                                                                                   │
│ from data_fetcher import DataFetcher                                                                                        │
│                                                                                                                             │
│ # 初始化                                                                                                                    │
│ fetcher = DataFetcher()                                                                                                     │
│                                                                                                                             │
│ # 获取 K 线数据                                                                                                             │
│ klines = fetcher.get_klines('BTCUSDT', '3m', limit=50)                                                                      │
│                                                                                                                             │
│ # 获取技术指标                                                                                                              │
│ indicators = fetcher.calculate_all_indicators(klines)                                                                       │
│                                                                                                                             │
│ # 获取完整市场数据                                                                                                          │
│ market_data = fetcher.get_market_data('BTCUSDT')                                                                            │
│ ```                                                                                                                         │
│                                                                                                                             │
│ ### 计算的技术指标                                                                                                          │
│                                                                                                                             │
│ - **EMA (20-period)**: 指数移动平均线                                                                                       │
│ - **MACD**: 移动平均收敛散度                                                                                                │
│   - MACD Line                                                                                                               │
│   - Signal Line                                                                                                             │
│   - Histogram                                                                                                               │
│ - **RSI (7-period, 14-period)**: 相对强弱指数                                                                               │
│ - **ATR (3-period, 14-period)**: 平均真实波幅                                                                               │
│ - **交易量分析**: 当前 vs 平均                                                                                              │
│                                                                                                                             │
│ ### 数据格式                                                                                                                │
│                                                                                                                             │
│ 根据 Nof1 Alpha Arena 的数据格式：                                                                                          │
│                                                                                                                             │
│ ```json                                                                                                                     │
│ {                                                                                                                           │
│     "symbol": "BTC",                                                                                                        │
│     "timestamp": "2025-10-19 10:10:00",                                                                                     │
│     "current_price": 107982.5,                                                                                              │
│     "intraday": {                                                                                                           │
│         "prices": [107726.5, 107741.0, ...],                                                                                │
│         "ema20": [107540.298, 107556.175, ...],                                                                             │
│         "macd": [10.802, 21.816, ...],                                                                                      │
│         "rsi_7": [73.026, 71.971, ...],                                                                                     │
│         "rsi_14": [59.393, 59.004, ...]                                                                                     │
│     },                                                                                                                      │
│     "long_term": {                                                                                                          │
│         "ema_20": 107854.332,                                                                                               │
│         "ema_50": 110571.164,                                                                                               │
│         "atr_3": 557.797,                                                                                                   │
│         "atr_14": 1145.893,                                                                                                 │
│         "volume_current": 5.495,                                                                                            │
│         "volume_average": 5047.135,                                                                                         │
│         "macd": [-1914.209, -1853.793, ...],                                                                                │
│         "rsi_14": [35.766, 37.705, ...]                                                                                     │
│     },                                                                                                                      │
│     "perp_data": {                                                                                                          │
│         "open_interest_latest": 25458.85,                                                                                   │
│         "open_interest_average": 25461.32,                                                                                  │
│         "funding_rate": 8.2948e-06                                                                                          │
│     }                                                                                                                       │
│ }                                                                                                                           │
│ ```                                                                                                                         │
│                                                                                                                             │
│ ## 配置说明                                                                                                                 │
│                                                                                                                             │
│ ### config.py                                                                                                               │
│                                                                                                                             │
│ ```python                                                                                                                   │
│ # 数据更新间隔（秒）                                                                                                        │
│ UPDATE_INTERVAL = 180  # 3分钟                                                                                              │
│                                                                                                                             │
│ # 数据库配置                                                                                                                │
│ DATABASE_PATH = "market_data.db"                                                                                            │
│                                                                                                                             │
│ # 交易品种                                                                                                                  │
│ SYMBOLS = [                                                                                                                 │
│     'BTCUSDT',                                                                                                              │
│     'ETHUSDT',                                                                                                              │
│     'SOLUSDT',                                                                                                              │
│     'BNBUSDT',                                                                                                              │
│     'DOGEUSDT',                                                                                                             │
│     'XRPUSDT'                                                                                                               │
│ ]                                                                                                                           │
│                                                                                                                             │
│ # 时间间隔                                                                                                                  │
│ INTERVALS = {                                                                                                               │
│     'intraday': '3m',                                                                                                       │
│     'long_term': '4h'                                                                                                       │
│ }                                                                                                                           │
│ ```                                                                                                                         │
│                                                                                                                             │
│ ## 未来计划                                                                                                                 │
│                                                                                                                             │
│ - [ ] 支持更多交易所（Hyperliquid, OKX, Bybit）                                                                             │
│ - [ ] 添加更多技术指标                                                                                                      │
│ - [ ] 实现 WebSocket 实时数据推送                                                                                           │
│ - [ ] 添加数据可视化                                                                                                        │
│ - [ ] 实现自动交易功能                                                                                                      │
│                                                                                                                             │
│ ## 参考资料                                                                                                                 │
│                                                                                                                             │
│ - [Nof1 Alpha Arena](https://nof1.ai)                                                                                       │
│ - [Binance API 文档](https://binance-docs.github.io/apidocs/spot/en/)                                                       │
│ - [pandas-ta 技术指标库](https://github.com/twopirllc/pandas-ta)                                                            │
│                                                                                                                             │
│ ## 许可证                                                                                                                   │
│                                                                                                                             │
│ MIT License
