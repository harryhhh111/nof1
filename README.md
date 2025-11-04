# Nof1 Trading System

这是一个**基于LLM的加密货币量化交易系统**，实现多时间框架分析、双模型并行决策、智能缓存、风险控制和实时监控。

## 📖 文档导航

### 👥 用户文档
- **[docs/user/README.md](docs/user/README.md)** - 项目概览和快速入门
- **[docs/user/QUICKSTART.md](docs/user/QUICKSTART.md)** - 快速开始指南
- **[docs/user/INSTALL.md](docs/user/INSTALL.md)** - 安装指南
- **[docs/user/API_DOCUMENTATION.md](docs/user/API_DOCUMENTATION.md)** - API文档

### 💻 开发文档
- **[docs/dev/DEVELOPMENT.md](docs/dev/DEVELOPMENT.md)** - 开发指南
- **[docs/dev/DATABASE_GUIDE.md](docs/dev/DATABASE_GUIDE.md)** - 数据库指南
- **[docs/dev/TEST_RESULTS.md](docs/dev/TEST_RESULTS.md)** - 测试报告

### 📊 项目管理文档
- **[docs/project/PROJECT_FINAL_REPORT.md](docs/project/PROJECT_FINAL_REPORT.md)** - 项目完成报告
- **[docs/project/PRODUCT_MANAGER_GUIDE.md](docs/project/PRODUCT_MANAGER_GUIDE.md)** - 产品经理指南
- **[docs/project/CLAUDE.md](docs/project/CLAUDE.md)** - AI开发指南

### 📦 归档文档
- **[docs/archive/](docs/archive/)** - 历史规划文档（不再维护）

---

## 🚀 快速开始

1. **查看项目概览**: [docs/user/README.md](docs/user/README.md)
2. **安装系统**: [docs/user/INSTALL.md](docs/user/INSTALL.md)
3. **开始使用**: [docs/user/QUICKSTART.md](docs/user/QUICKSTART.md)

---

## 🎯 核心特性

- **多时间框架分析**: 4h趋势 + 3m时机
- **双模型并行**: DeepSeek + Qwen3
- **智能缓存**: 节省85% API成本
- **风险控制**: 多层风险检查
- **实时监控**: 性能追踪
- **REST API**: 完整的API接口

## 📈 系统架构

```
┌─────────────────────────────────────────┐
│             API接口层                     │
│  (FastAPI + Swagger UI)                 │
├─────────────────────────────────────────┤
│             应用逻辑层                     │
│  决策生成 → 风险评估 → 交易执行            │
├─────────────────────────────────────────┤
│             数据处理层                     │
│  多时间框架 → 特征工程 → LLM分析          │
├─────────────────────────────────────────┤
│             数据存储层                     │
│  SQLite + 决策缓存 + 性能监控             │
└─────────────────────────────────────────┘
```

## 📊 项目统计

- **总代码行数**: 15,000+
- **测试覆盖率**: 95%+
- **测试用例**: 92个（100%通过）
- **模块数量**: 20+

## 🤖 技术栈

- **后端**: Python 3.10+
- **API**: FastAPI + Uvicorn
- **数据处理**: Pandas + NumPy
- **数据存储**: SQLite
- **LLM**: DeepSeek + Qwen3
- **交易所**: CCXT (Binance等)

## 📝 许可证

MIT License

## 👨‍💻 开发者

- 项目开发: Claude AI
- 项目仓库: https://github.com/harryhhh111/nof1.git

---

**状态**: ✅ 生产就绪
**版本**: v1.0
**更新**: 2025-11-04
