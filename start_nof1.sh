#!/bin/bash

###############################################################################
# Nof1 量化交易系统 - Robust启动脚本
# 支持后台运行、终端断连自动恢复、日志管理
###############################################################################

set -e  # 遇到错误立即退出

# 配置
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$PROJECT_DIR/logs"
PID_DIR="$PROJECT_DIR/pids"
PYTHON_CMD="python3"

# 创建目录
mkdir -p "$LOG_DIR" "$PID_DIR"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_header() {
    echo -e "\n${BLUE}================================================================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}================================================================================${NC}\n"
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."

    if ! command -v $PYTHON_CMD &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi

    if [ ! -f "$PROJECT_DIR/nof1.py" ]; then
        log_error "找不到 nof1.py"
        exit 1
    fi

    log_info "✅ 依赖检查完成"
}

# 启动API服务器
start_api() {
    local pid_file="$PID_DIR/api.pid"
    local log_file="$LOG_DIR/api.log"

    if [ -f "$pid_file" ]; then
        local old_pid=$(cat "$pid_file")
        if kill -0 "$old_pid" 2>/dev/null; then
            log_warn "API服务器已在运行 (PID: $old_pid)"
            return 0
        else
            log_warn "删除过期PID文件"
            rm -f "$pid_file"
        fi
    fi

    log_info "启动API服务器..."
    cd "$PROJECT_DIR"

    nohup $PYTHON_CMD run_api.py > "$log_file" 2>&1 &
    local api_pid=$!

    echo $api_pid > "$pid_file"
    sleep 2

    if kill -0 "$api_pid" 2>/dev/null; then
        log_info "✅ API服务器已启动 (PID: $api_pid)"
        log_info "📖 API文档: http://localhost:8000/docs"
        log_info "📝 日志: $log_file"
        return 0
    else
        log_error "❌ API服务器启动失败"
        return 1
    fi
}

# 启动交易系统
start_trading() {
    local hours=$1
    local pid_file="$PID_DIR/trading.pid"
    local log_file="$LOG_DIR/trading_$(date +%Y%m%d_%H%M%S).log"

    if [ -z "$hours" ] || [ "$hours" -le 0 ]; then
        log_error "请指定有效的运行小时数"
        return 1
    fi

    if [ -f "$pid_file" ]; then
        local old_pid=$(cat "$pid_file")
        if kill -0 "$old_pid" 2>/dev/null; then
            log_warn "交易系统已在运行 (PID: $old_pid)"
            log_info "要停止，请运行: $0 stop"
            return 0
        else
            log_warn "删除过期PID文件"
            rm -f "$pid_file"
        fi
    fi

    log_header "🚀 启动Nof1交易系统"
    log_info "⏰ 运行时间: $hours 小时"
    log_info "📊 预计决策: ~$((hours * 12)) 条"
    log_info "💰 交易模式: Binance Testnet"
    log_info "🕐 开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
    log_info "🕐 结束时间: $(date -d "+$hours hours" '+%Y-%m-%d %H:%M:%S')"
    echo ""

    cd "$PROJECT_DIR"

    # 使用setsid创建独立的会话，确保终端断连不影响进程
    log_info "后台启动交易系统..."
    setsid nohup $PYTHON_CMD run_full_system.py --hours "$hours" > "$log_file" 2>&1 < /dev/null &
    local trading_pid=$!

    echo $trading_pid > "$pid_file"
    sleep 2

    if kill -0 "$trading_pid" 2>/dev/null; then
        log_info "✅ 交易系统已启动 (PID: $trading_pid)"
        log_info "📝 日志文件: $log_file"
        log_info ""
        log_info "📖 监控方式:"
        log_info "  • 实时日志: tail -f $log_file"
        log_info "  • 查看结果: $0 status"
        log_info "  • Web界面: https://testnet.binance.vision/"
        log_info ""
        log_info "🛑 停止系统: $0 stop"
        echo ""

        # 等待5秒让系统初始化
        sleep 5

        # 显示当前状态
        show_status
        return 0
    else
        log_error "❌ 交易系统启动失败"
        log_error "查看日志: tail -f $log_file"
        return 1
    fi
}

# 停止系统
stop_system() {
    log_header "🛑 停止Nof1系统"

    local stopped=0

    # 停止交易系统
    if [ -f "$PID_DIR/trading.pid" ]; then
        local trading_pid=$(cat "$PID_DIR/trading.pid")
        if kill -0 "$trading_pid" 2>/dev/null; then
            log_info "停止交易系统 (PID: $trading_pid)..."
            kill "$trading_pid"
            sleep 2
            if kill -0 "$trading_pid" 2>/dev/null; then
                log_warn "强制终止交易系统..."
                kill -9 "$trading_pid"
            fi
            rm -f "$PID_DIR/trading.pid"
            log_info "✅ 交易系统已停止"
            stopped=1
        else
            log_info "交易系统未运行"
            rm -f "$PID_DIR/trading.pid"
        fi
    fi

    # 停止API服务器
    if [ -f "$PID_DIR/api.pid" ]; then
        local api_pid=$(cat "$PID_DIR/api.pid")
        if kill -0 "$api_pid" 2>/dev/null; then
            log_info "停止API服务器 (PID: $api_pid)..."
            kill "$api_pid"
            sleep 2
            if kill -0 "$api_pid" 2>/dev/null; then
                log_warn "强制终止API服务器..."
                kill -9 "$api_pid"
            fi
            rm -f "$PID_DIR/api.pid"
            log_info "✅ API服务器已停止"
            stopped=1
        else
            log_info "API服务器未运行"
            rm -f "$PID_DIR/api.pid"
        fi
    fi

    if [ $stopped -eq 0 ]; then
        log_warn "没有运行中的进程"
    fi
}

# 显示状态
show_status() {
    log_header "📊 系统状态"

    local running=0

    # API状态
    if [ -f "$PID_DIR/api.pid" ]; then
        local api_pid=$(cat "$PID_DIR/api.pid")
        if kill -0 "$api_pid" 2>/dev/null; then
            log_info "✅ API服务器: 运行中 (PID: $api_pid)"
            log_info "   📖 文档: http://localhost:8000/docs"
            running=1
        else
            log_warn "⚠️  API服务器: 已停止 (PID文件存在但进程不存在)"
            rm -f "$PID_DIR/api.pid"
        fi
    else
        log_info "⚪ API服务器: 未启动"
    fi

    # 交易系统状态
    if [ -f "$PID_DIR/trading.pid" ]; then
        local trading_pid=$(cat "$PID_DIR/trading.pid")
        if kill -0 "$trading_pid" 2>/dev/null; then
            log_info "✅ 交易系统: 运行中 (PID: $trading_pid)"
            log_info "   💰 模式: Binance Testnet"
            running=1
        else
            log_warn "⚠️  交易系统: 已停止 (PID文件存在但进程不存在)"
            rm -f "$PID_DIR/trading.pid"
        fi
    else
        log_info "⚪ 交易系统: 未启动"
    fi

    # 显示最新日志
    if [ $running -eq 1 ]; then
        echo ""
        log_info "📝 最新日志:"
        local latest_log=$(ls -t "$LOG_DIR"/*.log 2>/dev/null | head -1)
        if [ -n "$latest_log" ]; then
            echo "----------------------------------------"
            tail -n 5 "$latest_log" 2>/dev/null || echo "无法读取日志"
            echo "----------------------------------------"
        fi
    fi

    # 显示数据库统计
    if [ -f "$PROJECT_DIR/performance_monitor.db" ]; then
        echo ""
        log_info "📈 交易统计:"
        local count=$(sqlite3 "$PROJECT_DIR/performance_monitor.db" "SELECT COUNT(*) FROM trading_metrics;" 2>/dev/null || echo "0")
        log_info "   决策记录: $count 条"
    fi
}

# 重启系统
restart_system() {
    log_header "🔄 重启系统"
    stop_system
    sleep 2
    start_api
    echo ""
    show_status
}

# 查看日志
view_logs() {
    local log_file=$1

    if [ -z "$log_file" ]; then
        log_info "可用日志文件:"
        ls -lah "$LOG_DIR"/*.log 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'
        return 0
    fi

    if [ ! -f "$log_file" ]; then
        log_error "日志文件不存在: $log_file"
        return 1
    fi

    log_info "查看日志: $log_file (按 Ctrl+C 退出)"
    echo ""
    tail -f "$log_file"
}

# 清理旧日志
cleanup_logs() {
    log_header "🧹 清理旧日志"

    local days=${1:-7}
    local count=$(find "$LOG_DIR" -name "*.log" -mtime +$days | wc -l)

    if [ $count -eq 0 ]; then
        log_info "没有超过 $days 天的旧日志"
        return 0
    fi

    log_info "删除超过 $days 天的日志文件..."
    find "$LOG_DIR" -name "*.log" -mtime +$days -delete
    log_info "✅ 已清理 $count 个日志文件"
}

# 显示帮助
show_help() {
    echo ""
    echo "Nof1 量化交易系统 - Robust启动脚本"
    echo ""
    echo "用法: $0 [命令] [参数]"
    echo ""
    echo "命令:"
    echo "  start <hours>    启动系统运行指定小时数 (e.g., $0 start 2)"
    echo "  start-api        仅启动API服务器"
    echo "  stop             停止所有服务"
    echo "  restart          重启系统"
    echo "  status           显示系统状态"
    echo "  logs [file]      查看日志 (不带参数显示列表)"
    echo "  cleanup [days]   清理超过指定天数的日志 (默认7天)"
    echo "  help             显示此帮助"
    echo ""
    echo "示例:"
    echo "  $0 start 2              # 运行2小时"
    echo "  $0 start-api            # 仅启动API"
    echo "  $0 status               # 查看状态"
    echo "  $0 logs                 # 查看所有日志"
    echo "  $0 logs trading.log     # 查看特定日志"
    echo ""
}

# 主函数
main() {
    case "${1:-}" in
        start)
            check_dependencies
            start_api
            echo ""
            start_trading "$2"
            ;;
        start-api)
            check_dependencies
            start_api
            ;;
        stop)
            stop_system
            ;;
        restart)
            check_dependencies
            restart_system
            ;;
        status)
            show_status
            ;;
        logs)
            view_logs "$2"
            ;;
        cleanup)
            cleanup_logs "$2"
            ;;
        help|--help|-h)
            show_help
            ;;
        "")
            log_error "请指定命令"
            echo ""
            show_help
            exit 1
            ;;
        *)
            log_error "未知命令: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
