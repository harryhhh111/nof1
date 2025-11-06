# Nof1 Robust启动指南

## 🎯 问题：终端断连怎么办？

**问题场景**：
- SSH连接断开
- 终端关闭
- 网络中断
- 系统休眠/唤醒

**解决方案**：使用 `start_nof1.sh` 脚本，它使用 `nohup` + `setsid` 确保进程独立运行。

---

## 🚀 使用方法

### 1. 启动2小时交易系统（推荐）

```bash
cd /home/claude_user/nof1
./start_nof1.sh start 2
```

**特点**：
- ✅ 后台独立运行（终端断连不影响）
- ✅ 自动创建PID文件管理进程
- ✅ 日志分离：`logs/trading_YYYYMMDD_HHMMSS.log`
- ✅ 启动API服务器（如果未启动）

### 2. 仅启动API服务器

```bash
./start_nof1.sh start-api
```

### 3. 查看系统状态

```bash
./start_nof1.sh status
```

### 4. 停止系统

```bash
./start_nof1.sh stop
```

### 5. 重启系统

```bash
./start_nof1.sh restart
```

### 6. 查看日志

```bash
# 查看所有日志文件
./start_nof1.sh logs

# 实时查看最新日志
./start_nof1.sh logs logs/trading_YYYYMMDD_HHMMSS.log
```

### 7. 清理旧日志

```bash
# 清理超过7天的日志（默认）
./start_nof1.sh cleanup

# 清理超过3天的日志
./start_nof1.sh cleanup 3
```

---

## 🔧 工作原理

### 进程管理
```bash
# 使用setsid创建独立会话
setsid nohup command > logfile 2>&1 < /dev/null &

# 进程ID保存在pids/目录
echo $! > pids/api.pid
echo $! > pids/trading.pid
```

### 日志管理
```
logs/
├── api.log                      # API服务器日志
├── trading_20251105_163000.log  # 交易系统日志（按时间命名）
└── ...
```

### PID文件
```
pids/
├── api.pid      # API进程ID
└── trading.pid  # 交易进程ID
```

---

## 🛡️ 抗断连特性

### 1. **setsid**
- 创建新会话，脱离父进程控制
- 即使终端关闭，进程继续运行

### 2. **nohup**
- 忽略SIGHUP信号（终端关闭信号）
- 输出重定向到日志文件

### 3. **输入重定向**
```bash
< /dev/null
```
- 防止进程等待输入
- 确保后台运行

### 4. **PID文件**
- 记录进程ID
- 防止重复启动
- 方便进程管理

---

## 📋 完整工作流示例

### 场景：运行2小时系统

**步骤1：启动系统**
```bash
$ ./start_nof1.sh start 2

================================================================================
  🚀 启动Nof1交易系统
================================================================================

[INFO] ✅ 依赖检查完成
[INFO] 启动API服务器...
[INFO] ✅ API服务器已启动 (PID: 12345)
[INFO] 📖 API文档: http://localhost:8000/docs
[INFO] 📝 日志: logs/api.log

[INFO] 后台启动交易系统...
[INFO] ✅ 交易系统已启动 (PID: 12346)
[INFO] 📝 日志文件: logs/trading_20251105_163000.log
[INFO]
[INFO] 📖 监控方式:
[INFO]   • 实时日志: tail -f logs/trading_20251105_163000.log
[INFO]   • 查看结果: ./start_nof1.sh status
[INFO]   • Web界面: https://testnet.binance.vision/
[INFO]
[INFO] 🛑 停止系统: ./start_nof1.sh stop

================================================================================
  📊 系统状态
================================================================================

[INFO] ✅ API服务器: 运行中 (PID: 12345)
[INFO]    📖 文档: http://localhost:8000/docs
[INFO] ✅ 交易系统: 运行中 (PID: 12346)
[INFO]    💰 模式: Binance Testnet
```

**步骤2：可以安全关闭终端**
```bash
exit  # 终端断开，系统继续运行
```

**步骤3：重新连接后查看状态**
```bash
$ ./start_nof1.sh status

================================================================================
  📊 系统状态
================================================================================

[INFO] ✅ API服务器: 运行中 (PID: 12345)
[INFO]    📖 文档: http://localhost:8000/docs
[INFO] ✅ 交易系统: 运行中 (PID: 12346)
[INFO]    💰 模式: Binance Testnet
[INFO]
[INFO] 📝 最新日志:
[INFO] ----------------------------------------
[INFO] 2025-11-05 16:35:12 - INFO - 生成模拟LLM决策...
[INFO] ✅ BTCUSDT: BUY 10.5% (置信度: 78.3%)
[INFO] ✅ ETHUSDT: HOLD 8.2% (置信度: 82.1%)
[INFO] ✅ SOLUSDT: BUY 12.7% (置信度: 75.9%)
[INFO] ----------------------------------------
[INFO]
[INFO] 📈 交易统计:
[INFO]    决策记录: 12 条
```

**步骤4：停止系统**
```bash
$ ./start_nof1.sh stop

================================================================================
  🛑 停止Nof1系统
================================================================================

[INFO] 停止交易系统 (PID: 12346)...
[INFO] ✅ 交易系统已停止
[INFO] 停止API服务器 (PID: 12345)...
[INFO] ✅ API服务器已停止
```

---

## 🔍 故障排除

### 1. 进程未启动
```bash
# 检查日志
./start_nof1.sh logs logs/trading_YYYYMMDD_HHMMSS.log

# 查看系统状态
./start_nof1.sh status
```

### 2. 端口被占用
```bash
# 检查端口占用
lsof -i :8000

# 或查看进程
ps aux | grep run_api
```

### 3. PID文件存在但进程不运行
```bash
# 清理PID文件
rm pids/*.pid

# 重新启动
./start_nof1.sh start 2
```

### 4. 日志过大
```bash
# 清理超过30天的日志
./start_nof1.sh cleanup 30

# 或手动删除
rm logs/*.log
```

---

## 🎯 最佳实践

### 1. 启动时
- ✅ 使用脚本启动，不直接运行Python脚本
- ✅ 检查日志确认启动成功
- ✅ 确认PID文件已创建

### 2. 运行中
- ✅ 使用 `./start_nof1.sh status` 查看状态
- ✅ 实时查看日志：`tail -f logs/trading_*.log`
- ✅ 监控系统资源：`top` 或 `htop`

### 3. 停止时
- ✅ 使用 `./start_nof1.sh stop` 优雅停止
- ✅ 不要直接 `kill` 进程
- ✅ 确认PID文件已清理

### 4. 维护时
- ✅ 定期清理旧日志（默认7天）
- ✅ 监控磁盘空间
- ✅ 备份重要数据

---

## 📚 相关文件

- **启动脚本**：`start_nof1.sh`
- **统一启动**：`nof1.py`
- **API服务器**：`run_api.py`
- **交易系统**：`run_full_system.py`
- **HTML面板**：`trading_dashboard.html`
- **配置**：`config.py`, `.env`

---

## ⚡ 快速参考

| 任务 | 命令 |
|------|------|
| 启动2小时 | `./start_nof1.sh start 2` |
| 查看状态 | `./start_nof1.sh status` |
| 停止系统 | `./start_nof1.sh stop` |
| 查看日志 | `./start_nof1.sh logs` |
| 重启 | `./start_nof1.sh restart` |
| 帮助 | `./start_nof1.sh help` |

---

**💡 提示**：脚本会处理所有断连问题，让你安心运行系统！🚀
