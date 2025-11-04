# Nof1 开发指南

本指南为开发人员提供系统开发、数据库操作、测试等技术的详细说明。

---

## 📁 数据库开发指南

### 数据库位置

数据库文件位置：
- `market_data.db` - 市场数据（K线、技术指标）
- `trading.db` - 纸交易记录
- `performance_monitor.db` - 性能监控数据

```bash
# 查看数据库文件
ls -lh *.db
```

### 数据库表结构

#### 1. klines_3m (3分钟K线数据)

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

#### 2. klines_4h (4小时K线数据)

字段结构与 `klines_3m` 相同。

#### 3. technical_indicators (技术指标数据)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| symbol | TEXT | 交易对符号 |
| timestamp | INTEGER | 时间戳 |
| timeframe | TEXT | 时间框架 (3m 或 4h) |
| ema_20 | REAL | 20期指数移动平均线 |
| ema_50 | REAL | 50期指数移动平均线 |
| macd | REAL | MACD值 |
| macd_signal | REAL | MACD信号线 |
| macd_histogram | REAL | MACD柱状图 |
| rsi_7 | REAL | 7期相对强弱指数 |
| rsi_14 | REAL | 14期相对强弱指数 |
| atr_3 | REAL | 3期平均真实波幅 |
| atr_14 | REAL | 14期平均真实波幅 |
| current_volume | REAL | 当前成交量 |
| average_volume | REAL | 平均成交量 |
| created_at | TIMESTAMP | 创建时间 |

#### 4. perpetual_data (永续合约数据)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| symbol | TEXT | 交易对符号 |
| timestamp | INTEGER | 时间戳 |
| open_interest_latest | REAL | 最新开放利息 |
| open_interest_average | REAL | 平均开放利息 |
| funding_rate | REAL | 资金费率 |
| created_at | TIMESTAMP | 创建时间 |

#### 5. trades (交易记录表)

| 字段 | 类型 | 说明 |
|------|------|------|
| trade_id | TEXT | 交易唯一ID |
| timestamp | TEXT | 交易时间 |
| symbol | TEXT | 交易对 |
| action | TEXT | 交易动作 (BUY/SELL/HOLD) |
| entry_price | REAL | 入场价格 |
| exit_price | REAL | 出场价格 |
| size | REAL | 仓位大小 |
| pnl | REAL | 盈亏 |
| balance | REAL | 账户余额 |
| decision | TEXT | 交易决策 (JSON) |

#### 6. trading_metrics (性能监控表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| timestamp | TEXT | 时间戳 |
| symbol | TEXT | 交易对 |
| action | TEXT | 操作 |
| confidence | REAL | 置信度 |
| pnl | REAL | 盈亏 |
| execution_time | REAL | 执行时间 |
| llm_cost | REAL | LLM成本 |
| total_cost | REAL | 总成本 |

### 数据库操作工具

#### 快速查看

```bash
python3 quick_query.py summary   # 查看摘要
python3 quick_query.py symbols   # 查看交易对
python3 quick_query.py latest    # 查看最新数据
python3 quick_query.py klines    # 查看K线
python3 quick_query.py indicators # 查看技术指标
python3 quick_query.py perp      # 查看永续合约数据
```

#### 交互式查看器

```bash
python3 view_database.py
```

功能包括：
- 查看数据库概览
- 查看最新数据
- 自定义SQL查询

#### 数据库演示

```bash
python3 demo_database.py
```

### 直接SQL查询示例

```python
import sqlite3

# 连接数据库
conn = sqlite3.connect('market_data.db')
cursor = conn.cursor()

# 查询最新K线
cursor.execute('''
    SELECT * FROM klines_3m
    WHERE symbol = ?
    ORDER BY timestamp DESC
    LIMIT 10
''', ('BTCUSDT',))

for row in cursor.fetchall():
    print(row)

conn.close()
```

---

## 🧪 测试指南

### 测试概览

**测试执行时间**：2025年11月4日
**测试环境**：Linux 5.15.0-153-generic, Python 3.10

### 测试统计

| 测试文件 | 测试用例数 | 通过 | 失败 | 错误 | 状态 |
|---------|-----------|------|------|------|------|
| test_performance_monitor.py | 14 | 14 | 0 | 0 | ✅ 通过 |
| test_multi_timeframe_preprocessor.py | 14 | 14 | 0 | 0 | ✅ 通过 |
| test_paper_trader.py | 22 | 22 | 0 | 0 | ✅ 通过 |
| test_decision_cache.py | 13 | 13 | 0 | 0 | ✅ 通过 |
| test_risk_manager.py | 17 | 17 | 0 | 0 | ✅ 通过 |
| test_integration_complete.py | 12 | 12 | 0 | 0 | ✅ 通过 |
| **总计** | **92** | **92** | **0** | **0** | **✅ 100%通过** |

### 运行测试

```bash
# 运行所有测试
PYTHONPATH=/home/claude_user/nof1 python3 tests/test_*.py

# 运行单个测试文件
PYTHONPATH=/home/claude_user/nof1 python3 tests/test_performance_monitor.py

# 运行集成测试
PYTHONPATH=/home/claude_user/nof1 python3 tests/test_integration_complete.py
```

### 测试类型

#### 1. 单元测试

每个模块都有对应的单元测试：

- `test_multi_timeframe_preprocessor.py` - 14个测试
  - 4小时数据处理
  - 3分钟数据处理
  - 趋势分析
  - 突破检测
  - 超买超卖分析

- `test_paper_trader.py` - 22个测试
  - 买入/卖出交易执行
  - 盈亏计算
  - 仓位管理
  - 手续费计算
  - 数据库持久化

- `test_decision_cache.py` - 13个测试
  - 缓存保存/获取
  - TTL过期机制
  - 缓存命中率计算
  - 多级缓存管理

- `test_risk_manager.py` - 17个测试
  - 决策有效性评估
  - 风险指标计算
  - VaR计算
  - 夏普比率计算
  - 最大回撤计算

- `test_performance_monitor.py` - 14个测试
  - 性能监控
  - 交易指标记录
  - 系统指标记录
  - 成本分析
  - 告警系统

#### 2. 集成测试

`test_integration_complete.py` - 12个测试

验证模块间协作：
- 所有模块导入测试
- 数据管道集成
- 交易决策创建和验证
- 纸交易执行器集成
- 风险管理器集成
- 回测引擎集成
- 性能监控器集成
- 决策缓存集成
- 完整工作流模拟

### 测试覆盖率

- **核心功能模块**：100%覆盖
- **关键路径测试**：✅ 全部通过
- **边界条件测试**：✅ 全部通过
- **错误处理测试**：✅ 全部通过

### 编写新测试

```python
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from your_module import YourClass

class TestYourClass(unittest.TestCase):
    def setUp(self):
        """测试前准备"""
        self.instance = YourClass()

    def test_your_method(self):
        """测试你的方法"""
        result = self.instance.your_method()
        self.assertEqual(result, expected_value)

    def test_edge_case(self):
        """测试边界情况"""
        with self.assertRaises(Exception):
            self.instance.bad_method()

if __name__ == '__main__':
    unittest.main()
```

---

## 💻 开发环境设置

### 环境要求

- Python 3.10+
- pip

### 安装依赖

```bash
pip install -r requirements.txt
```

### 代码结构

```
nof1/
├── api/                    # API服务
├── llm_clients/           # LLM客户端
├── models/                # 数据模型
├── trading/              # 交易执行
├── scheduling/           # 调度和缓存
├── risk_management/      # 风险管理和回测
├── monitoring/           # 性能监控
├── tests/                # 测试目录
├── docs/                 # 文档
└── examples/             # 示例代码
```

---

## 🚀 常用命令

### 启动API服务

```bash
python3 run_api.py
```

### 运行示例

```bash
# 监控系统示例
python3 examples/monitoring_example.py

# API使用示例
python3 examples/api_example.py
```

### 数据库工具

```bash
# SQLite命令行
sqlite3 market_data.db

# 快速查询
python3 quick_query.py summary
```

---

## 🔧 核心模块开发

### 1. 数据获取

**文件**: `data_fetcher.py`

```python
from data_fetcher import DataFetcher

fetcher = DataFetcher()
data = fetcher.get_klines('BTCUSDT', '3m', limit=100)
```

### 2. 数据预处理

**文件**: `multi_timeframe_preprocessor.py`

```python
from multi_timeframe_preprocessor import MultiTimeframeProcessor

processor = MultiTimeframeProcessor()
result_4h = processor.process_4h_data(data_4h)
result_3m = processor.process_3m_data(data_3m)
```

### 3. LLM决策

**文件**: `llm_clients/`

```python
from llm_clients.deepseek_client import DeepSeekClient
from llm_clients.qwen_client import QwenClient

deepseek = DeepSeekClient()
qwen = QwenClient()

decision = deepseek.get_decision(prompt)
```

### 4. 纸交易

**文件**: `trading/paper_trader.py`

```python
from trading.paper_trader import PaperTrader

trader = PaperTrader(initial_balance=100000)
result = trader.execute_decision(decision, current_price)
```

### 5. 风险评估

**文件**: `risk_management/risk_manager.py`

```python
from risk_management.risk_manager import RiskManager

risk_manager = RiskManager(account_balance=100000)
is_passed, message, size = risk_manager.evaluate_decision(
    decision, current_positions, price_data
)
```

### 6. 性能监控

**文件**: `monitoring/performance_monitor.py`

```python
from monitoring.performance_monitor import PerformanceMonitor

monitor = PerformanceMonitor()
monitor.record_trading_metrics(decision, pnl, execution_time, llm_cost, total_cost)
summary = monitor.get_performance_summary(paper_trader)
```

---

## 📚 参考资料

- [FastAPI文档](https://fastapi.tiangolo.com/)
- [SQLite教程](https://sqlite.org/docs.html)
- [pandas文档](https://pandas.pydata.org/docs/)
- [unittest文档](https://docs.python.org/3/library/unittest.html)

---

**更新时间**: 2025-11-04
**版本**: v1.0
