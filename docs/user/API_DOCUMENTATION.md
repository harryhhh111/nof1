# Nof1 Trading API 文档

## 概述

Nof1 Trading API 提供RESTful接口，用于查询交易决策记录、盈利数据、性能统计等信息。参考 nof1.ai 的设计风格。

## 快速开始

### 1. 启动API服务器

```bash
# 安装依赖
pip install -r requirements.txt

# 启动API服务
python3 run_api.py
```

### 2. 访问API文档

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 3. 测试API

```bash
# 运行示例
python3 examples/api_example.py
```

## API端点

### 1. 获取决策记录

**端点**: `GET /api/v1/decisions`

**参数**:
- `page` (int, 查询参数): 页码，默认1
- `limit` (int, 查询参数): 每页数量，默认20，最大100
- `model` (str, 查询参数): 模型筛选 (deepseek/qwen/fusion)
- `symbol` (str, 查询参数): 交易对筛选
- `action` (str, 查询参数): 操作筛选 (BUY/SELL/HOLD)
- `start_date` (str, 查询参数): 开始日期 (YYYY-MM-DD)
- `end_date` (str, 查询参数): 结束日期 (YYYY-MM-DD)

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "timestamp": "2024-01-01 12:00:00",
      "symbol": "BTCUSDT",
      "action": "BUY",
      "confidence": 85,
      "pnl": 100.5,
      "execution_time": 1.5,
      "llm_cost": 0.02,
      "total_cost": 0.03
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "total_pages": 5
  }
}
```

**使用示例**:
```bash
# 获取所有决策
curl "http://localhost:8000/api/v1/decisions"

# 获取第2页，每页10条
curl "http://localhost:8000/api/v1/decisions?page=2&limit=10"

# 筛选DeepSeek模型决策
curl "http://localhost:8000/api/v1/decisions?model=deepseek"

# 筛选买入决策
curl "http://localhost:8000/api/v1/decisions?action=BUY"

# 时间范围查询
curl "http://localhost:8000/api/v1/decisions?start_date=2024-01-01&end_date=2024-01-31"

# 组合筛选
curl "http://localhost:8000/api/v1/decisions?symbol=BTCUSDT&action=BUY&limit=50"
```

### 2. 获取模型盈利数据

**端点**: `GET /api/v1/models/profit`

**参数**:
- `start_date` (str, 查询参数): 开始日期 (YYYY-MM-DD)
- `end_date` (str, 查询参数): 结束日期 (YYYY-MM-DD)
- `interval` (str, 查询参数): 时间间隔 (hour/day/week)，默认hour

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "timestamp": "2024-01-01 12:00:00",
      "period_pnl": 50.5,
      "cumulative_pnl": 50.5,
      "trade_count": 3
    },
    {
      "timestamp": "2024-01-01 13:00:00",
      "period_pnl": -20.0,
      "cumulative_pnl": 30.5,
      "trade_count": 2
    }
  ],
  "interval": "hour"
}
```

**使用示例**:
```bash
# 获取小时级盈利数据
curl "http://localhost:8000/api/v1/models/profit"

# 获取日级盈利数据
curl "http://localhost:8000/api/v1/models/profit?interval=day"

# 时间范围查询
curl "http://localhost:8000/api/v1/models/profit?start_date=2024-01-01&end_date=2024-01-31&interval=day"
```

### 3. 获取模型性能摘要

**端点**: `GET /api/v1/models/performance`

**参数**: 无

**响应示例**:
```json
{
  "success": true,
  "data": {
    "model": "ALL",
    "total_trades": 100,
    "winning_trades": 60,
    "losing_trades": 40,
    "win_rate": 60.0,
    "total_pnl": 5000.0,
    "avg_pnl_per_trade": 50.0,
    "total_cost": 3.0
  }
}
```

**使用示例**:
```bash
curl "http://localhost:8000/api/v1/models/performance"
```

### 4. 获取系统统计摘要

**端点**: `GET /api/v1/stats/summary`

**参数**: 无

**响应示例**:
```json
{
  "success": true,
  "data": {
    "total_decisions": 200,
    "total_trades": 100,
    "total_pnl": 5000.0,
    "total_cost": 6.0,
    "avg_confidence": 75.5,
    "cost_per_trade": 0.06
  }
}
```

**使用示例**:
```bash
curl "http://localhost:8000/api/v1/stats/summary"
```

### 5. 健康检查

**端点**: `GET /api/v1/health`

**参数**: 无

**响应示例**:
```json
{
  "success": true,
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00"
}
```

**使用示例**:
```bash
curl "http://localhost:8000/api/v1/health"
```

## Python客户端示例

```python
import requests

# 获取决策记录
response = requests.get("http://localhost:8000/api/v1/decisions?page=1&limit=10")
decisions = response.json()

# 获取盈利数据
response = requests.get(
    "http://localhost:8000/api/v1/models/profit",
    params={"interval": "day"}
)
profit_data = response.json()

# 获取性能摘要
response = requests.get("http://localhost:8000/api/v1/models/performance")
performance = response.json()
```

## 数据存储说明

### 数据库文件

1. **trading.db** - 纸交易记录
   - 表名: `trades`
   - 记录实际交易（BUY/SELL）
   - 字段: trade_id, timestamp, symbol, action, pnl, balance等

2. **performance_monitor.db** - 性能监控数据
   - 表名: `trading_metrics`
   - 记录所有决策（包含HOLD）
   - 字段: id, timestamp, symbol, action, confidence, pnl, llm_cost等

### 查询示例

```bash
# 直接查询SQLite数据库
sqlite3 performance_monitor.db

# 查看所有决策记录
SELECT * FROM trading_metrics ORDER BY timestamp DESC LIMIT 10;

# 统计每个模型的交易次数
SELECT action, COUNT(*) FROM trading_metrics GROUP BY action;

# 查看每日盈利
SELECT DATE(timestamp) as date, SUM(pnl) as daily_pnl
FROM trading_metrics
WHERE pnl IS NOT NULL
GROUP BY DATE(timestamp)
ORDER BY date DESC;
```

## 错误处理

所有API响应都遵循统一的格式：

```json
{
  "success": true/false,
  "data": ...,
  "error": "错误信息（如果有）"
}
```

## 限制说明

- 分页最大限制: 100条/页
- 日期格式: YYYY-MM-DD
- 时间戳格式: YYYY-MM-DD HH:MM:SS

## 常见问题

### Q: 数据库文件不存在怎么办？
A: API会返回空数据，并提示"数据库文件不存在"。需要先运行交易系统生成数据。

### Q: 如何查看HOLD决策？
A: 所有决策（包括HOLD）都记录在performance_monitor.db的trading_metrics表中。

### Q: 如何筛选特定模型的决策？
A: 使用model参数，但需要注意模型信息存储在action字段中，可能需要使用模糊匹配。

## 联系我们

如有问题或建议，请提交Issue到GitHub仓库。
