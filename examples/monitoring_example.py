"""
监控系统集成示例

演示如何在交易系统中集成性能监控
"""

import os
import sys
from datetime import datetime
from typing import Dict

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from monitoring.performance_monitor import PerformanceMonitor
from trading.paper_trader import PaperTrader
from models.trading_decision import TradingDecision


def main():
    """主函数 - 演示监控系统的使用"""
    print("=" * 60)
    print("性能监控系统集成示例")
    print("=" * 60)

    # 初始化组件
    monitor = PerformanceMonitor(database_path="example_monitor.db")
    paper_trader = PaperTrader(initial_balance=100000)

    print("\n1. 记录模拟交易数据...")

    # 模拟一些交易
    for i in range(5):
        decision = TradingDecision(
            action="BUY" if i % 2 == 0 else "SELL",
            confidence=75 + i * 5,
            symbol="BTCUSDT",
            entry_price=50000 + i * 1000,
            position_size=10.0,
            risk_level="MEDIUM",
            risk_score=50,
            model_source="example",
            timeframe="4h"
        )

        pnl = 100.0 * (1 if i % 2 == 0 else -1)
        llm_cost = 0.02
        total_cost = 0.03

        monitor.record_trading_metrics(
            decision=decision,
            pnl=pnl,
            execution_time=1.5,
            llm_cost=llm_cost,
            total_cost=total_cost
        )

        print(f"  交易 {i+1}: {decision.action} - PnL: ${pnl:.2f}")

    print("\n2. 记录系统指标...")

    # 记录系统指标
    monitor.record_system_metrics(
        cpu_usage=45.0,
        memory_usage=60.0,
        active_connections=5,
        response_time=0.3,
        cache_hit_rate=0.85,
        error_rate=1.5
    )

    print("  系统指标已记录")

    print("\n3. 生成性能摘要...")

    # 获取性能摘要
    summary = monitor.get_performance_summary(paper_trader)

    print(f"  总交易次数: {summary.total_trades}")
    print(f"  胜率: {summary.win_rate:.1f}%")
    print(f"  总盈亏: ${summary.total_pnl:.2f}")
    print(f"  总回报率: {summary.total_return_pct:.2f}%")
    print(f"  最大回撤: {summary.max_drawdown:.2f}%")
    print(f"  夏普比率: {summary.sharpe_ratio:.2f}")

    print("\n4. 成本分析...")

    # 获取成本分析
    cost_analysis = monitor.get_cost_analysis()

    print(f"  总成本: ${cost_analysis['total_cost']:.4f}")
    print(f"  LLM成本: ${cost_analysis['llm_cost']:.4f}")
    print(f"  其他成本: ${cost_analysis['other_cost']:.4f}")
    print(f"  平均每笔交易成本: ${cost_analysis['avg_cost_per_trade']:.4f}")

    print("\n5. 系统健康状况...")

    # 获取系统健康
    health = monitor.get_system_health()

    print(f"  状态: {health['status']}")
    print(f"  平均CPU使用率: {health['avg_cpu_usage']:.1f}%")
    print(f"  平均内存使用率: {health['avg_memory_usage']:.1f}%")
    print(f"  平均响应时间: {health['avg_response_time']:.3f}s")
    print(f"  缓存命中率: {health['avg_cache_hit_rate']:.2f}%")

    print("\n6. 告警信息...")

    # 获取告警
    alerts = monitor.get_alerts(paper_trader)

    if alerts:
        for alert in alerts:
            print(f"  [{alert['level'].upper()}] {alert['message']}")
    else:
        print("  暂无告警")

    print("\n7. 导出报告...")

    # 导出报告
    report_path = "examples/monitoring_report.json"
    monitor.export_report(report_path, paper_trader)

    print(f"  报告已导出到: {report_path}")

    print("\n" + "=" * 60)
    print("监控系统演示完成！")
    print("=" * 60)

    # 清理
    if os.path.exists("example_monitor.db"):
        os.remove("example_monitor.db")
    if os.path.exists(report_path):
        os.remove(report_path)


if __name__ == "__main__":
    main()
