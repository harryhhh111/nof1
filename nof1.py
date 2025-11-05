#!/usr/bin/env python3
"""
Nof1 量化交易系统 - 统一启动脚本

支持多种运行模式：
- 运行指定小时数（使用Binance Testnet）
- 仅启动API服务器
- 查看测试结果
- 集成测试
"""

import sys
import os
import argparse
import subprocess
import time

# 添加项目根目录
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def print_header(title):
    """打印标题"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def run_system(hours):
    """运行交易系统"""
    print_header(f"🚀 启动Nof1交易系统（{hours}小时）")

    print(f"⏰ 运行时间: {hours}小时")
    print(f"📊 预计决策: ~{int(hours * 12)} 条")
    print(f"💰 交易模式: Binance Testnet（真实API，虚拟资金）")
    print(f"🕐 开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🕐 结束时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + hours * 3600))}")

    print("\n📖 查看方式:")
    print("  • 日志: tail -f run_full_system.log")
    print("  • 决策: python3 nof1.py --view")
    print("  • Web: https://testnet.binance.vision/")
    print("  • HTML: 打开 trading_dashboard.html")

    print("\n" + "=" * 80)

    # 运行系统
    cmd = [sys.executable, "run_full_system.py", "--hours", str(hours)]
    os.system(" ".join(cmd))


def start_api():
    """启动API服务器"""
    print_header("🚀 启动API服务器")

    print("📖 API文档: http://localhost:8000/docs")
    print("🔍 健康检查: http://localhost:8000/api/v1/health")
    print("📊 决策记录: http://localhost:8000/api/v1/decisions")
    print("\n按 Ctrl+C 停止\n")

    os.system(f"{sys.executable} run_api.py")


def view_results():
    """查看结果"""
    print_header("📊 当前交易结果")

    # 1. 查看数据库记录数
    try:
        import sqlite3

        # 决策记录
        conn = sqlite3.connect('performance_monitor.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM trading_metrics')
        count = cursor.fetchone()[0]
        print(f"📈 决策记录: {count} 条")

        if count > 0:
            cursor.execute('SELECT symbol, action, confidence, pnl FROM trading_metrics ORDER BY id DESC LIMIT 5')
            rows = cursor.fetchall()
            print("\n最近5条决策:")
            for row in rows:
                print(f"  • {row[0]:10} {row[1]:6} 置信度:{row[2]:.1f}% PnL:${row[3]:.2f}")
        conn.close()
    except:
        print("⚠️  暂无决策记录")

    # 2. Testnet状态
    print("\n💰 Testnet余额:")
    os.system(f"{sys.executable} testnet_viewer.py 2>/dev/null || echo '  请先运行系统生成记录'")


def test_integration():
    """集成测试"""
    print_header("🧪 运行集成测试")
    os.system(f"{sys.executable} testnet_demo.py")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Nof1量化交易系统 - 统一启动脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 nof1.py --run 2          # 运行2小时
  python3 nof1.py --run 0.5        # 运行30分钟
  python3 nof1.py --api            # 仅启动API
  python3 nof1.py --view           # 查看结果
  python3 nof1.py --test           # 运行测试

常用:
  python3 nof1.py --run 2 && python3 nof1.py --view
        """
    )

    parser.add_argument('--run', type=float, metavar='HOURS',
                       help='运行指定小时数（使用Binance Testnet）')
    parser.add_argument('--api', action='store_true',
                       help='仅启动API服务器')
    parser.add_argument('--view', action='store_true',
                       help='查看当前结果')
    parser.add_argument('--test', action='store_true',
                       help='运行集成测试')

    args = parser.parse_args()

    # 如果没有参数，显示帮助
    if not any(vars(args).values()):
        parser.print_help()
        print("\n" + "=" * 80)
        print("💡 快速开始:")
        print("  python3 nof1.py --run 2     # 运行2小时")
        print("  python3 nof1.py --view      # 查看结果")
        print("=" * 80)
        return

    # 执行相应命令
    if args.run:
        run_system(args.run)
    elif args.api:
        start_api()
    elif args.view:
        view_results()
    elif args.test:
        test_integration()


if __name__ == '__main__':
    main()
