# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Python 3 cryptocurrency market data acquisition and analysis system** (Nof1 数据获取系统), inspired by Nof1 Alpha Arena. It fetches, stores, and analyzes cryptocurrency market data with automated scheduling.

**Key Features:**
- Multi-exchange data fetching (currently Binance via CCXT)
- Real-time market data acquisition (OHLCV K-line data)
- Technical indicator calculations (EMA, MACD, RSI, ATR, Volume)
- Perpetual futures data (funding rates, open interest)
- SQLite database persistence
- Automated scheduled data updates (default: every 3 minutes)

## Common Commands

### Setup
```bash
pip install -r requirements.txt
```

### Running the Application
```bash
# Get single symbol data
python main.py --symbol BTCUSDT

# Get multiple symbols
python main.py --symbols BTCUSDT ETHUSDT SOLUSDT

# Start automated scheduler
python main.py --schedule

# Start scheduler with custom settings
python main.py --schedule --symbols BTCUSDT ETHUSDT --interval 60

# Query database
python main.py --query --symbols BTCUSDT

# Show system status
python main.py --status
```

### Direct Module Execution
```bash
python scheduler.py  # Run scheduler standalone
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
| **data_fetcher.py** (354 lines) | Data acquisition engine | CCXT exchange integration (Binance), OHLCV retrieval, multi-timeframe support (3m, 4h) |
| **database.py** (334 lines) | SQLite operations | K-line storage (3m, 4h), indicators storage, perpetuals data storage, data retrieval |
| **indicators.py** (200 lines) | Technical analysis | EMA (20-period), MACD, RSI (7, 14), ATR (3, 14), Volume analysis |
| **scheduler.py** (154 lines) | Task scheduling | Periodic updates, background tasks, error handling |
| **config.py** (56 lines) | Configuration | Update intervals, database path, trading symbols, indicator parameters |

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
    "symbol": "BTC",
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
The SQLite database (`market_data.db`) stores:
- **K-line data**: 3-minute and 4-hour OHLCV candles
- **Technical indicators**: Pre-calculated EMA, MACD, RSI, ATR values
- **Perpetual futures data**: Funding rates and open interest
- **Historical data**: Supports retrieval via database queries

## Exchange Integration

**Current**: Binance via CCXT library (extensible to other exchanges)

**API Requirements**: Configure exchange API credentials in environment variables (supports python-dotenv)

## Dependencies

Key packages from `requirements.txt`:
- `ccxt>=4.0.0` - Cryptocurrency exchange integration
- `pandas>=2.0.0` - Data manipulation
- `pandas-ta>=0.3.14b` - Technical indicators
- `numpy>=1.24.0` - Numerical computing
- `schedule>=1.2.0` - Task scheduling
- `requests>=2.31.0` - HTTP requests
- `python-dotenv>=1.0.0` - Environment variables

## Important Notes

1. **Not a Git Repository**: The codebase is not initialized with git
2. **No Tests**: No testing infrastructure (pytest/unittest) present
3. **No Containerization**: No Docker or Docker Compose configuration
4. **Logging**: Outputs to both console and `nof1.log` file
5. **Extensible Design**: Designed to easily add more exchanges through CCXT
6. **Research Reference**: Includes `source.html` with research on LLM trading experiments (not functional code)

## Future Roadmap (from README)

- [ ] Support more exchanges (Hyperliquid, OKX, Bybit)
- [ ] Add more technical indicators
- [ ] Implement WebSocket for real-time data push
- [ ] Add data visualization
- [ ] Implement automated trading functionality

## References

- [Nof1 Alpha Arena](https://nof1.ai)
- [Binance API Documentation](https://binance-docs.github.io/apidocs/spot/en/)
- [pandas-ta Technical Indicators Library](https://github.com/twopirllc/pandas-ta)
