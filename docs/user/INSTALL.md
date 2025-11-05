# Nof1 数据获取系统 - 安装和使用说明

## 📦 依赖安装

### 方式 1：使用 pip 直接安装
```bash
pip install -r requirements.txt
```

### 方式 2：使用国内镜像源（推荐）
如果网络较慢，可以使用国内镜像源：
```bash
# 清华镜像源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt

# 阿里云镜像源
pip install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

# 腾讯云镜像源
pip install -i https://mirrors.cloud.tencent.com/pypi/simple/ -r requirements.txt
```

### 方式 3：分步安装
```bash
# 核心依赖
pip install ccxt pandas numpy schedule requests python-dotenv
```

### 验证安装
```bash
python3 -c "import ccxt, pandas, numpy; print('所有依赖安装成功！')"
```

## 🚀 快速开始

### 第一步：安装依赖（见上方）

### 第二步：运行基础测试
```bash
python3 test_basic.py
```

如果看到类似输出，说明系统正常：
```
[测试 1] 验证模块导入...
✓ 所有模块导入成功

[测试 2] 创建模拟 OHLCV 数据...
✓ 创建 50 条模拟数据

[测试 3] 测试 EMA 计算...
✓ EMA20 计算成功

...

✓ 所有基础功能测试通过！
```

### 第三步：获取实时数据
```bash
# 获取 BTC 数据（JSON 格式）
python main.py --symbol BTCUSDT

# 获取多个交易对
python main.py --symbols BTCUSDT ETHUSDT SOLUSDT

# 以可读格式显示
python main.py --symbol BTCUSDT --output print
```

### 第四步：启动交易系统（推荐）

#### 使用 start_nof1.sh（抗断连）
```bash
# 启动2小时交易系统
./start_nof1.sh start 2

# 查看状态
./start_nof1.sh status

# 停止系统
./start_nof1.sh stop
```

#### 使用 nof1.py 统一启动器
```bash
# 前台运行2小时
python3 nof1.py --run 2

# 仅启动API
python3 nof1.py --api

# 查看结果
python3 nof1.py --view
```

### 第五步：启动持续监控（传统方式）
```bash
# 后台运行，每 3 分钟更新一次
python main.py --schedule
```

按 `Ctrl+C` 可以安全停止。

### 第六步：查看系统状态
```bash
python main.py --status
```

## 📊 使用示例

### 示例 1：获取 BTC 当前数据
```bash
python main.py --symbol BTCUSDT --output print
```

输出：
```
=== BTCUSDT 市场数据 ===
当前价格: $67,500.50
时间戳: 2025-11-02 10:30:00

=== 日内数据 (3分钟) ===
价格范围: $67,250.30 - $67,800.20
最新 EMA20: 67,350.15
最新 MACD: 15.30
最新 RSI7: 56.80
最新 RSI14: 54.20

=== 长期数据 (4小时) ===
EMA20: 67,200.50
EMA50: 66,800.25
ATR3: 150.75
ATR14: 285.50
当前交易量: 1,250.30
平均交易量: 1,180.45

=== 永续合约数据 ===
资金费率: 0.000150
开放利息: 50,000.00
```

### 示例 2：持续监控多个交易对
```bash
python main.py --schedule --symbols BTCUSDT ETHUSDT SOLUSDT --interval 60
```

每 60 秒更新一次，监控 BTC、ETH、SOL 三个交易对。

### 示例 3：查询历史数据
```bash
python main.py --query --symbols BTCUSDT ETHUSDT
```

从数据库查询最新保存的数据。

### 示例 4：系统状态监控
```bash
python main.py --status
```

显示数据库记录数、监控状态等信息。

### 示例 5：数据库查看（新增）
```bash
# 快速查看数据库摘要
python3 quick_query.py summary

# 查看技术指标
python3 quick_query.py indicators

# 查看 K 线数据
python3 quick_query.py klines

# 交互式数据库浏览器
python3 view_database.py

# 数据库演示工具
python3 demo_database.py
```

## 🔧 配置自定义

编辑 `config.py` 文件：

```python
# 修改更新间隔（秒）
UPDATE_INTERVAL = 180  # 3分钟

# 修改监控的交易对
SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']

# 修改技术指标参数
INDICATOR_PARAMS = {
    'ema_short': 20,
    'ema_long': 50,
    'rsi_short': 7,
    'rsi_long': 14,
    'atr_short': 3,
    'atr_long': 14
}
```

## 📝 日志文件

系统运行时会生成日志文件 `nof1.log`：

```bash
# 实时查看日志
tail -f nof1.log

# 查看最近 100 行
tail -100 nof1.log

# 搜索错误
grep ERROR nof1.log
```

## 💾 数据库

默认数据库文件：`market_data.db`

### 查看数据库
```bash
# 使用 sqlite3 命令行工具
sqlite3 market_data.db

# 查看表
.tables

# 查看 K 线数据
SELECT * FROM klines_3m LIMIT 5;
```

### 清理数据库
```bash
# 删除数据库文件
rm market_data.db

# 系统会自动重新创建
python main.py --status
```

## 🧪 测试

### 运行所有测试
```bash
python3 run_tests.py
```

### 单独运行模块测试
```bash
python3 -m unittest tests.test_config
python3 -m unittest tests.test_indicators
python3 -m unittest tests.test_database
```

### 使用 pytest（需单独安装）
```bash
pip install pytest
pytest tests/ -v
```

## ❗ 常见问题

### 1. 依赖安装失败
**问题**：`ModuleNotFoundError` 或 `pip install` 超时

**解决**：
- 使用国内镜像源：`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt`
- 或者分步安装：`pip install ccxt pandas numpy schedule requests python-dotenv`

### 2. 网络连接问题
**问题**：获取数据失败或超时

**解决**：
- 检查网络连接
- 确认可以访问 Binance API
- 等待几分钟后重试

### 3. 数据库锁定
**问题**：`database is locked`

**解决**：
- 确保没有多个实例在运行
- 停止调度器：`Ctrl+C`
- 删除临时文件：`rm market_data.db-wal market_data.db-shm`

### 4. CCXT 错误
**问题**：`ccxt` 库调用失败

**解决**：
- 重新安装：`pip install --upgrade ccxt`
- 检查 API 版本兼容性

### 5. 数据获取失败
**问题**：返回空数据或错误

**解决**：
- 检查交易对名称是否正确（如 `BTCUSDT`）
- 查看日志：`tail -f nof1.log`
- 确认网络和 API 可用性

## 📚 更多资源

- `README.md` - 完整项目文档
- `CLAUDE.md` - AI 开发指南
- `QUICKSTART.md` - 详细快速入门
- `INSTALL.md` - 安装说明（本文件）
- `PROJECT_SUMMARY.md` - 项目实现总结
- `DATABASE_GUIDE.md` - 完整数据库指南
- `demo.py` - 交互式演示
- `quick_query.py` - 快速数据库查询工具
- `view_database.py` - 交互式数据库浏览器
- `demo_database.py` - 数据库演示工具

## 🎯 下一步

安装完成后，您可以：

1. **立即测试**：`python3 test_basic.py`
2. **获取数据**：`python main.py --symbol BTCUSDT`
3. **启动监控**：`python main.py --schedule`
4. **查看演示**：`python3 demo.py`

## ✅ 验证清单

安装完成后，请确认：

- [ ] 依赖安装成功：`python3 -c "import ccxt, pandas, numpy; print('OK')"`
- [ ] 基础测试通过：`python3 test_basic.py`
- [ ] 数据获取成功：`python main.py --symbol BTCUSDT`
- [ ] 系统状态正常：`python main.py --status`

如果以上都正常，说明系统已准备就绪！

---

祝您使用愉快！ 🎉
