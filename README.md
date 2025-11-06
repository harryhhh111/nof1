# Nof1 - LLM驱动加密货币交易系统

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Binance Testnet](https://img.shields.io/badge/Binance-Testnet-green.svg)](https://testnet.binance.vision/)

**基于LLM的加密货币量化交易系统** - 集成多时间框架分析、双模型并行决策、Binance Testnet真实交易、智能缓存和实时监控。

## ⭐ 核心特性

- **🤖 双模型并行决策**: DeepSeek + Qwen3 协同分析
- **📊 多时间框架**: 4h趋势 + 3m时机精准把握
- **💰 Binance Testnet**: 真实API，虚拟资金（10,000 USDT）
- **🛡️ 抗断连启动**: `start_nof1.sh` - 终端断开自动恢复
- **🎯 智能缓存**: 节省85% API成本
- **📈 实时监控**: FastAPI + HTML面板
- **🗄️ 完整数据库工具**: 查询、浏览、演示
- **🧪 95%+ 测试覆盖率**: 92个测试用例，100%通过

## 🚀 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 启动系统（推荐）

#### 1️⃣ 生产级启动（推荐）
```bash
# 方式1：使用抗断连启动脚本（永久运行）
./start_nof1.sh start 999999         # 永久运行
# 或
./start_nof1.sh start 2              # 运行2小时

# 方式2：使用统一启动器
python3 nof1.py --run 2              # 运行2小时

# 方式3：仅数据收集模式（永久运行）
nohup python3 scripts/data_collector_only.py > logs/data_collector.log 2>&1 &

# 方式4：仅启动API服务器
./start_nof1.sh start-api
# 或
python3 nof1.py --api
```

#### 2️⃣ 查看结果
```bash
# 推荐：使用监控脚本
./scripts/check_trading.sh           # 快速状态检查
./scripts/monitor_trading.sh         # 定期监控 (每5分钟)

# 数据库查询
python3 scripts/quick_query.py summary  # 查看数据库摘要
python3 scripts/quick_query.py latest   # 查看最新数据

# 查看交易结果
python3 nof1.py --view               # 查看交易决策和持仓
```

## 📊 项目结构

```
nof1/
├── 🔧 核心模块          # 交易系统和数据处理
├── 📚 docs/            # 完整文档
├── 🛠️ scripts/         # 工具脚本
├── 🧪 tests/           # 测试套件
├── 🌐 web/             # 前端监控面板
├── 📝 logs/            # 日志文件
└── 📊 数据库文件        # SQLite数据库
```

📖 **详细文档**: [查看 PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)

## 💰 支持的交易模式

| 模式 | API | 资金 | 风险 |
|------|-----|------|------|
| 🟢 Paper | 模拟 | 虚拟 | 无 |
| 🟢 Testnet | testnet.binance.vision | 虚拟 | 无 |
| 🟢 Demo | demo-api.binance.com | 虚拟 | 无 |
| 🔴 Live | api.binance.com | 真实 | 高 |

## 📖 文档导航

### 用户指南
- [快速开始](docs/user/QUICKSTART.md)
- [Testnet快速指南](docs/user/QUICKSTART_TESTNET.md)
- [数据库使用指南](docs/user/DATABASE_GUIDE.md)
- [抗断连启动指南](docs/user/ROBUST_STARTUP.md)

### 监控工具
- [监控脚本使用指南](scripts/README_MONITORING.md)
- [快速状态检查](scripts/check_trading.sh)
- [定期监控工具](scripts/monitor_trading.sh)

### 开发者
- [CLAUDE.md - AI开发指南](CLAUDE.md) (📌 位于根目录)
- [API文档](docs/user/API_DOCUMENTATION.md)
- [测试指南](docs/dev/DEVELOPMENT.md)

### 项目
- [项目结构](PROJECT_STRUCTURE.md)
- [Demo Trading升级报告](docs/project/DEMO_TRADING_UPGRADE_REPORT.md)

## 🔧 常用命令

### 系统运行
```bash
# 推荐：永久运行
nohup python3 run_full_system.py --hours 999999 > logs/trading_infinity.log 2>&1 &
./start_nof1.sh start 999999         # 或使用此命令

# 限时运行
./start_nof1.sh start 2              # 运行2小时
./start_nof1.sh start 24             # 运行24小时

# 系统管理
./start_nof1.sh status               # 查看状态
./start_nof1.sh stop                 # 停止服务
./start_nof1.sh restart              # 重启服务
python3 nof1.py --api                # 启动API服务器
```

### 数据操作
```bash
# 快速查询
python3 scripts/quick_query.py summary
python3 scripts/quick_query.py latest
python3 scripts/quick_query.py klines

# 交互式查看
python3 scripts/view_database.py
```

### 测试
```bash
# 完整测试套件
python3 run_tests.py

# 交易工厂测试
python3 tests/demo_trading/test_trading_factory.py

# 基本功能测试
python3 test_basic.py
```

### 监控
```bash
# 推荐：使用监控脚本
./scripts/check_trading.sh           # 快速状态检查 (推荐日常使用)
./scripts/monitor_trading.sh         # 定期监控 (每5分钟自动刷新)

# 查看日志
tail -f logs/trading_infinity.log    # 交易系统日志
tail -f logs/data_collector.log      # 数据收集器日志
./start_nof1.sh logs                 # 查看所有日志

# API接口
curl http://localhost:8000/api/v1/health     # 健康检查
curl http://localhost:8000/api/v1/decisions  # 查看交易决策

# Web界面
# 浏览器打开: http://localhost:8000/docs (API文档)
# 浏览器打开: https://testnet.binance.vision/ (Testnet官方界面)
```

## ⚠️ 重要提示

1. **测试模式**: 系统默认使用Testnet模式，资金为虚拟资金 (推荐)
2. **永久运行**: 使用 `999999` 小时参数实现永久运行，或使用监控脚本
3. **API配置**: 需要配置Testnet API Key（从 [testnet.binance.vision](https://testnet.binance.vision) 获取）
4. **监控工具**: 推荐使用 `./scripts/check_trading.sh` 和 `./scripts/monitor_trading.sh`
5. **文件位置**: CLAUDE.md 必须在项目根目录（遵循规范）
6. **数据安全**: 请勿将 `.env` 文件提交到版本控制
7. **网络限制**: Demo Trading API在当前网络环境下可能不可达

## 📊 性能监控

### 当前运行状态
```bash
# 快速状态检查 (推荐)
./scripts/check_trading.sh

# 查看系统状态
./start_nof1.sh status
python3 nof1.py --status

# 查看性能摘要
python3 nof1.py --view
```

### 数据库统计
- 市场数据: `market_data.db`
- 性能监控: `performance_monitor.db`
- 纸交易: `paper_trading.db`
- 真实交易: `real_trading.db`

## 📊 项目统计

- **总代码行数**: 15,000+
- **测试覆盖率**: 95%+
- **测试用例**: 92个（100%通过）
- **模块数量**: 20+
- **数据库表**: 4个核心表（klines, indicators, perp_data）
- **API端点**: 10+ RESTful接口

## 🤖 技术栈

- **后端**: Python 3.10+
- **API**: FastAPI + Uvicorn (端口8000)
- **数据处理**: Pandas + NumPy
- **数据存储**: SQLite (3个数据库文件)
- **LLM**: DeepSeek + Qwen3
- **交易所**: CCXT (Binance Testnet/Live)
- **启动方式**: `start_nof1.sh` (抗断连) + `nof1.py` (统一启动)

## 💡 为什么选择 Nof1？

### ✅ 生产就绪
- 完整的端到端交易系统
- 95%+测试覆盖率
- 错误处理和日志记录

### ✅ 易用性
- 一键启动：`./start_nof1.sh start 2`
- 统一管理界面
- 丰富的监控工具

### ✅ 安全性
- 默认使用Testnet（虚拟资金）
- 决策验证机制
- 风险管理系统

### ✅ 可扩展
- 模块化架构
- 支持添加新交易所
- 易于扩展技术指标

## 🤝 贡献

欢迎提交Issues和Pull Requests！

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [CCXT](https://github.com/ccxt/ccxt) - 加密货币交易库
- [Binance](https://www.binance.com/) - 交易所API
- [pandas](https://pandas.pydata.org/) - 数据分析库

---

**⚠️ 风险警告**: 加密货币交易存在风险。本系统仅供学习和研究使用，请谨慎投资。
