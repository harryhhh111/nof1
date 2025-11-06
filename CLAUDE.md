# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🔒 Handling Access Restrictions

### When Websites Block Direct Access

Some websites (especially financial/exchange platforms like Binance) actively block automated requests from unknown sources. If direct `WebFetch` fails:

**Error Example:**
```
Claude Code is unable to fetch from https://developers.binance.com/...
```

**Solutions:**

1. **Use MCP Web Fetch Tool** (Recommended for Binance/exchange documentation)
```python
# Search for the documentation first
mcp__web_search.search_query = "binance demo trading API documentation site:binance.com"

# Then fetch specific pages
WebFetch(url="...", prompt="Extract technical details about base URL, authentication, and configuration")
```

2. **Alternative Access Methods**
   - Use search engines to find cached versions
   - Look for mirror sites or GitHub mirrors
   - Access via alternative search indices

3. **For Binance Specifically**
   - Use GitHub mirrors: https://github.com/binance/binance-spot-api-docs
   - Use community documentation
   - Check CCXT library documentation for integration examples

## 🔧 交易模块抽象（工厂模式）

### 概述

系统现在使用抽象工厂模式来支持多种交易模式，可以轻松切换不同的交易环境而无需修改业务逻辑。

### 支持的交易模式

| 模式 | 类型 | 描述 | 风险级别 |
|------|------|------|----------|
| **paper** | 纸交易 | 纯模拟交易，不调用真实API | 🟢 无风险 |
| **testnet** | Testnet | Binance Testnet API (testnet.binance.vision) | 🟢 无风险 |
| **demo** | Demo Trading | Binance Demo Trading API (demo-api.binance.com) | 🟢 无风险 |
| **live** | 实盘 | 真实Binance API | 🔴 高风险 |

### 交易工厂使用

```python
from trading.trading_factory import TradingFactory
from models.trading_decision import TradingDecision

# 1. 创建交易器（自动根据配置选择模式）
trader = TradingFactory.create_trader()

# 2. 或指定特定模式
paper_trader = TradingFactory.create_trader('paper')
testnet_trader = TradingFactory.create_trader('testnet')
demo_trader = TradingFactory.create_trader('demo')
live_trader = TradingFactory.create_trader('live')

# 3. 使用统一的接口
balance = trader.get_account_balance()
price = trader.get_symbol_price('BTCUSDT')

# 4. 下订单
result = trader.place_market_order('BTCUSDT', 'buy', 0.001, "买入测试")

# 5. 执行交易决策
decision = TradingDecision(
    action="BUY",
    confidence=75.0,
    entry_price=price,
    stop_loss=price * 0.95,
    take_profit=price * 1.10,
    position_size=5.0,
    risk_level="MEDIUM",
    reasoning="测试决策",
    timeframe="4h",
    symbol="BTCUSDT"
)

result = trader.execute_decision(decision)

# 6. 清理资源
trader.close()
```

### 核心类

- **`TradingInterface`**: 抽象交易接口，定义所有交易器必须实现的方法
- **`TradingFactory`**: 工厂类，根据配置创建对应的交易器实例
- **`TestnetTrader`**: Testnet交易器实现
- **`DemoTrader`**: Demo Trading交易器实现
- **`PaperTraderImpl`**: 纸交易模拟器实现

### 模式切换

只需修改配置即可切换交易模式：

```python
# 在 config.py 中
USE_TESTNET = True  # 使用 testnet
CURRENT_MODE = 'testnet'

# 或
USE_TESTNET = False  # 使用 demo 或 live
CURRENT_MODE = 'demo'  # 或 'paper' 或 'live'
```

### 优劣势对比

#### Paper Trading
- ✅ 无需API Key
- ✅ 无网络依赖
- ✅ 快速测试
- ❌ 价格可能有延迟
- ❌ 无法测试真实网络情况

#### Testnet Trading
- ✅ 真实API调用
- ✅ 虚拟资金
- ✅ 完整交易功能
- ❌ 需要配置API Key
- ❌ 可能受网络限制

#### Demo Trading
- ✅ 统一现货+期货环境
- ✅ 初始资金充足
- ❌ 当前网络不可达
- ❌ 需要API Key

### 测试脚本

运行交易工厂测试：
```bash
python3 tests/demo_trading/test_trading_factory.py
```

这将测试所有交易模式并显示性能摘要。

## Project Overview

This is a **comprehensive LLM-powered cryptocurrency trading system** that combines market data analysis with AI-driven decision making. The system implements a multi-phase architecture with parallel LLM processing (DeepSeek + Qwen3), risk management, backtesting, and real-time performance monitoring.

**Key Features:**
- **Multi-timeframe data analysis** (4h trend + 3m timing)
- **Parallel LLM decision making** (DeepSeek + Qwen3)
- **Intelligent decision caching** to reduce API costs
- **Binance Testnet real trading** with virtual funds (10,000 USDT)
- **Robust startup script** (start_nof1.sh) - resistant to disconnections
- **Unified launcher** (nof1.py) for all operations
- **Real trading executor** with market/limit/stop orders
- **FastAPI server** for real-time monitoring (port 8000)
- **HTML dashboard** (trading_dashboard.html) with auto-refresh
- **Complete database tools** (quick_query, view_database, demo_database)
- **Risk assessment and position sizing**
- **Real-time performance monitoring**
- **Automated 5-minute decision cycles**
- **Complete test suite** (95%+ coverage, 92 test cases)
- **Comprehensive documentation** (user guides, API docs, dev guides)

**⚠️ IMPORTANT**:
- The system uses **Binance Testnet** (real API, virtual funds) for trading, not paper trading
- Decisions are executed via `RealTrader` which interacts with the actual Binance Testnet API
- Users must configure their own Testnet API keys from https://testnet.binance.vision/
- Always test thoroughly in Testnet mode before considering live trading

## Common Commands

### Setup
```bash
pip install -r requirements.txt
```

### Unified Launcher (Recommended)
```bash
# Run trading system for specified hours (uses Binance Testnet)
python3 nof1.py --run 2              # Run for 2 hours
python3 nof1.py --run 0.5            # Run for 30 minutes

# Start API server only
python3 nof1.py --api                # Start API on port 8000

# View current results
python3 nof1.py --view               # View decisions and positions

# Run integration test
python3 nof1.py --test               # Test Binance Testnet integration

# Quick start workflow
python3 nof1.py --run 2 && python3 nof1.py --view
```

### Robust Startup Script (Production-Ready)
```bash
# Production-grade startup with process management
./start_nof1.sh start 2              # Run for 2 hours (background, disconnection-resistant)

# System management
./start_nof1.sh status               # View system status
./start_nof1.sh stop                 # Stop all services gracefully
./start_nof1.sh restart              # Restart system
./start_nof1.sh logs                 # View logs

# Advanced usage
./start_nof1.sh start-api            # Start API server only
./start_nof1.sh start 24             # Run for 24 hours
./start_nof1.sh cleanup              # Clean old logs (7+ days)

# Monitor in real-time
tail -f logs/trading_*.log           # Follow trading logs
```
**Why start_nof1.sh?**
- ✅ **Disconnection-resistant**: Uses `setsid` + `nohup` to survive terminal close
- ✅ **Process management**: PID files prevent duplicate runs
- ✅ **Graceful shutdown**: Stops services properly without force-kill
- ✅ **Log separation**: Individual log files for each component
- ✅ **Auto-recovery**: Cleans up stale PID files automatically

### Legacy Commands
```bash
# Get single symbol data
python3 main.py --symbol BTCUSDT

# Get multiple symbols
python3 main.py --symbols BTCUSDT ETHUSDT SOLUSDT

# Start automated scheduler
python3 main.py --schedule

# Query database
python3 main.py --query --symbols BTCUSDT

# Show system status
python3 main.py --status
```

### Binance Testnet Trading
```bash
# Testnet integration test
python3 testnet_demo.py

# View Testnet positions and trades
python3 testnet_viewer.py

# Real-time monitoring (open in browser)
firefox trading_dashboard.html

# View Testnet in web interface
# Visit: https://testnet.binance.vision/
```

### API Server (Port 8000)
```bash
# API documentation
curl http://localhost:8000/docs

# Health check
curl http://localhost:8000/api/v1/health

# Get decisions
curl http://localhost:8000/api/v1/decisions?limit=100

# Get statistics
curl http://localhost:8000/api/v1/stats/summary
```

### Database Viewing (NEW)

**Quick Query:**
```bash
python3 quick_query.py summary      # Database overview
python3 quick_query.py latest       # Latest data
python3 quick_query.py indicators   # Technical indicators
python3 quick_query.py klines       # K-line data
python3 quick_query.py perp         # Perpetual futures data
python3 quick_query.py symbols      # All trading symbols
```

**Interactive Viewer:**
```bash
python3 view_database.py            # Interactive database browser
```

**Database Demo & Examples:**
```bash
python3 demo_database.py            # Demo with sample data and queries
```

### Binance Testnet (NEW)

**Setup:**
```bash
# 1. Get API Key from https://testnet.binance.vision/
# 2. Set environment variables
export TESTNET_API_KEY="your_api_key"
export TESTNET_SECRET_KEY="your_secret_key"
export USE_TESTNET="true"

# 3. Run Testnet demo
python3 testnet_demo.py
```

**Testnet Trading:**
```python
from trading.real_trader import RealTrader
from models.trading_decision import TradingDecision

trader = RealTrader()

# Check balance
balance = trader.get_account_balance()

# Place orders
result = trader.place_market_order('BTCUSDT', 'buy', 0.001)
result = trader.place_limit_order('BTCUSDT', 'buy', 0.001, 68000)

# Execute trading decision
decision = TradingDecision(
    action="BUY",
    confidence=80.0,
    entry_price=70000,
    stop_loss=68600,
    take_profit=72800,
    position_size=10.0,
    risk_level="MEDIUM",
    reasoning="Test analysis",
    timeframe="4h",
    symbol="BTCUSDT"
)
result = trader.execute_decision(decision)

trader.close()
```

**Mode Switching:**
```python
# In config.py
USE_TESTNET = True   # Testnet mode (paper trading with real API)
USE_TESTNET = False  # Live trading mode (real money!)
```

### Testing
```bash
# Run basic functionality tests
python3 test_basic.py

# Run full test suite
python3 run_tests.py
```

### Direct Module Execution
```bash
python3 scheduler.py  # Run scheduler standalone
```

## Architecture

### Module Structure
The system follows a modular architecture:

```
┌─────────────────┐
│   main.py       │  ← CLI Interface (argparse entry point)
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
    │   database.py    │  ← SQLite storage
    └──────────────────┘
```

### Core Modules

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| **main.py** (275 lines) | CLI entry point | Single/multiple symbol fetching, database queries, scheduler management, status display |
| **data_fetcher.py** (360+ lines) | Data acquisition engine | CCXT exchange integration (Binance), OHLCV retrieval, multi-timeframe support (3m, 4h), Testnet support |
| **database.py** (334 lines) | SQLite operations | K-line storage (3m, 4h), indicators storage, perpetuals data storage, data retrieval |
| **indicators.py** (200+ lines) | Technical analysis | EMA (20-period), MACD, RSI (7, 14), ATR (3, 14), Volume analysis - **Pure pandas implementation** |
| **scheduler.py** (154 lines) | Task scheduling | Periodic updates, background tasks, error handling |
| **config.py** (100+ lines) | Configuration | Update intervals, database path, trading symbols, indicator parameters, Testnet settings |
| **trading/real_trader.py** (600+ lines) | Real trading executor | Market/limit/stop orders, account balance, order management, position tracking |
| **models/trading_decision.py** (210 lines) | Trading decision model | Decision validation, risk assessment, position sizing |

### Database Viewing Tools (NEW)

| Tool | Purpose | Usage |
|------|---------|-------|
| **quick_query.py** | Quick database queries | `python3 quick_query.py [summary/latest/indicators/klines/perp/symbols]` |
| **view_database.py** | Interactive browser | `python3 view_database.py` |
| **demo_database.py** | Demo & examples | `python3 demo_database.py` |

## Configuration (config.py)

### Key Settings
```python
UPDATE_INTERVAL = 180  # 3 minutes default
DATABASE_PATH = "market_data.db"

SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'DOGEUSDT', 'XRPUSDT']

INTERVALS = {
    'intraday': '3m',   # Short-term data (10 historical points)
    'long_term': '4h'   # Long-term data
}

INDICATOR_PARAMS = {
    'ema_short': 20,
    'ema_long': 50,
    'rsi_short': 7,
    'rsi_long': 14,
    'atr_short': 3,
    'atr_long': 14
}
```

### Technical Indicator Parameters
- **EMA**: 20-period (intraday), 20 & 50 period (long-term)
- **RSI**: 7 & 14 periods (intraday), 14 period (long-term)
- **ATR**: 3 & 14 periods (long-term)
- **MACD**: Applied to both intraday and long-term data

## Data Structures

### Output Format
The system outputs JSON data matching Nof1 Alpha Arena format:

```json
{
    "symbol": "BTCUSDT",
    "timestamp": "2025-10-19 10:10:00",
    "current_price": 107982.5,
    "intraday": {
        "prices": [...],
        "ema20": [...],
        "macd": [...],
        "rsi_7": [...],
        "rsi_14": [...]
    },
    "long_term": {
        "ema_20": 107854.332,
        "ema_50": 110571.164,
        "atr_3": 557.797,
        "atr_14": 1145.893,
        "volume_current": 5.495,
        "volume_average": 5047.135,
        "macd": [...],
        "rsi_14": [...]
    },
    "perp_data": {
        "open_interest_latest": 25458.85,
        "open_interest_average": 25461.32,
        "funding_rate": 8.2948e-06
    }
}
```

### Database Schema
The SQLite database (`market_data.db`) contains 4 main tables:

1. **klines_3m** - 3-minute OHLCV K-line data
   - Fields: symbol, timestamp, open, high, low, close, volume, close_time

2. **klines_4h** - 4-hour OHLCV K-line data
   - Fields: symbol, timestamp, open, high, low, close, volume, close_time

3. **technical_indicators** - Pre-calculated technical indicators
   - Fields: symbol, timestamp, timeframe, ema_20, ema_50, macd, rsi_7, rsi_14, atr_3, atr_14, current_volume, average_volume

4. **perpetual_data** - Perpetual futures data
   - Fields: symbol, timestamp, open_interest_latest, open_interest_average, funding_rate

### Database Viewing Examples

**Using quick_query.py:**
```bash
# View database summary
python3 quick_query.py summary

# View latest technical indicators
python3 quick_query.py indicators
```

**Using view_database.py (interactive):**
```bash
python3 view_database.py
# Then select:
#   1. View database overview
#   2. Custom SQL query
```

**Direct database queries:**
```python
from database import Database
db = Database()
data = db.get_latest_data('BTCUSDT')
print(data)
```

**SQLite command line:**
```bash
sqlite3 market_data.db
.tables
SELECT * FROM klines_3m LIMIT 5;
.quit
```

## Exchange Integration

**Current**: Binance via CCXT library (extensible to other exchanges)

**API Requirements**: Configure exchange API credentials in environment variables (supports python-dotenv)
- No authentication required for public market data
- Add `BINANCE_API_KEY` and `BINANCE_SECRET_KEY` to `.env` for private endpoints

## Dependencies

Key packages from `requirements.txt`:
- `ccxt>=4.0.0` - Cryptocurrency exchange integration
- `pandas>=2.0.0` - Data manipulation
- `numpy>=1.24.0` - Numerical computing (NO LONGER uses pandas-ta)
- `schedule>=1.2.0` - Task scheduling
- `requests>=2.31.0` - HTTP requests
- `python-dotenv>=1.0.0` - Environment variables

**Note**: Technical indicators are implemented using **pure pandas** (no pandas-ta dependency) for better control and reliability.

## 🔄 版本控制要求

### ⚠️ 重要：每次更新必须推送GitHub

**所有代码、文档、配置更新必须立即推送到GitHub**，不得在本地未提交状态过夜。

### Git工作流程
```bash
# 1. 添加所有更改
git add .

# 2. 提交更改（包含详细说明）
git commit -m "$(cat << 'EOF'
📚 docs: 更新所有文档以反映项目最新状态

- 更新CLAUDE.md：添加Robust启动脚本信息
- 更新README.md：重新组织，突出核心特性
- 新增DATABASE_GUIDE.md：完整数据库使用指南
- 更新QUICKSTART_TESTNET.md：添加最佳实践
- 更新docs/user/*：补充启动脚本和使用说明
- 强调start_nof1.sh作为推荐启动方式

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"

# 3. 推送到GitHub
git push origin main

# 4. 验证推送成功
git status
```

### 提交消息规范
- **格式**: `type(scope): description`
- **类型**:
  - `docs` - 文档更新
  - `feat` - 新功能
  - `fix` - 错误修复
  - `refactor` - 代码重构
  - `test` - 测试相关
- **示例**:
  - `docs: 更新快速开始指南`
  - `feat: 新增Testnet交易功能`
  - `fix: 修复数据获取模块错误`

### ❌ 禁止的行为
- ❌ 在本地保留未提交的更改过夜
- ❌ 一次性提交过多不相关的更改
- ❌ 使用无意义的提交消息（如"update", "fix", "asdf"）
- ❌ 提交敏感信息（API密钥、密码等）

### ✅ 强制要求
- ✅ 每次文档更新后立即推送
- ✅ 代码修改后立即推送
- ✅ 配置变更后立即推送
- ✅ 提交消息必须清晰描述更改内容
- ✅ 大型更改分多次提交，便于追踪

## Testing Infrastructure

### Test Suite
Complete testing infrastructure with:
- **Unit tests** for all modules
- **Integration tests** for end-to-end workflows
- **Basic functionality tests** for quick verification

### Running Tests
```bash
# Basic functionality test
python3 test_basic.py

# Full test suite
python3 run_tests.py

# Using pytest (requires installation)
pip install pytest
pytest tests/ -v
```

### Test Files
- `tests/test_config.py` - Configuration tests
- `tests/test_indicators.py` - Technical indicators tests
- `tests/test_database.py` - Database operations tests
- `tests/test_data_fetcher.py` - Data fetching tests
- `tests/test_scheduler.py` - Scheduler tests
- `tests/test_integration.py` - Integration tests

### Testnet Testing
- `testnet_demo.py` - Complete Testnet integration test script
- `QUICKSTART_TESTNET.md` - 5-minute quick start guide
- `docs/user/TESTNET_INTEGRATION.md` - Comprehensive Testnet documentation

## Important Notes

1. **Git Repository**: Initialized with git, hosted on GitHub
2. **Complete Test Suite**: 6 test files with unit and integration tests
3. **No Containerization**: No Docker or Docker Compose configuration
4. **Logging**: Outputs to both console and `nof1.log` file
5. **Extensible Design**: Designed to easily add more exchanges through CCXT
6. **Database Tools**: Multiple tools for viewing and querying database (quick_query.py, view_database.py, demo_database.py)
7. **Documentation**: Comprehensive docs (README.md, CLAUDE.md, QUICKSTART.md, INSTALL.md, DATABASE_GUIDE.md)
8. **Technical Indicators**: Pure pandas implementation (not pandas-ta)

## File Structure

```
nof1/
├── 📄 Core Documentation
│   ├── README.md                     # Main project documentation
│   ├── CLAUDE.md                     # AI developer guide (this file)
│   ├── QUICKSTART.md                 # Quick start guide
│   ├── QUICKSTART_TESTNET.md         # Testnet quick start
│   ├── ROBUST_STARTUP.md             # Robust startup guide (抗断连)
│   ├── PROJECT_SUMMARY.md            # Project implementation summary
│   ├── DEMO_TRADING_UPGRADE.md       # Demo Trading upgrade guide ⭐
│   ├── DEMO_TRADING_MIGRATION_REPORT.md # Migration report ⭐
│   ├── DEMO_TRADING_INITIAL_FUNDS.md # Initial funds guide ⭐
│   └── requirements.txt              # Python dependencies
│
├── 🚀 Startup Scripts
│   ├── nof1.py                       # Unified launcher
│   ├── start_nof1.sh                 # Robust startup script (抗断连) ⭐
│   ├── run_full_system.py            # Core trading system (uses Testnet)
│   └── run_api.py                    # API server launcher
│
├── 🔧 Core Modules
│   ├── config.py                     # Configuration file (Testnet ready)
│   ├── main.py                       # Legacy CLI entry point
│   ├── data_fetcher.py              # Data acquisition (CCXT + Testnet)
│   ├── indicators.py                # Technical indicators (pure pandas)
│   ├── database.py                  # SQLite database operations
│   ├── scheduler.py                 # Legacy task scheduler
│   ├── prompt_generator.py          # LLM prompt generator
│   └── multi_timeframe_preprocessor.py  # Multi-timeframe analysis
│
├── 🧪 Testing & Demo
│   ├── testnet_demo.py              # Testnet integration test ⭐
│   ├── testnet_viewer.py            # View Testnet positions/trades
│   ├── testnet_trade_demo.py        # Trade execution demo
│   ├── demo_trading_test.py         # Demo Trading integration test ⭐
│   ├── demo_quick_test.py           # Quick Demo Trading verification ⭐
│   ├── check_initial_funds.py       # Check Demo Trading initial funds ⭐
│   ├── test_basic.py                # Basic functionality tests
│   ├── run_tests.py                 # Test runner
│   └── demo.py                      # System demonstration
│
├── 🗄️ Database Tools
│   ├── quick_query.py               # Quick database queries ⭐
│   ├── view_database.py             # Interactive database viewer ⭐
│   ├── demo_database.py             # Database demo tool ⭐
│   ├── market_data.db               # Market data (3m, 4h, indicators)
│   ├── performance_monitor.db       # Trading metrics
│   └── real_trading.db              # Real trading records
│
├── 🤖 LLM Clients
│   ├── llm_clients/
│   │   ├── __init__.py
│   │   ├── llm_factory.py           # LLM factory (DeepSeek + Qwen3)
│   │   ├── deepseek_client.py
│   │   └── qwen_client.py
│   └── models/
│       ├── __init__.py
│       └── trading_decision.py      # Trading decision model
│
├── 💰 Trading
│   ├── trading/
│   │   ├── __init__.py
│   │   ├── real_trader.py           # Real trading executor (Binance Testnet) ⭐
│   │   └── paper_trader.py          # Paper trading simulator (legacy)
│   └── trading_dashboard.html       # Real-time monitoring dashboard
│
├── ⚙️ System Components
│   ├── scheduling/                  # Scheduling modules
│   │   ├── __init__.py
│   │   ├── high_freq_scheduler.py
│   │   └── decision_cache.py
│   ├── risk_management/             # Risk management
│   │   ├── __init__.py
│   │   ├── backtest_engine.py
│   │   └── risk_manager.py
│   ├── monitoring/                  # Performance monitoring
│   │   ├── __init__.py
│   │   └── performance_monitor.py
│   └── api/                         # FastAPI service
│       └── main.py
│
├── 📚 Documentation
│   ├── docs/
│   │   ├── user/                    # User guides
│   │   │   ├── README.md
│   │   │   ├── QUICKSTART.md
│   │   │   ├── INSTALL.md
│   │   │   ├── API_DOCUMENTATION.md
│   │   │   └── TESTNET_INTEGRATION.md
│   │   ├── dev/                     # Developer docs
│   │   │   └── DEVELOPMENT.md
│   │   └── project/                 # Project docs
│   │
│   ├── logs/                        # Runtime logs
│   └── pids/                        # Process ID files (for start_nof1.sh)
│
└── 🧪 Tests (95%+ Coverage, 92 Tests)
    ├── __init__.py
    ├── test_*.py                    # Individual test files
    ├── test_integration_complete.py # Complete end-to-end test
    ├── test_llm_clients.py          # LLM client tests
    └── run_tests.py                 # Test runner

⭐ = Highly recommended/important files
```

## Configuration (Binance Demo Trading)

### Getting Demo Trading API Keys (Recommended)
1. Visit: https://demo.binance.com/
2. Login with your account
3. Go to API Management: https://demo.binance.com/en/my/settings/api-management
4. Create API Key and Secret Key
5. Enable "Reading" permissions (minimum required)

### Demo Trading Initial Funds
After resetting your Demo Trading account, you will receive:
- **USDT**: 5,000 (main trading asset)
- **BTC**: 0.05 (Bitcoin initial balance)
- **ETH**: 1 (Ethereum initial balance)
- **BNB**: 2 (Binance Coin initial balance)

**Total Initial Value**: ~5,000+ USDT

### Environment Variables (.env file)
Create a `.env` file in the project root:
```bash
# New Demo Trading API (Recommended)
DEMO_API_KEY=your_demo_api_key_here
DEMO_SECRET_KEY=your_demo_secret_key_here

# Old Testnet API (Backward compatibility)
# TESTNET_API_KEY=your_testnet_api_key_here
# TESTNET_SECRET_KEY=your_testnet_secret_key_here

USE_TESTNET=true
```

### Checking Initial Funds
```bash
# Check Demo Trading initial funds
python3 check_initial_funds.py

# View balance in detail
python3 testnet_viewer.py
```

### Trading Mode Selection (config.py)
```python
# Testnet Mode (Recommended for testing)
USE_TESTNET = True
CURRENT_MODE = 'testnet'
# Uses: Real Binance API + Virtual Funds (10,000 USDT)
# Safe to use - no real money involved

# Live Trading Mode (HIGH RISK!)
USE_TESTNET = False
BINANCE_API_KEY = "real_api_key_here"
BINANCE_SECRET_KEY = "real_secret_key_here"
CURRENT_MODE = 'live'
# Uses: Real Binance API + Real Money
# WARNING: Only use after extensive Testnet testing!
```

**⚠️ CRITICAL**:
- Always test in Testnet mode before using real funds!
- Never commit API keys to version control
- Use environment variables or .env files for sensitive data
- Testnet Key ≠ Live Key - they are completely separate

## Status Persistence

**Data Persistence**:
- ✅ **Decision History**: Preserved in `performance_monitor.db`
- ✅ **Market Data**: Preserved in `market_data.db`
- ✅ **Testnet Trades**: Visible at https://testnet.binance.vision/

**State Reset**:
- ❌ **Positions**: Reset on each restart (new RealTrader instance)
- ✅ **Historical Records**: Never reset (database accumulative)

## Future Roadmap

- [x] **COMPLETED**: Binance Testnet integration for real trading simulation
- [x] **COMPLETED**: Real trading executor with market/limit/stop orders
- [x] **COMPLETED**: Unified launcher (nof1.py)
- [x] **COMPLETED**: API server with FastAPI
- [x] **COMPLETED**: HTML dashboard with auto-refresh
- [x] **COMPLETED**: Trading decision model and validation
- [x] **COMPLETED**: Real-time performance monitoring
- [ ] Add more exchanges (Hyperliquid, OKX, Bybit)
- [ ] Add more technical indicators
- [ ] Implement WebSocket for real-time data push
- [ ] Add data visualization
- [ ] Implement automated trading functionality with LLM integration
- [ ] Web dashboard for monitoring and control

## References

- [Nof1 Alpha Arena](https://nof1.ai)
- [Binance API Documentation](https://binance-docs.github.io/apidocs/spot/en/)
- [pandas Documentation](https://pandas.pydata.org/)

## Development Tips

### Adding New Indicators
Edit `indicators.py` and add static methods to the `TechnicalIndicators` class:

```python
@staticmethod
def calculate_new_indicator(data: pd.DataFrame, period: int = 14) -> pd.Series:
    # Implementation using pandas
    return result
```

Then update `calculate_all_indicators()` method to include the new indicator.

### Adding New Exchanges
CCXT already supports 100+ exchanges. To add a new exchange:

1. Update `data_fetcher.py` to accept exchange parameter
2. Add exchange-specific configurations in `config.py`
3. Test with the new exchange's API

### Database Operations
Use the `Database` class methods:
- `insert_klines(symbol, klines, timeframe)`
- `insert_indicators(symbol, timestamp, timeframe, indicators)`
- `insert_perp_data(symbol, timestamp, perp_data)`
- `get_klines(symbol, timeframe, limit)`
- `get_latest_data(symbol)`

### Querying Database
For quick queries, use `quick_query.py`:
```bash
python3 quick_query.py latest    # Latest records from all tables
python3 quick_query.py klines    # K-line data
python3 quick_query.py indicators # Technical indicators
```

For interactive exploration, use `view_database.py`:
```bash
python3 view_database.py
```

For SQL learning and examples, use `demo_database.py`:
```bash
python3 demo_database.py
```

See `DATABASE_GUIDE.md` for comprehensive database documentation.
