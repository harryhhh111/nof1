# 交易监控脚本使用指南

## 📋 脚本列表

### 1. check_trading.sh - 快速状态检查
```bash
./scripts/check_trading.sh
```
- 查看系统进程状态
- Testnet余额
- 最新数据时间
- 快速摘要信息

### 2. monitor_trading.sh - 定期监控
```bash
./scripts/monitor_trading.sh
```
- 每5分钟自动刷新
- 终端界面监控
- 实时更新数据

## 🚀 常用命令

### 日常检查
```bash
# 快速查看
./scripts/check_trading.sh

# 查看最新数据
python3 scripts/quick_query.py summary

# 查看API状态
curl http://localhost:8000/api/v1/health
```

### 深度监控
```bash
# 启动定期监控 (终端中运行)
/scripts/monitor_trading.sh

# 实时查看日志
tail -f logs/trading_infinity.log

# 查看所有进程
ps aux | grep -E "data_collector|run_full_system|run_api"
```

### Web界面
- API文档: http://localhost:8000/docs
- Testnet: https://testnet.binance.vision/

## 📊 重要指标

### 余额监控
- USDT: 资金充足度
- BTC, ETH, SOL: 主要持仓

### 交易统计
- 总交易次数
- 胜率 (目标 >50%)
- 总PnL (盈亏)

### 数据健康
- K线记录数: 持续增长
- 最新时间: 延迟 <5分钟
- 6个交易对: 全部正常

## ⚠️ 注意事项

1. 所有脚本都在项目目录 `scripts/` 下
2. 定期监控需要终端保持开启
3. Web界面需要浏览器访问
4. Testnet是虚拟资金，无真实风险
