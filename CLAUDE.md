# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **comprehensive LLM-powered cryptocurrency trading system** that combines market data analysis with AI-driven decision making. The system implements a multi-phase architecture with parallel LLM processing (DeepSeek + Qwen3), risk management, backtesting, and real-time performance monitoring.

**Key Features:**
- **Multi-timeframe data analysis** (4h trend + 3m timing)
- **Parallel LLM decision making** (DeepSeek + Qwen3)
- **Intelligent decision caching** to reduce API costs
- **Binance Testnet real trading** with virtual funds (10,000 USDT)
- **Unified launcher** (nof1.py) for all operations
- **Real trading executor** with market/limit/stop orders
- **API server** (FastAPI) for real-time monitoring
- **HTML dashboard** (trading_dashboard.html) with auto-refresh
- **Risk assessment and position sizing**
- **Historical backtesting engine**
- **Real-time performance monitoring**
- **Automated 5-minute decision cycles**
- **Complete test suite and documentation**

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
├── README.md                     # Main project documentation
├── CLAUDE.md                     # AI developer guide (this file)
├── QUICKSTART.md                 # Quick start guide
├── QUICKSTART_TESTNET.md         # Testnet quick start (NEW)
├── INSTALL.md                    # Installation instructions
├── DATABASE_GUIDE.md             # Database viewing guide
├── PROJECT_SUMMARY.md            # Project implementation summary
├── requirements.txt              # Python dependencies
├── nof1.py                       # Unified launcher (RECOMMENDED)
├── run_full_system.py            # Core trading system (uses Testnet)
├── run_api.py                    # API server launcher
├── config.py                     # Configuration file (enhanced with Testnet)
├── main.py                       # Legacy CLI entry point
├── data_fetcher.py              # Data acquisition module (Testnet support)
├── indicators.py                # Technical indicators (pure pandas)
├── database.py                  # SQLite database operations
├── scheduler.py                 # Legacy task scheduler
├── testnet_demo.py              # Testnet integration test
├── testnet_viewer.py            # View Testnet positions/trades
├── trading_dashboard.html       # Real-time monitoring dashboard
├── test_basic.py                # Basic functionality tests
├── run_tests.py                 # Test runner
├── demo.py                      # System demonstration
├── quick_query.py               # Quick database queries
├── view_database.py             # Interactive database viewer
├── demo_database.py             # Database demo tool
├── llm_clients/                 # LLM client modules
│   ├── __init__.py
│   ├── llm_factory.py
│   ├── deepseek_client.py
│   └── qwen_client.py
├── models/                      # Data models
│   ├── __init__.py
│   └── trading_decision.py      # Trading decision model
├── trading/                     # Trading modules
│   ├── __init__.py
│   ├── paper_trader.py          # Paper trading simulator (legacy)
│   └── real_trader.py           # Real trading executor (Testnet/Live)
├── scheduling/                  # Scheduling modules
│   ├── __init__.py
│   ├── high_freq_scheduler.py
│   └── decision_cache.py
├── risk_management/             # Risk management
│   ├── __init__.py
│   ├── backtest_engine.py
│   └── risk_manager.py
├── monitoring/                  # Performance monitoring
│   ├── __init__.py
│   └── performance_monitor.py
├── api/                         # API service
│   ├── __init__.py
│   └── main.py
├── docs/                        # Documentation
│   ├── user/                    # User guides
│   │   ├── README.md
│   │   ├── QUICKSTART.md
│   │   ├── INSTALL.md
│   │   ├── API_DOCUMENTATION.md
│   │   └── TESTNET_INTEGRATION.md  # Testnet guide (NEW)
│   ├── archive/                 # Archive docs
│   ├── dev/                     # Developer docs
│   └── project/                 # Project docs (CLAUDE.md moved to root)
└── tests/                       # Test directory
    ├── __init__.py
    ├── test_config.py
    ├── test_indicators.py
    ├── test_database.py
    ├── test_data_fetcher.py
    ├── test_scheduler.py
    ├── test_integration.py
    ├── test_llm_clients.py
    ├── test_paper_trader.py
    ├── test_decision_cache.py
    ├── test_risk_manager.py
    ├── test_performance_monitor.py
    ├── test_multi_timeframe_preprocessor.py
    ├── test_integration_complete.py
    └── run_tests.py
```

## Configuration (Binance Testnet)

### Getting Testnet API Keys
1. Visit: https://testnet.binance.vision/
2. Login with GitHub account (recommended)
3. Copy the displayed API Key and Secret Key
4. Testnet provides virtual funds: 10,000+ USDT, 1+ BTC, etc.

### Environment Variables (.env file)
Create a `.env` file in the project root:
```bash
TESTNET_API_KEY=your_testnet_api_key_here
TESTNET_SECRET_KEY=your_testnet_secret_key_here
USE_TESTNET=true
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
