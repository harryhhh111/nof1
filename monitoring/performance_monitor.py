"""
性能监控模块

实时监控系统性能、交易表现和成本
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import sqlite3
from collections import defaultdict, deque
import statistics

from models.trading_decision import TradingDecision
from trading.paper_trader import PaperTrader
from scheduling.decision_cache import DecisionCache


@dataclass
class SystemMetrics:
    """系统指标"""

    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    active_connections: int
    response_time: float
    cache_hit_rate: float
    error_rate: float


@dataclass
class TradingMetrics:
    """交易指标"""

    timestamp: datetime
    symbol: str
    action: str
    confidence: float
    pnl: float
    execution_time: float
    llm_cost: float
    total_cost: float


@dataclass
class PerformanceSummary:
    """性能摘要"""

    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    total_return_pct: float
    max_drawdown: float
    sharpe_ratio: float
    total_cost: float
    avg_cost_per_trade: float
    profit_factor: float
    avg_execution_time: float
    total_runtime: float  # 小时


class PerformanceMonitor:
    """
    性能监控器

    功能：
    - 实时监控系统性能
    - 跟踪交易表现
    - 成本分析
    - 生成报告
    """

    def __init__(
        self,
        database_path: str = "performance_monitor.db",
        window_size: int = 1000  # 滑动窗口大小
    ):
        """
        初始化性能监控器

        Args:
            database_path: 数据库路径
            window_size: 滑动窗口大小
        """
        self.database_path = database_path
        self.window_size = window_size

        # 内存缓存（最近的数据）
        self.trading_metrics: deque = deque(maxlen=window_size)
        self.system_metrics: deque = deque(maxlen=window_size)

        # 统计数据
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_cost': 0.0,
            'total_trades': 0,
            'start_time': datetime.now()
        }

        # 初始化数据库
        self._init_database()

    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        # 创建系统指标表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                cpu_usage REAL,
                memory_usage REAL,
                active_connections INTEGER,
                response_time REAL,
                cache_hit_rate REAL,
                error_rate REAL
            )
        ''')

        # 创建交易指标表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trading_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                symbol TEXT,
                action TEXT,
                confidence REAL,
                pnl REAL,
                execution_time REAL,
                llm_cost REAL,
                total_cost REAL
            )
        ''')

        # 创建性能摘要表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                total_trades INTEGER,
                winning_trades INTEGER,
                losing_trades INTEGER,
                win_rate REAL,
                total_pnl REAL,
                total_return_pct REAL,
                max_drawdown REAL,
                sharpe_ratio REAL,
                total_cost REAL,
                avg_cost_per_trade REAL,
                profit_factor REAL,
                avg_execution_time REAL,
                total_runtime REAL
            )
        ''')

        conn.commit()
        conn.close()

    def record_trading_metrics(
        self,
        decision: TradingDecision,
        pnl: float,
        execution_time: float,
        llm_cost: float,
        total_cost: float
    ):
        """
        记录交易指标

        Args:
            decision: 交易决策
            pnl: 盈亏
            execution_time: 执行时间
            llm_cost: LLM成本
            total_cost: 总成本
        """
        metric = TradingMetrics(
            timestamp=datetime.now(),
            symbol=decision.symbol or "UNKNOWN",
            action=decision.action,
            confidence=decision.confidence,
            pnl=pnl,
            execution_time=execution_time,
            llm_cost=llm_cost,
            total_cost=total_cost
        )

        self.trading_metrics.append(metric)

        # 保存到数据库
        self._save_trading_metric(metric)

        # 更新统计
        self.stats['total_trades'] += 1
        self.stats['total_cost'] += total_cost

        if pnl > 0:
            self.stats['successful_requests'] += 1
        else:
            self.stats['failed_requests'] += 1

    def record_system_metrics(
        self,
        cpu_usage: float,
        memory_usage: float,
        active_connections: int,
        response_time: float,
        cache_hit_rate: float,
        error_rate: float
    ):
        """
        记录系统指标

        Args:
            cpu_usage: CPU使用率
            memory_usage: 内存使用率
            active_connections: 活跃连接数
            response_time: 响应时间
            cache_hit_rate: 缓存命中率
            error_rate: 错误率
        """
        metric = SystemMetrics(
            timestamp=datetime.now(),
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            active_connections=active_connections,
            response_time=response_time,
            cache_hit_rate=cache_hit_rate,
            error_rate=error_rate
        )

        self.system_metrics.append(metric)

        # 保存到数据库
        self._save_system_metric(metric)

    def get_performance_summary(
        self,
        paper_trader: PaperTrader,
        price_data: Optional[Dict[str, float]] = None
    ) -> PerformanceSummary:
        """
        获取性能摘要

        Args:
            paper_trader: 纸交易执行器
            price_data: 当前价格数据

        Returns:
            性能摘要
        """
        # 计算交易统计
        trades = list(self.trading_metrics)
        if not trades:
            return PerformanceSummary(
                total_trades=0, winning_trades=0, losing_trades=0, win_rate=0,
                total_pnl=0, total_return_pct=0, max_drawdown=0, sharpe_ratio=0,
                total_cost=0, avg_cost_per_trade=0, profit_factor=0,
                avg_execution_time=0, total_runtime=0
            )

        total_trades = len(trades)
        winning_trades = sum(1 for t in trades if t.pnl > 0)
        losing_trades = total_trades - winning_trades
        win_rate = winning_trades / total_trades * 100 if total_trades > 0 else 0

        total_pnl = sum(t.pnl for t in trades)
        total_cost = sum(t.total_cost for t in trades)

        # 从纸交易获取组合指标
        if price_data:
            pnl_metrics = paper_trader.get_pnl(price_data)
            performance_metrics = paper_trader.get_performance_metrics()
        else:
            pnl_metrics = {'total_pnl': total_pnl, 'total_return_pct': 0}
            performance_metrics = {'max_drawdown': 0, 'total_trades': total_trades}

        # 计算其他指标
        avg_cost_per_trade = total_cost / total_trades if total_trades > 0 else 0

        # 盈亏比
        winning_pnls = [t.pnl for t in trades if t.pnl > 0]
        losing_pnls = [t.pnl for t in trades if t.pnl < 0]
        avg_win = statistics.mean(winning_pnls) if winning_pnls else 0
        avg_loss = abs(statistics.mean(losing_pnls)) if losing_pnls else 0
        profit_factor = (avg_win * len(winning_pnls)) / (avg_loss * len(losing_pnls)) if avg_loss > 0 else 0

        # 平均执行时间
        avg_execution_time = statistics.mean([t.execution_time for t in trades])

        # 运行时间
        total_runtime = (datetime.now() - self.stats['start_time']).total_seconds() / 3600

        # 夏普比率（简化）
        returns = [t.pnl for t in trades]
        sharpe_ratio = 0
        if len(returns) > 1 and statistics.stdev(returns) > 0:
            mean_return = statistics.mean(returns)
            sharpe_ratio = mean_return / statistics.stdev(returns) * statistics.sqrt(365)

        summary = PerformanceSummary(
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            total_pnl=total_pnl,
            total_return_pct=pnl_metrics.get('total_return_pct', 0),
            max_drawdown=performance_metrics.get('max_drawdown', 0),
            sharpe_ratio=sharpe_ratio,
            total_cost=total_cost,
            avg_cost_per_trade=avg_cost_per_trade,
            profit_factor=profit_factor,
            avg_execution_time=avg_execution_time,
            total_runtime=total_runtime
        )

        # 保存摘要到数据库
        self._save_performance_summary(summary)

        return summary

    def get_recent_trades(self, limit: int = 100) -> List[Dict]:
        """
        获取最近交易记录

        Args:
            limit: 限制数量

        Returns:
            交易记录列表
        """
        recent = list(self.trading_metrics)[-limit:]
        return [t.__dict__ for t in recent]

    def get_cost_analysis(self) -> Dict[str, Any]:
        """
        获取成本分析

        Returns:
            成本分析
        """
        trades = list(self.trading_metrics)
        if not trades:
            return {}

        total_cost = sum(t.total_cost for t in trades)
        llm_cost = sum(t.llm_cost for t in trades)
        other_cost = total_cost - llm_cost

        # 按模型分组的成本
        model_costs = defaultdict(float)
        for trade in trades:
            # 这里简化处理，实际应该从决策中获取模型信息
            model_costs['deepseek'] += trade.llm_cost / 2  # 假设两个模型平分
            model_costs['qwen'] += trade.llm_cost / 2

        return {
            'total_cost': total_cost,
            'llm_cost': llm_cost,
            'other_cost': other_cost,
            'avg_cost_per_trade': total_cost / len(trades),
            'cost_breakdown': dict(model_costs),
            'cost_per_hour': total_cost / max(1, (datetime.now() - self.stats['start_time']).total_seconds() / 3600)
        }

    def get_system_health(self) -> Dict[str, Any]:
        """
        获取系统健康状况

        Returns:
            系统健康状况
        """
        if not self.system_metrics:
            return {'status': 'no_data'}

        recent = list(self.system_metrics)[-10:]  # 最近10个指标

        avg_cpu = statistics.mean([m.cpu_usage for m in recent])
        avg_memory = statistics.mean([m.memory_usage for m in recent])
        avg_response_time = statistics.mean([m.response_time for m in recent])
        avg_cache_hit_rate = statistics.mean([m.cache_hit_rate for m in recent])
        avg_error_rate = statistics.mean([m.error_rate for m in recent])

        # 判断健康状况
        if avg_cpu > 80 or avg_memory > 80:
            status = 'warning'
        elif avg_error_rate > 5:
            status = 'critical'
        else:
            status = 'healthy'

        return {
            'status': status,
            'avg_cpu_usage': avg_cpu,
            'avg_memory_usage': avg_memory,
            'avg_response_time': avg_response_time,
            'avg_cache_hit_rate': avg_cache_hit_rate,
            'avg_error_rate': avg_error_rate,
            'active_connections': recent[-1].active_connections if recent else 0
        }

    def _save_trading_metric(self, metric: TradingMetrics):
        """保存交易指标到数据库"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO trading_metrics
            (timestamp, symbol, action, confidence, pnl, execution_time, llm_cost, total_cost)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            metric.timestamp.isoformat(),
            metric.symbol,
            metric.action,
            metric.confidence,
            metric.pnl,
            metric.execution_time,
            metric.llm_cost,
            metric.total_cost
        ))
        conn.commit()
        conn.close()

    def _save_system_metric(self, metric: SystemMetrics):
        """保存系统指标到数据库"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO system_metrics
            (timestamp, cpu_usage, memory_usage, active_connections, response_time, cache_hit_rate, error_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            metric.timestamp.isoformat(),
            metric.cpu_usage,
            metric.memory_usage,
            metric.active_connections,
            metric.response_time,
            metric.cache_hit_rate,
            metric.error_rate
        ))
        conn.commit()
        conn.close()

    def _save_performance_summary(self, summary: PerformanceSummary):
        """保存性能摘要到数据库"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO performance_summary
            (timestamp, total_trades, winning_trades, losing_trades, win_rate, total_pnl,
             total_return_pct, max_drawdown, sharpe_ratio, total_cost, avg_cost_per_trade,
             profit_factor, avg_execution_time, total_runtime)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            summary.total_trades,
            summary.winning_trades,
            summary.losing_trades,
            summary.win_rate,
            summary.total_pnl,
            summary.total_return_pct,
            summary.max_drawdown,
            summary.sharpe_ratio,
            summary.total_cost,
            summary.avg_cost_per_trade,
            summary.profit_factor,
            summary.avg_execution_time,
            summary.total_runtime
        ))
        conn.commit()
        conn.close()

    def export_report(self, file_path: str, paper_trader: PaperTrader):
        """
        导出性能报告

        Args:
            file_path: 文件路径
            paper_trader: 纸交易执行器
        """
        summary = self.get_performance_summary(paper_trader)
        cost_analysis = self.get_cost_analysis()
        system_health = self.get_system_health()

        report = {
            'timestamp': datetime.now().isoformat(),
            'performance_summary': summary.__dict__,
            'cost_analysis': cost_analysis,
            'system_health': system_health,
            'recent_trades': self.get_recent_trades(20),
            'statistics': self.stats
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)

    def get_alerts(self, paper_trader: PaperTrader) -> List[Dict[str, Any]]:
        """
        获取告警信息

        Args:
            paper_trader: 纸交易执行器

        Returns:
            告警列表
        """
        alerts = []

        # 检查系统健康
        health = self.get_system_health()
        if health['status'] == 'critical':
            alerts.append({
                'level': 'critical',
                'message': f"系统错误率过高: {health['avg_error_rate']:.2f}%",
                'timestamp': datetime.now().isoformat()
            })
        elif health['status'] == 'warning':
            alerts.append({
                'level': 'warning',
                'message': f"系统资源使用率过高: CPU {health['avg_cpu_usage']:.1f}%, 内存 {health['avg_memory_usage']:.1f}%",
                'timestamp': datetime.now().isoformat()
            })

        # 检查成本
        cost_analysis = self.get_cost_analysis()
        cost_per_hour = cost_analysis.get('cost_per_hour', 0)
        if cost_per_hour > 10:  # 每小时成本超过10美元
            alerts.append({
                'level': 'warning',
                'message': f"LLM成本过高: ${cost_per_hour:.2f}/小时",
                'timestamp': datetime.now().isoformat()
            })

        # 检查胜率
        summary = self.get_performance_summary(paper_trader)
        if summary.total_trades > 10 and summary.win_rate < 40:
            alerts.append({
                'level': 'warning',
                'message': f"交易胜率过低: {summary.win_rate:.1f}%",
                'timestamp': datetime.now().isoformat()
            })

        return alerts
