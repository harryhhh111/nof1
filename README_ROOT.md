# Nof1 - LLM驱动加密货币交易系统

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Binance Testnet](https://img.shields.io/badge/Binance-Testnet-green.svg)](https://testnet.binance.vision/)

## 🚀 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 启动系统（推荐）
```bash
# 方式1：使用抗断连启动脚本
./start_nof1.sh start 2              # 运行2小时

# 方式2：使用统一启动器
python3 nof1.py --run 2              # 运行2小时

# 方式3：数据收集模式
python3 scripts/data_collector_only.py
```

### 查看结果
```bash
python3 nof1.py --view               # 查看交易决策和持仓
python3 scripts/quick_query.py summary  # 查看数据库摘要
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

## 🎯 核心功能

- ✅ 多时间框架数据分析 (4h + 3m)
- ✅ 并行LLM决策 (DeepSeek + Qwen3)
- ✅ 智能决策缓存
- ✅ 真实交易执行 (Testnet)
- ✅ 交易工厂模式
- ✅ FastAPI服务器 (Port 8000)
- ✅ HTML监控面板
- ✅ 数据库工具集

## 📖 文档导航

### 用户指南
- [快速开始](docs/user/QUICKSTART.md)
- [Testnet快速指南](docs/user/QUICKSTART_TESTNET.md)
- [数据库使用指南](docs/user/DATABASE_GUIDE.md)
- [抗断连启动指南](docs/user/ROBUST_STARTUP.md)

### 开发者
- [交易工厂使用](CLAUDE.md#交易模块抽象工厂模式)
- [API文档](docs/user/API_DOCUMENTATION.md)
- [测试指南](docs/dev/DEVELOPMENT.md)

### 项目
- [项目结构](PROJECT_STRUCTURE.md)
- [Demo Trading升级报告](docs/project/DEMO_TRADING_UPGRADE_REPORT.md)

## 🔧 常用命令

### 系统运行
```bash
./start_nof1.sh start 24             # 运行24小时
./start_nof1.sh status               # 查看状态
./start_nof1.sh stop                 # 停止服务
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
# 查看日志
tail -f logs/trading_*.log

# 访问监控面板
# 浏览器打开: web/trading_dashboard.html

# API文档
# 浏览器打开: http://localhost:8000/docs
```

## ⚠️ 重要提示

1. **测试模式**: 系统默认使用Testnet模式，资金为虚拟资金
2. **API配置**: 需要配置Testnet API Key（从 [testnet.binance.vision](https://testnet.binance.vision) 获取）
3. **网络限制**: Demo Trading API在当前网络环境下可能不可达
4. **数据安全**: 请勿将 `.env` 文件提交到版本控制

## 📊 性能监控

### 当前运行状态
```bash
# 查看系统状态
python3 nof1.py --status

# 查看性能摘要
python3 nof1.py --view
```

### 数据库统计
- 市场数据: `market_data.db`
- 性能监控: `performance_monitor.db`
- 纸交易: `paper_trading.db`
- 真实交易: `real_trading.db`

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
