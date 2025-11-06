# 项目结构说明

## 📁 目录结构

```
nof1/
├── 📄 核心文件 (Root Level)
│   ├── main.py                      # 传统CLI入口点
│   ├── nof1.py                      # 统一启动器 (推荐)
│   ├── config.py                    # 配置文件
│   ├── database.py                  # 数据库操作
│   ├── data_fetcher.py              # 数据获取器
│   ├── indicators.py                # 技术指标计算
│   ├── scheduler.py                 # 任务调度器
│   ├── run_full_system.py           # 完整交易系统
│   ├── run_api.py                   # API服务器
│   ├── start_nof1.sh                # 抗断连启动脚本
│   └── requirements.txt             # 依赖列表
│
├── 🔧 交易模块 (trading/)
│   ├── __init__.py
│   ├── base.py                      # 抽象交易接口
│   ├── trading_factory.py           # 交易工厂
│   ├── testnet_trader.py            # Testnet交易器
│   ├── demo_trader.py               # Demo Trading交易器
│   ├── paper_trader_impl.py         # 纸交易模拟器
│   └── real_trader.py               # 真实交易器 (Legacy)
│
├── 📊 数据和模型
│   ├── models/                      # 数据模型
│   │   └── trading_decision.py      # 交易决策模型
│   ├── llm_clients/                 # LLM客户端
│   └── monitoring/                  # 性能监控
│
├── 🧪 测试 (tests/)
│   ├── unit/                        # 单元测试
│   ├── integration/                 # 集成测试
│   └── demo_trading/                # Demo Trading测试
│
├── 🛠️ 工具脚本 (scripts/)
│   ├── quick_query.py               # 快速数据库查询
│   ├── view_database.py             # 交互式数据库查看
│   ├── demo_database.py             # 数据库演示
│   ├── data_collector_only.py       # 纯数据收集器
│   ├── check_initial_funds.py       # 检查初始资金
│   ├── debug_*.py                   # 调试脚本
│   └── test_*.py                    # 测试脚本
│
├── 📚 文档 (docs/)
│   ├── user/                        # 用户文档
│   │   ├── README.md
│   │   ├── QUICKSTART.md
│   │   ├── QUICKSTART_TESTNET.md
│   │   ├── DATABASE_GUIDE.md
│   │   └── ROBUST_STARTUP.md
│   ├── dev/                         # 开发文档
│   ├── project/                     # 项目文档
│   │   ├── DEMO_TRADING_*.md        # Demo Trading相关文档
│   │   ├── API_DEBUG_SUMMARY.md
│   │   └── INITIAL_ASSETS_*.md
│   └── reference/                   # 参考文档
│       └── Binance Spot API.json
│
├── 🌐 前端文件 (web/)
│   └── trading_dashboard.html       # 实时交易监控面板
│
├── 📝 日志 (logs/)
│   ├── *.log                        # 各种日志文件
│   └── trading_*.log                # 交易系统日志
│
├── 🔧 工具 (utils/)
│   └── source.html                  # 临时/参考文件
│
└── 📊 数据库文件
    ├── market_data.db               # 市场数据
    ├── performance_monitor.db       # 性能监控
    ├── paper_trading.db             # 纸交易记录
    └── real_trading.db              # 真实交易记录
```

## 🎯 使用指南

### 快速启动
```bash
# 推荐方式：使用统一启动器
./start_nof1.sh start 2              # 运行2小时
python3 nof1.py --run 2              # 或直接运行

# 查看结果
python3 nof1.py --view
```

### 数据收集
```bash
# 纯数据收集（无交易）
python3 scripts/data_collector_only.py

# 快速数据收集测试
python3 scripts/quick_test_data_collection.py
```

### 数据库操作
```bash
# 快速查询
python3 scripts/quick_query.py summary
python3 scripts/quick_query.py latest

# 交互式查看
python3 scripts/view_database.py
```

### 测试
```bash
# 运行测试套件
python3 run_tests.py
python3 tests/demo_trading/test_trading_factory.py
```

### 交易模式
```python
from trading.trading_factory import TradingFactory

# 切换交易模式
trader = TradingFactory.create_trader('paper')    # 纸交易
trader = TradingFactory.create_trader('testnet')  # Testnet
trader = TradingFactory.create_trader('demo')     # Demo Trading
```

## 📖 文档位置

- **用户指南**: `docs/user/`
- **开发文档**: `docs/dev/`
- **项目文档**: `docs/project/`
- **API参考**: `docs/reference/`

## ⚠️ 注意事项

1. **配置文件**: `.env` 文件包含敏感信息，请勿提交到版本控制
2. **日志文件**: 存储在 `logs/` 目录中，可定期清理
3. **数据库**: SQLite数据库文件位于根目录，定期备份
4. **PID文件**: `pids/` 目录存储进程ID，用于进程管理

## 🔄 文件变更历史

### 最近整理 (2025-11-06)
- ✅ 移动所有 `.md` 文档到 `docs/` 目录
- ✅ 移动工具脚本到 `scripts/` 目录
- ✅ 移动日志文件到 `logs/` 目录
- ✅ 移动前端文件到 `web/` 目录
- ✅ 整理测试文件到 `tests/` 目录
- ✅ 创建清晰的项目结构说明

## 📝 贡献指南

在添加新文件时，请遵循以下规则：
- 核心模块留在根目录或相应模块目录
- 工具脚本放在 `scripts/` 目录
- 文档放在 `docs/` 相应子目录
- 测试文件放在 `tests/` 目录
- 日志文件自动存储在 `logs/` 目录
