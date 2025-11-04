# Nof1 数据获取系统 - 快速启动指南

## ✅ 已完成的工作

### 1. 系统实现
- ✅ 完整的模块化架构实现
- ✅ 数据获取模块（支持 Binance via CCXT）
- ✅ 技术指标计算（EMA, MACD, RSI, ATR）
- ✅ SQLite 数据库存储
- ✅ 定时调度器
- ✅ 命令行接口

### 2. 核心文件
- `main.py` - 主程序入口，支持多种操作模式
- `data_fetcher.py` - 数据获取与处理引擎
- `indicators.py` - 纯 pandas 实现的技术指标计算
- `database.py` - SQLite 数据库操作
- `scheduler.py` - 定时任务调度器
- `config.py` - 系统配置

### 3. 数据库查看工具（新增）
- ✅ `quick_query.py` - 快速数据库查询工具
- ✅ `view_database.py` - 交互式数据库浏览器
- ✅ `demo_database.py` - 数据库演示工具
- ✅ `DATABASE_GUIDE.md` - 完整数据库指南

### 4. 测试与文档
- ✅ 完整的单元测试套件（tests/ 目录）
- ✅ 集成测试
- ✅ 基础功能测试脚本（test_basic.py）
- ✅ 系统演示脚本（demo.py）
- ✅ CLAUDE.md - AI 辅助开发指南
- ✅ QUICKSTART.md - 本文档
- ✅ INSTALL.md - 安装说明
- ✅ PROJECT_SUMMARY.md - 项目总结

### 5. 已修复的问题
- ✅ 修复数据库指标插入逻辑错误
- ✅ 移除对 pandas-ta 的依赖，改用纯 pandas 实现
- ✅ 优化技术指标计算算法

## 📦 依赖安装

### 安装所有依赖
```bash
pip install -r requirements.txt
```

### 核心依赖包
- `ccxt>=4.0.0` - 交易所 API 集成
- `pandas>=2.0.0` - 数据处理
- `numpy>=1.24.0` - 数值计算
- `schedule>=1.2.0` - 任务调度
- `requests>=2.31.0` - HTTP 请求
- `python-dotenv>=1.0.0` - 环境变量

## 🚀 快速开始

### 第一步：安装依赖
```bash
pip install -r requirements.txt
```

### 第二步：运行基础测试
```bash
python3 test_basic.py
```

这将测试：
- 模块导入
- 技术指标计算（EMA, MACD, RSI, ATR）
- 数据库操作
- 数据格式化

### 第三步：获取实时数据
```bash
# 获取单个交易对数据（JSON 格式）
python main.py --symbol BTCUSDT

# 获取多个交易对数据
python main.py --symbols BTCUSDT ETHUSDT SOLUSDT

# 以可读格式输出
python main.py --symbol BTCUSDT --output print
```

### 第四步：启动持续数据获取
```bash
# 启动定时调度器（默认每 3 分钟更新一次）
python main.py --schedule

# 自定义间隔和交易对
python main.py --schedule --symbols BTCUSDT ETHUSDT --interval 60
```

### 第五步：查看系统状态
```bash
# 显示数据库记录数、监控状态等
python main.py --status
```

### 第六步：查询历史数据
```bash
# 查询数据库中的最新数据
python main.py --query --symbols BTCUSDT
```

### 第七步：查看数据库（新增）
```bash
# 快速查看数据库摘要
python3 quick_query.py summary

# 查看技术指标
python3 quick_query.py indicators

# 查看 K 线数据
python3 quick_query.py klines

# 交互式数据库浏览器
python3 view_database.py

# 数据库演示和示例
python3 demo_database.py
```

## 📊 使用场景示例

### 场景 1：单次数据获取
```bash
# 获取 BTC 当前市场数据
python main.py --symbol BTCUSDT
```

输出示例：
```json
{
  "symbol": "BTCUSDT",
  "timestamp": "2025-11-02 10:30:00",
  "current_price": 67500.50,
  "intraday": {
    "prices": [67400.25, 67450.30, ...],
    "ema20": [67300.15, 67350.20, ...],
    "macd": [12.5, 15.3, ...],
    "rsi_7": [55.2, 56.8, ...],
    "rsi_14": [53.5, 54.2, ...]
  },
  "long_term": {
    "ema_20": 67200.50,
    "ema_50": 66800.25,
    "atr_3": 150.75,
    "atr_14": 285.50,
    "volume_current": 1250.30,
    "volume_average": 1180.45,
    "macd": [-15.2, -12.8, ...],
    "rsi_14": [48.5, 49.2, ...]
  },
  "perp_data": {
    "open_interest_latest": 50000.0,
    "open_interest_average": 48500.0,
    "funding_rate": 0.00015
  }
}
```

### 场景 2：持续监控模式
```bash
# 后台运行调度器（每 3 分钟更新一次）
python main.py --schedule
```

这将：
1. 立即获取一次所有交易对数据
2. 每 3 分钟自动更新一次
3. 将数据保存到 SQLite 数据库
4. 支持 Ctrl+C 安全退出

### 场景 3：系统监控
```bash
# 查看系统运行状态
python main.py --status
```

输出示例：
```
=== Nof1 数据获取系统状态 ===
数据库路径: market_data.db
监控交易对: BTCUSDT, ETHUSDT, SOLUSDT, BNBUSDT, DOGEUSDT, XRPUSDT
更新间隔: 180 秒
当前时间: 2025-11-02 10:30:00

数据库记录数:
  3分钟 K 线: 1,250 条
  4小时 K 线: 850 条
  技术指标: 2,100 条
  永续合约数据: 1,200 条
```

### 场景 4：数据库查看（新增）

系统提供多种查看数据库的方式：

**方式 1：快速查询工具**
```bash
# 查看数据库摘要
python3 quick_query.py summary

# 查看技术指标
python3 quick_query.py indicators

# 查看 K 线数据
python3 quick_query.py klines

# 查看永续合约数据
python3 quick_query.py perp
```

**方式 2：交互式查看器**
```bash
# 启动交互式数据库浏览器
python3 view_database.py

# 选择操作：
#   1. 查看数据库概览
#   2. 自定义 SQL 查询
#   3. 退出
```

**方式 3：数据库演示工具**
```bash
# 启动演示工具，包含示例数据
python3 demo_database.py

# 选择操作：
#   1. 创建示例数据
#   2. 查看数据库摘要
#   3. 常用查询示例
#   4. 查看表结构
#   5. 退出
```

**输出示例（quick_query.py indicators）：**
```
======================================================================
📊 技术指标 (最新)
======================================================================
交易对          周期     EMA20        EMA50        RSI14    ATR14
----------------------------------------------------------------------
BTCUSDT      3m         49992.89     49977.24    53.44       145.36
ETHUSDT      3m          3006.60      3018.54    44.54       151.85
BTCUSDT      4h         50209.51     50063.61    49.92       718.51
ETHUSDT      4h          3242.76      2963.92    48.03       653.59
```

## 🧪 运行测试

### 基础功能测试
```bash
python3 test_basic.py
```

### 完整测试套件
```bash
python3 run_tests.py
```

### 使用 pytest（需单独安装）
```bash
# 安装 pytest
pip install pytest

# 运行测试
pytest tests/ -v
```

## ⚙️ 配置自定义

编辑 `config.py` 文件：

```python
# 更改更新间隔（秒）
UPDATE_INTERVAL = 180  # 3分钟

# 更改监控的交易对
SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']

# 更改技术指标参数
INDICATOR_PARAMS = {
    'ema_short': 20,
    'ema_long': 50,
    'rsi_short': 7,
    'rsi_long': 14,
    'atr_short': 3,
    'atr_long': 14
}
```

## 📁 数据库结构

系统使用 SQLite 数据库存储数据，主要表：

1. **klines_3m** - 3 分钟 K 线数据
2. **klines_4h** - 4 小时 K 线数据
3. **technical_indicators** - 技术指标数据
4. **perpetual_data** - 永续合约数据

默认数据库文件：`market_data.db`

## 🔍 故障排除

### 1. 依赖安装失败
```bash
# 使用国内镜像源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt
```

### 2. 网络连接问题
确保网络可以访问 Binance API：
- 临时网络问题：等待几分钟后重试
- 防火墙问题：检查网络代理设置

### 3. 数据库锁定
如果遇到数据库锁定错误：
- 确保没有其他进程访问数据库
- 删除 `market_data.db-wal` 和 `market_data.db-shm` 文件（如果存在）

### 4. 测试失败
```bash
# 运行基础测试查看详细错误
python3 test_basic.py

# 查看日志文件
tail -f nof1.log
```

## 📖 更多信息

- 查看 `README.md` 了解完整文档
- 查看 `CLAUDE.md` 了解代码架构
- 运行 `python3 demo.py` 查看详细演示

## 🎯 下一步计划

根据 `README.md`，未来计划包括：
- [ ] 支持更多交易所（Hyperliquid, OKX, Bybit）
- [ ] 添加更多技术指标
- [ ] 实现 WebSocket 实时数据推送
- [ ] 添加数据可视化
- [ ] 实现自动交易功能

## 📞 支持

如有问题，请：
1. 查看日志文件：`tail -f nof1.log`
2. 运行诊断：`python3 test_basic.py`
3. 检查配置：`python main.py --status`
