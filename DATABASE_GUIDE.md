# Nof1 数据库查看指南

## 📁 数据库位置

数据库文件默认位置：`market_data.db`

```bash
# 查看数据库文件
ls -lh market_data.db
```

## 🗄️ 数据库表结构

### 1. klines_3m (3分钟 K 线数据)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| symbol | TEXT | 交易对符号 |
| timestamp | INTEGER | 时间戳 (毫秒) |
| open | REAL | 开盘价 |
| high | REAL | 最高价 |
| low | REAL | 最低价 |
| close | REAL | 收盘价 |
| volume | REAL | 成交量 |
| close_time | INTEGER | 收盘时间 |
| created_at | TIMESTAMP | 创建时间 |

### 2. klines_4h (4小时 K 线数据)

字段结构与 `klines_3m` 相同。

### 3. technical_indicators (技术指标数据)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| symbol | TEXT | 交易对符号 |
| timestamp | INTEGER | 时间戳 |
| timeframe | TEXT | 时间框架 (3m 或 4h) |
| ema_20 | REAL | 20期指数移动平均线 |
| ema_50 | REAL | 50期指数移动平均线 |
| macd | REAL | MACD 值 |
| macd_signal | REAL | MACD 信号线 |
| macd_histogram | REAL | MACD 柱状图 |
| rsi_7 | REAL | 7期相对强弱指数 |
| rsi_14 | REAL | 14期相对强弱指数 |
| atr_3 | REAL | 3期平均真实波幅 |
| atr_14 | REAL | 14期平均真实波幅 |
| current_volume | REAL | 当前成交量 |
| average_volume | REAL | 平均成交量 |
| created_at | TIMESTAMP | 创建时间 |

### 4. perpetual_data (永续合约数据)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| symbol | TEXT | 交易对符号 |
| timestamp | INTEGER | 时间戳 |
| open_interest_latest | REAL | 最新开放利息 |
| open_interest_average | REAL | 平均开放利息 |
| funding_rate | REAL | 资金费率 |
| created_at | TIMESTAMP | 创建时间 |

## 🔍 查看数据库的方法

### 方法 1：快速查看所有信息

```bash
python3 quick_query.py
```

或单独查看某个方面：
```bash
python3 quick_query.py summary   # 查看摘要
python3 quick_query.py symbols   # 查看交易对
python3 quick_query.py latest    # 查看最新数据
python3 quick_query.py klines    # 查看 K 线
python3 quick_query.py indicators # 查看技术指标
python3 quick_query.py perp      # 查看永续合约数据
```

### 方法 2：交互式数据库查看器

```bash
python3 view_database.py
```

功能包括：
- 查看数据库概览
- 查看最新数据
- 自定义 SQL 查询

### 方法 3：数据库演示工具

```bash
python3 demo_database.py
```

功能包括：
- 创建示例数据
- 数据库摘要
- 常用查询示例
- 表结构查看

### 方法 4：直接使用 sqlite3 命令

```bash
# 进入 sqlite3 命令行
sqlite3 market_data.db

# 查看所有表
.tables

# 查看表结构
.schema klines_3m

# 查看数据
SELECT * FROM klines_3m LIMIT 10;

# 退出
.quit
```

### 方法 5：使用 Python 脚本

```python
import sqlite3
from datetime import datetime

conn = sqlite3.connect('market_data.db')
cursor = conn.cursor()

# 查询最新数据
cursor.execute("""
    SELECT symbol, timestamp, close, volume
    FROM klines_3m
    ORDER BY timestamp DESC
    LIMIT 5
""")

for row in cursor.fetchall():
    dt = datetime.fromtimestamp(row[1] / 1000).strftime('%Y-%m-%d %H:%M:%S')
    print(f"{row[0]} @ {dt}: ${row[2]:.2f} (Volume: {row[3]:.2f})")

conn.close()
```

## 📊 常用 SQL 查询示例

### 1. 查看数据库统计

```sql
-- 查看各表记录数
SELECT
    'klines_3m' as table_name, COUNT(*) as record_count
FROM klines_3m
UNION ALL
SELECT
    'klines_4h' as table_name, COUNT(*) as record_count
FROM klines_4h
UNION ALL
SELECT
    'technical_indicators' as table_name, COUNT(*) as record_count
FROM technical_indicators
UNION ALL
SELECT
    'perpetual_data' as table_name, COUNT(*) as record_count
FROM perpetual_data;
```

### 2. 查看最新价格

```sql
-- 查看所有交易对的最新价格
SELECT
    symbol,
    timestamp,
    close as price,
    volume
FROM klines_3m
WHERE (symbol, timestamp) IN (
    SELECT symbol, MAX(timestamp)
    FROM klines_3m
    GROUP BY symbol
)
ORDER BY symbol;
```

### 3. 查看技术指标趋势

```sql
-- 查看 BTCUSDT 最近 10 条技术指标
SELECT
    symbol,
    timeframe,
    timestamp,
    ema_20,
    ema_50,
    rsi_14,
    atr_14
FROM technical_indicators
WHERE symbol = 'BTCUSDT'
ORDER BY timestamp DESC
LIMIT 10;
```

### 4. 查看交易量分析

```sql
-- 查看当前交易量 vs 平均交易量
SELECT
    symbol,
    timeframe,
    current_volume,
    average_volume,
    (current_volume / average_volume) as volume_ratio
FROM technical_indicators
WHERE (symbol, timestamp) IN (
    SELECT symbol, MAX(timestamp)
    FROM technical_indicators
    GROUP BY symbol
)
ORDER BY volume_ratio DESC;
```

### 5. 查看永续合约数据

```sql
-- 查看资金费率和开放利息
SELECT
    symbol,
    funding_rate,
    open_interest_latest,
    open_interest_average,
    timestamp
FROM perpetual_data
ORDER BY timestamp DESC;
```

### 6. 时间范围查询

```sql
-- 查看最近一小时的 K 线数据
SELECT *
FROM klines_3m
WHERE timestamp > (SELECT MAX(timestamp) - 3600000 FROM klines_3m)
ORDER BY timestamp DESC;
```

### 7. 统计查询

```sql
-- 统计每个交易对的记录数
SELECT
    symbol,
    COUNT(*) as kline_count,
    MIN(timestamp) as first_update,
    MAX(timestamp) as last_update
FROM klines_3m
GROUP BY symbol
ORDER BY kline_count DESC;
```

## 📈 使用 Python 查询示例

### 示例 1：获取最新 BTC 价格

```python
from database import Database
from datetime import datetime

db = Database()
data = db.get_latest_data('BTCUSDT')

if data:
    print(f"BTCUSDT 最新数据:")
    print(f"  时间: {data['timestamp']}")
    print(f"  价格: ${data['current_price']:,.2f}")
    print(f"  EMA20: {data['long_term']['ema_20']:.2f}")
    print(f"  RSI14: {data['long_term']['rsi_14']:.2f}")
```

### 示例 2：获取所有交易对最新价格

```python
from database import Database

db = Database()

for symbol in ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']:
    data = db.get_latest_data(symbol)
    if data:
        print(f"{symbol}: ${data['current_price']:,.2f}")
```

### 示例 3：获取历史数据

```python
from database import Database
import pandas as pd

db = Database()

# 获取 BTCUSDT 最近 50 条 K 线数据
df = db.get_klines('BTCUSDT', '3m', limit=50)
print(df.tail())

# 计算平均价格
avg_price = df['close'].mean()
print(f"平均价格: ${avg_price:.2f}")
```

## 🔧 工具脚本说明

### quick_query.py

快速查看数据库信息：

```bash
python3 quick_query.py summary   # 摘要
python3 quick_query.py symbols   # 交易对
python3 quick_query.py latest    # 最新数据
python3 quick_query.py klines    # K 线
python3 quick_query.py indicators # 技术指标
python3 quick_query.py perp      # 永续合约
```

### view_database.py

交互式查看器：

```bash
python3 view_database.py
```

选项：
1. 查看数据库概览
2. 自定义 SQL 查询
3. 退出

### demo_database.py

数据库演示工具：

```bash
python3 demo_database.py
```

选项：
1. 创建示例数据
2. 查看数据库摘要
3. 常用查询示例
4. 查看表结构
5. 退出

## 💡 查询技巧

### 1. 格式化时间戳

```sql
-- 将毫秒时间戳转换为可读格式
SELECT
    symbol,
    datetime(timestamp/1000, 'unixepoch') as datetime,
    close
FROM klines_3m
ORDER BY timestamp DESC
LIMIT 5;
```

### 2. 计算价格变化

```sql
-- 计算价格变化百分比
SELECT
    symbol,
    timestamp,
    close,
    LAG(close) OVER (PARTITION BY symbol ORDER BY timestamp) as prev_close,
    ((close - LAG(close) OVER (PARTITION BY symbol ORDER BY timestamp)) / LAG(close) OVER (PARTITION BY symbol ORDER BY timestamp)) * 100 as change_pct
FROM klines_3m
ORDER BY symbol, timestamp DESC
LIMIT 10;
```

### 3. 查找异常数据

```sql
-- 查找异常大的成交量
SELECT *
FROM klines_3m
WHERE volume > (SELECT AVG(volume) * 3 FROM klines_3m)
ORDER BY volume DESC
LIMIT 10;
```

## 📝 注意事项

1. **时间戳格式**：数据库中的 timestamp 为毫秒级时间戳
2. **索引**：已为关键字段创建索引，查询性能良好
3. **数据清理**：可以删除旧数据以节省空间
4. **备份**：定期备份数据库文件

## 🚀 高级用法

### 使用 pandas 查看数据

```python
import pandas as pd
import sqlite3

# 直接从数据库读取到 DataFrame
conn = sqlite3.connect('market_data.db')
df = pd.read_sql_query("SELECT * FROM klines_3m", conn)
conn.close()

# 分析数据
print(df.describe())
print(df.groupby('symbol')['volume'].mean())
```

---

通过以上方法，您可以轻松查看和分析 Nof1 数据库中的所有数据！
