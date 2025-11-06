# Nof1 数据获取与交易系统 - 快速启动指南

## ✅ 已完成的工作

### 1. 系统实现
- ✅ 完整的模块化架构实现
- ✅ 数据获取模块（支持 Binance via CCXT）
- ✅ 技术指标计算（EMA, MACD, RSI, ATR）
- ✅ SQLite 数据库存储
- ✅ 定时调度器
- ✅ 命令行接口
- ✅ **Binance Testnet 真实交易集成**
- ✅ **纸交易和真实交易模式切换**
- ✅ **智能订单管理（市价单、限价单、止损止盈）**

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

### 第三步：启动交易系统（推荐方式）

#### 使用 start_nof1.sh（抗断连启动）
```bash
# 启动2小时交易系统（后台运行，终端可断开）
./start_nof1.sh start 2

# 查看状态
./start_nof1.sh status

# 停止系统
./start_nof1.sh stop
```

**优势**：
- ✅ 终端断开后继续运行
- ✅ PID文件管理，防止重复启动
- ✅ 日志分离，便于调试
- ✅ 优雅停止

#### 使用 nof1.py 统一启动器
```bash
# 前台运行2小时
python3 nof1.py --run 2

# 仅启动API服务器
python3 nof1.py --api

# 查看结果
python3 nof1.py --view
```

### 第四步：获取实时数据（传统方式）
```bash
# 获取单个交易对数据（JSON 格式）
python main.py --symbol BTCUSDT

# 获取多个交易对数据
python main.py --symbols BTCUSDT ETHUSDT SOLUSDT

# 以可读格式输出
python main.py --symbol BTCUSDT --output print
```

### 第五步：启动持续数据获取
```bash
# 启动定时调度器（默认每 3 分钟更新一次）
python main.py --schedule

# 自定义间隔和交易对
python main.py --schedule --symbols BTCUSDT ETHUSDT --interval 60
```

### 第六步：查看系统状态
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
python3 scripts/quick_query.py summary

# 查看技术指标
python3 scripts/quick_query.py indicators

# 查看 K 线数据
python3 scripts/quick_query.py klines

# 交互式数据库浏览器
python3 view_database.py

# 数据库演示和示例
python3 demo_database.py
```

### 第八步：Binance Testnet 真实交易（新增）

#### 8.1 获取 Testnet API Key

1. 访问：https://testnet.binance.vision/
2. 使用 GitHub 账号登录
3. 复制显示的 API Key 和 Secret Key

#### 8.2 配置环境

**创建 `.env` 文件（推荐）：**
```bash
TESTNET_API_KEY=your_testnet_api_key_here
TESTNET_SECRET_KEY=your_testnet_secret_key_here
USE_TESTNET=true
```

**或设置环境变量：**
```bash
export TESTNET_API_KEY="your_api_key"
export TESTNET_SECRET_KEY="your_secret_key"
export USE_TESTNET="true"
```

#### 8.3 验证 Testnet 连接

```bash
# 运行完整测试
python3 testnet_demo.py

# 查看持仓和交易
python3 testnet_viewer.py
```

#### 8.4 执行真实交易

**Python 代码示例：**
```python
from trading.real_trader import RealTrader

# 初始化交易器
trader = RealTrader()

# 查看余额
balance = trader.get_account_balance()
print(f"USDT余额: {balance.get('USDT', 0)}")

# 获取价格
btc_price = trader.get_symbol_price('BTCUSDT')
print(f"BTC价格: ${btc_price:,.2f}")

# 小仓位测试（1%资金）
test_amount = 100.0  # $100 USDT
btc_amount = test_amount / btc_price

result = trader.place_market_order(
    symbol='BTCUSDT',
    side='buy',
    amount=btc_amount,
    reason="Testnet测试交易"
)

print(f"交易结果: {result}")

trader.close()
```

#### 8.5 查看交易记录

**命令行查看：**
```bash
python3 testnet_viewer.py
```

**Web 界面查看（推荐）：**
访问：https://testnet.binance.vision/

- Portfolio：查看余额和价值
- Orders：查看挂单
- Trade History：查看历史交易
- Fills：查看成交记录

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
python3 scripts/quick_query.py summary

# 查看技术指标
python3 scripts/quick_query.py indicators

# 查看 K 线数据
python3 scripts/quick_query.py klines

# 查看永续合约数据
python3 scripts/quick_query.py perp
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

## 🔄 交易模式切换

### 模式 1：纸交易（虚拟资金）
```python
# config.py
USE_TESTNET = False  # 关闭Testnet
# 使用虚拟100,000 USDT，完全安全
```

### 模式 2：Testnet（推荐测试）
```python
# .env 或环境变量
USE_TESTNET=true
TESTNET_API_KEY=your_key
TESTNET_SECRET_KEY=your_secret

# config.py
USE_TESTNET = True
# 使用真实API + 虚拟资金，接近实盘体验
```

### 模式 3：实盘交易（高风险！）
```python
# .env
BINANCE_API_KEY=real_api_key
BINANCE_SECRET_KEY=real_secret
USE_TESTNET=false

# config.py
USE_TESTNET = False
CURRENT_MODE = 'live'
# ⚠️ 真实资金，高风险！务必先在Testnet充分测试
```

## 🎯 下一步计划

已完成：
- [x] ✅ Binance Testnet 集成
- [x] ✅ 真实交易执行器
- [x] ✅ 多种订单类型支持

未来计划：
- [ ] 支持更多交易所（Hyperliquid, OKX, Bybit）
- [ ] 添加更多技术指标
- [ ] 实现 WebSocket 实时数据推送
- [ ] 添加数据可视化
- [ ] 实现 LLM 驱动的自动交易功能

## 📞 支持

如有问题，请：
1. 查看日志文件：`tail -f nof1.log`
2. 运行诊断：`python3 test_basic.py`
3. 检查配置：`python main.py --status`
