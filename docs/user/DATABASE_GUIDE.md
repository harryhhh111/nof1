# Nof1 数据库指南 🗄️

## 📖 概述

Nof1系统使用SQLite数据库存储所有市场数据和交易记录。系统包含3个主要数据库文件：

1. **market_data.db** - 市场数据和技术指标
2. **performance_monitor.db** - 交易性能指标
3. **real_trading.db** - 真实交易记录

## 📊 数据库结构

### 1. market_data.db

包含4个核心表：

#### klines_3m（3分钟K线数据）
```sql
CREATE TABLE klines_3m (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL,
    volume REAL NOT NULL,
    close_time INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, timestamp)
);
```

#### klines_4h（4小时K线数据）
```sql
CREATE TABLE klines_4h (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL,
    volume REAL NOT NULL,
    close_time INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, timestamp)
);
```

#### technical_indicators（技术指标）
```sql
CREATE TABLE technical_indicators (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    timeframe TEXT NOT NULL,
    ema_20 REAL,
    ema_50 REAL,
    macd REAL,
    macd_signal REAL,
    macd_histogram REAL,
    rsi_7 REAL,
    rsi_14 REAL,
    atr_3 REAL,
    atr_14 REAL,
    current_volume REAL,
    average_volume REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, timestamp, timeframe)
);
```

#### perpetual_data（永续合约数据）
```sql
CREATE TABLE perpetual_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    open_interest_latest REAL,
    open_interest_average REAL,
    funding_rate REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, timestamp)
);
```

## 🛠️ 数据库工具

### 1. quick_query.py - 快速查询

```bash
# 查看数据库概览
python3 quick_query.py summary

# 查看最新技术指标
python3 quick_query.py indicators

# 查看K线数据
python3 quick_query.py klines

# 查看永续合约数据
python3 quick_query.py perp

# 查看所有交易对
python3 quick_query.py symbols

# 查看最新数据
python3 quick_query.py latest
```

### 2. view_database.py - 交互式浏览器

```bash
# 启动交互式浏览器
python3 view_database.py

# 选择菜单：
# 1. View database overview
# 2. Custom SQL query
# 3. View klines data
# 4. View indicators
# 5. View perpetual data
```

### 3. demo_database.py - 数据库演示

```bash
# 运行数据库演示和示例
python3 demo_database.py

# 将展示：
# - 数据库表结构
# - 示例查询
# - SQL语法示例
# - 数据分析示例
```

## 💡 使用示例

### 直接SQL查询

```bash
# 进入SQLite命令行
sqlite3 market_data.db

# 查看所有表
.tables

# 查看表结构
.schema klines_3m

# 查询最新BTC数据
SELECT * FROM klines_3m WHERE symbol='BTCUSDT' ORDER BY timestamp DESC LIMIT 10;

# 查看技术指标
SELECT symbol, timestamp, ema_20, rsi_14 FROM technical_indicators WHERE symbol='BTCUSDT' ORDER BY timestamp DESC LIMIT 5;

# 退出
.quit
```

### Python代码查询

```python
import sqlite3

# 连接数据库
conn = sqlite3.connect('market_data.db')
cursor = conn.cursor()

# 查询最新数据
cursor.execute("""
    SELECT * FROM klines_3m
    WHERE symbol = ?
    ORDER BY timestamp DESC
    LIMIT 10
""", ('BTCUSDT',))

rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()
```

### 使用Database类

```python
from database import Database

# 初始化数据库
db = Database()

# 获取最新数据
data = db.get_latest_data('BTCUSDT')
print(data)

# 获取K线数据
klines = db.get_klines('BTCUSDT', '3m', limit=100)
print(klines)

# 获取技术指标
indicators = db.get_technical_indicators('BTCUSDT', '4h', limit=10)
print(indicators)
```

## 📈 数据分析示例

### 查看价格趋势
```sql
-- 查看BTC最近50条4小时K线
SELECT
    datetime(timestamp/1000, 'unixepoch') as time,
    open, high, low, close,
    (close - open) / open * 100 as change_pct
FROM klines_4h
WHERE symbol = 'BTCUSDT'
ORDER BY timestamp DESC
LIMIT 50;
```

### 分析技术指标
```sql
-- 查看最新技术指标
SELECT
    symbol,
    timeframe,
    ema_20,
    ema_50,
    rsi_14,
    macd,
    CASE
        WHEN rsi_14 > 70 THEN 'OVERBOUGHT'
        WHEN rsi_14 < 30 THEN 'OVERSOLD'
        ELSE 'NEUTRAL'
    END as rsi_signal
FROM technical_indicators
WHERE symbol = 'BTCUSDT' AND timeframe = '4h'
ORDER BY timestamp DESC
LIMIT 1;
```

### 交易量分析
```sql
-- 分析交易量变化
SELECT
    symbol,
    datetime(timestamp/1000, 'unixepoch') as time,
    volume,
    current_volume,
    average_volume,
    volume / average_volume as volume_ratio
FROM technical_indicators
WHERE symbol = 'BTCUSDT'
ORDER BY timestamp DESC
LIMIT 20;
```

## 🔧 维护和优化

### 数据库备份

```bash
# 备份数据库
cp market_data.db "market_data_$(date +%Y%m%d_%H%M%S).db"

# 备份所有数据库
for db in *.db; do
    cp "$db" "backup_${db}_$(date +%Y%m%d_%H%M%S)";
done
```

### 数据库优化

```sql
-- 分析数据库
ANALYZE;

-- 清理数据库
VACUUM;

-- 重建索引
REINDEX;
```

### 清理旧数据

```sql
-- 删除30天前的K线数据
DELETE FROM klines_3m
WHERE timestamp < (strftime('%s', 'now') - 30*24*3600) * 1000;

-- 删除90天前的技术指标数据
DELETE FROM technical_indicators
WHERE timestamp < (strftime('%s', 'now') - 90*24*3600) * 1000;
```

## 📊 性能监控

### 查看数据库统计

```bash
# 使用quick_query查看概览
python3 quick_query.py summary
```

输出示例：
```
Database: market_data.db
=======================

Table: klines_3m
  Records: 15,420
  Latest: 2025-11-05 16:30:00
  Symbols: BTCUSDT, ETHUSDT, SOLUSDT

Table: klines_4h
  Records: 3,850
  Latest: 2025-11-05 16:00:00
  Symbols: BTCUSDT, ETHUSDT, SOLUSDT

Table: technical_indicators
  Records: 12,600
  Latest: 2025-11-05 16:30:00

Table: perpetual_data
  Records: 5,420
  Latest: 2025-11-05 16:30:00
```

## 🚀 最佳实践

### 1. 定期备份
- 每日备份数据库文件
- 重要数据实时同步到云存储

### 2. 数据清理
- 定期清理过期的历史数据
- 保留必要的历史数据用于回测

### 3. 性能优化
- 为常用查询字段创建索引
- 定期执行ANALYZE更新统计信息

### 4. 监控
- 定期检查数据库大小
- 监控磁盘空间使用情况

## 📚 更多资源

- [SQLite 官方文档](https://sqlite.org/docs.html)
- [Python sqlite3 模块文档](https://docs.python.org/3/library/sqlite3.html)
- [SQL 教程](https://www.sqlite.org/lang.html)

## ⚠️ 注意事项

1. **并发访问**: SQLite不支持高并发写入，必要时考虑升级到PostgreSQL
2. **数据一致性**: 确保在写入数据时保持事务完整性
3. **定期维护**: 定期备份和清理，避免数据库过大影响性能

---

**更新**: 2025-11-05
**版本**: v1.0
