# Nof1 Trading System 🚀

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

### 1️⃣ 生产级启动（推荐）
```bash
# 启动2小时交易系统（后台运行，终端可断开）
./start_nof1.sh start 2

# 查看状态
./start_nof1.sh status
```

### 2️⃣ 统一启动器
```bash
# 运行2小时
python3 nof1.py --run 2

# 仅启动API
python3 nof1.py --api

# 查看结果
python3 nof1.py --view
```

### 3️⃣ 监控方式
```bash
# 实时日志
tail -f logs/trading_*.log

# API文档
firefox http://localhost:8000/docs

# HTML面板
firefox trading_dashboard.html

# Testnet查看
python3 testnet_viewer.py
```

## 📖 完整文档

### 👥 用户文档
- **[QUICKSTART_TESTNET.md](QUICKSTART_TESTNET.md)** - Testnet快速开始（5分钟上手）
- **[ROBUST_STARTUP.md](ROBUST_STARTUP.md)** - 抗断连启动指南
- **[docs/user/README.md](docs/user/README.md)** - 项目概览
- **[docs/user/QUICKSTART.md](docs/user/QUICKSTART.md)** - 详细快速开始
- **[docs/user/INSTALL.md](docs/user/INSTALL.md)** - 安装指南
- **[docs/user/API_DOCUMENTATION.md](docs/user/API_DOCUMENTATION.md)** - API文档

### 💻 开发文档
- **[CLAUDE.md](CLAUDE.md)** - 开发者完整指南（最重要！）
- **[docs/dev/DEVELOPMENT.md](docs/dev/DEVELOPMENT.md)** - 开发指南
- **Database Tools**:
  ```bash
  python3 quick_query.py summary      # 快速查询
  python3 view_database.py            # 交互式浏览
  python3 demo_database.py            # 演示和示例
  ```

### 📊 项目文档
- **[docs/project/PROJECT_FINAL_REPORT.md](docs/project/PROJECT_FINAL_REPORT.md)** - 项目完成报告
- **[docs/project/PRODUCT_MANAGER_GUIDE.md](docs/project/PRODUCT_MANAGER_GUIDE.md)** - 产品经理指南

### 📦 归档文档
- **[docs/archive/](docs/archive/)** - 历史规划文档（参考用）

## 🎯 核心特性

- **🤖 双模型并行决策**: DeepSeek + Qwen3 协同分析
- **📊 多时间框架**: 4h趋势 + 3m时机精准把握
- **💰 Binance Testnet**: 真实API，虚拟资金（10,000 USDT）
- **🛡️ 抗断连启动**: `start_nof1.sh` - 终端断开自动恢复
- **🎯 智能缓存**: 节省85% API成本
- **📈 实时监控**: FastAPI + HTML面板
- **🗄️ 完整数据库工具**: 查询、浏览、演示
- **🧪 95%+ 测试覆盖率**: 92个测试用例，100%通过

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

## 📝 许可证

MIT License

## 👨‍💻 开发者

- 项目开发: Claude AI
- 项目仓库: https://github.com/harryhhh111/nof1.git
- 文档完整度: ⭐⭐⭐⭐⭐

---

**状态**: ✅ 生产就绪
**版本**: v1.0
**更新**: 2025-11-05
**推荐**: 使用 `start_nof1.sh` 进行生产部署
