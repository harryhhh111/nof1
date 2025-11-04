"""
性能监控器测试

测试性能监控功能
"""

import unittest
import tempfile
import os
import sqlite3
from datetime import datetime, timedelta
import json

from monitoring.performance_monitor import (
    PerformanceMonitor,
    SystemMetrics,
    TradingMetrics,
    PerformanceSummary
)
from models.trading_decision import TradingDecision
from trading.paper_trader import PaperTrader


class TestSystemMetrics(unittest.TestCase):
    """系统指标测试"""

    def test_system_metrics_creation(self):
        """测试创建系统指标"""
        metric = SystemMetrics(
            timestamp=datetime.now(),
            cpu_usage=50.5,
            memory_usage=60.0,
            active_connections=10,
            response_time=0.25,
            cache_hit_rate=0.85,
            error_rate=2.0
        )

        self.assertEqual(metric.cpu_usage, 50.5)
        self.assertEqual(metric.memory_usage, 60.0)
        self.assertEqual(metric.active_connections, 10)


class TestTradingMetrics(unittest.TestCase):
    """交易指标测试"""

    def test_trading_metrics_creation(self):
        """测试创建交易指标"""
        metric = TradingMetrics(
            timestamp=datetime.now(),
            symbol="BTCUSDT",
            action="BUY",
            confidence=80,
            pnl=100.5,
            execution_time=1.5,
            llm_cost=0.02,
            total_cost=0.03
        )

        self.assertEqual(metric.symbol, "BTCUSDT")
        self.assertEqual(metric.action, "BUY")
        self.assertEqual(metric.confidence, 80)
        self.assertEqual(metric.pnl, 100.5)


class TestPerformanceSummary(unittest.TestCase):
    """性能摘要测试"""

    def test_performance_summary_creation(self):
        """测试创建性能摘要"""
        summary = PerformanceSummary(
            total_trades=100,
            winning_trades=60,
            losing_trades=40,
            win_rate=60.0,
            total_pnl=5000.0,
            total_return_pct=5.0,
            max_drawdown=0.1,
            sharpe_ratio=1.5,
            total_cost=100.0,
            avg_cost_per_trade=1.0,
            profit_factor=1.8,
            avg_execution_time=1.2,
            total_runtime=24.0
        )

        self.assertEqual(summary.total_trades, 100)
        self.assertEqual(summary.winning_trades, 60)
        self.assertEqual(summary.win_rate, 60.0)
        self.assertEqual(summary.total_pnl, 5000.0)


class TestPerformanceMonitor(unittest.TestCase):
    """性能监控器测试"""

    def setUp(self):
        """测试前准备"""
        # 使用临时数据库
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.database_path = self.temp_db.name
        self.temp_db.close()

        self.monitor = PerformanceMonitor(database_path=self.database_path)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.database_path):
            os.unlink(self.database_path)

    def test_init_database(self):
        """测试初始化数据库"""
        # 数据库文件应该已创建
        self.assertTrue(os.path.exists(self.database_path))

        # 检查表是否存在
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = [row[0] for row in cursor.fetchall()]

        self.assertIn('system_metrics', tables)
        self.assertIn('trading_metrics', tables)
        self.assertIn('performance_summary', tables)

        conn.close()

    def test_record_trading_metrics(self):
        """测试记录交易指标"""
        decision = TradingDecision(
            action="BUY",
            confidence=80,
            symbol="BTCUSDT",
            entry_price=50000,
            position_size=10.0,
            risk_level="MEDIUM",
            risk_score=50,
            model_source="test",
            timeframe="4h"
        )

        self.monitor.record_trading_metrics(
            decision=decision,
            pnl=100.5,
            execution_time=1.5,
            llm_cost=0.02,
            total_cost=0.03
        )

        # 检查是否记录到内存
        self.assertEqual(len(self.monitor.trading_metrics), 1)
        metric = self.monitor.trading_metrics[0]
        self.assertEqual(metric.symbol, "BTCUSDT")
        self.assertEqual(metric.action, "BUY")
        self.assertEqual(metric.pnl, 100.5)

        # 检查统计是否更新
        self.assertEqual(self.monitor.stats['total_trades'], 1)
        self.assertEqual(self.monitor.stats['total_cost'], 0.03)

    def test_record_system_metrics(self):
        """测试记录系统指标"""
        self.monitor.record_system_metrics(
            cpu_usage=50.0,
            memory_usage=60.0,
            active_connections=10,
            response_time=0.25,
            cache_hit_rate=0.85,
            error_rate=2.0
        )

        # 检查是否记录到内存
        self.assertEqual(len(self.monitor.system_metrics), 1)
        metric = self.monitor.system_metrics[0]
        self.assertEqual(metric.cpu_usage, 50.0)
        self.assertEqual(metric.memory_usage, 60.0)
        self.assertEqual(metric.active_connections, 10)

    def test_get_performance_summary(self):
        """测试获取性能摘要"""
        paper_trader = PaperTrader(initial_balance=100000)

        # 先添加一些交易数据
        for i in range(10):
            decision = TradingDecision(
                action="BUY" if i % 2 == 0 else "SELL",
                confidence=80,
                symbol="BTCUSDT",
                position_size=10.0,
                risk_level="MEDIUM",
                risk_score=50,
                model_source="test",
                timeframe="4h"
            )

            pnl = 100.0 if i % 2 == 0 else -50.0
            self.monitor.record_trading_metrics(
                decision=decision,
                pnl=pnl,
                execution_time=1.0,
                llm_cost=0.02,
                total_cost=0.03
            )

        summary = self.monitor.get_performance_summary(paper_trader)

        self.assertEqual(summary.total_trades, 10)
        self.assertEqual(summary.winning_trades, 5)
        self.assertEqual(summary.losing_trades, 5)
        self.assertEqual(summary.win_rate, 50.0)
        self.assertEqual(summary.total_pnl, 250.0)

    def test_get_recent_trades(self):
        """测试获取最近交易记录"""
        # 添加多条交易记录
        for i in range(5):
            decision = TradingDecision(
                action="BUY",
                confidence=80,
                symbol="BTCUSDT",
                position_size=10.0,
                risk_level="MEDIUM",
                risk_score=50,
                model_source="test",
                timeframe="4h"
            )

            self.monitor.record_trading_metrics(
                decision=decision,
                pnl=100.0,
                execution_time=1.0,
                llm_cost=0.02,
                total_cost=0.03
            )

        # 获取最近3条记录
        recent = self.monitor.get_recent_trades(limit=3)
        self.assertEqual(len(recent), 3)
        self.assertEqual(recent[0]['symbol'], "BTCUSDT")

    def test_get_cost_analysis(self):
        """测试成本分析"""
        # 添加交易记录
        for i in range(3):
            decision = TradingDecision(
                action="BUY",
                confidence=80,
                symbol="BTCUSDT",
                position_size=10.0,
                risk_level="MEDIUM",
                risk_score=50,
                model_source="test",
                timeframe="4h"
            )

            llm_cost = 0.02
            total_cost = 0.05

            self.monitor.record_trading_metrics(
                decision=decision,
                pnl=100.0,
                execution_time=1.0,
                llm_cost=llm_cost,
                total_cost=total_cost
            )

        analysis = self.monitor.get_cost_analysis()

        self.assertIn('total_cost', analysis)
        self.assertIn('llm_cost', analysis)
        self.assertIn('other_cost', analysis)
        self.assertIn('avg_cost_per_trade', analysis)
        self.assertIn('cost_breakdown', analysis)

        self.assertAlmostEqual(analysis['total_cost'], 0.15, places=6)
        self.assertAlmostEqual(analysis['llm_cost'], 0.06, places=6)
        self.assertAlmostEqual(analysis['other_cost'], 0.09, places=6)

    def test_get_system_health(self):
        """测试获取系统健康状况"""
        # 添加健康指标数据
        for i in range(5):
            self.monitor.record_system_metrics(
                cpu_usage=50.0 + i,
                memory_usage=60.0 + i,
                active_connections=10,
                response_time=0.25,
                cache_hit_rate=0.85,
                error_rate=2.0
            )

        health = self.monitor.get_system_health()

        self.assertIn('status', health)
        self.assertIn('avg_cpu_usage', health)
        self.assertIn('avg_memory_usage', health)
        self.assertIn('avg_response_time', health)
        self.assertIn('avg_cache_hit_rate', health)
        self.assertIn('avg_error_rate', health)

        # CPU和内存使用率应该在合理范围内
        self.assertGreater(health['avg_cpu_usage'], 0)
        self.assertGreater(health['avg_memory_usage'], 0)

    def test_get_alerts(self):
        """测试获取告警信息"""
        paper_trader = PaperTrader(initial_balance=100000)

        # 添加一些交易记录（胜率较低）
        for i in range(15):
            decision = TradingDecision(
                action="SELL",  # 大部分是亏损交易
                confidence=80,
                symbol="BTCUSDT",
                position_size=10.0,
                risk_level="MEDIUM",
                risk_score=50,
                model_source="test",
                timeframe="4h"
            )

            pnl = -100.0  # 全部亏损

            self.monitor.record_trading_metrics(
                decision=decision,
                pnl=pnl,
                execution_time=1.0,
                llm_cost=0.02,
                total_cost=0.03
            )

        alerts = self.monitor.get_alerts(paper_trader)

        # 应该有胜率过低的告警
        self.assertTrue(len(alerts) > 0)
        alert_messages = [alert['message'] for alert in alerts]
        self.assertTrue(
            any('胜率过低' in msg for msg in alert_messages)
        )

    def test_export_report(self):
        """测试导出报告"""
        paper_trader = PaperTrader(initial_balance=100000)

        # 添加一些测试数据
        decision = TradingDecision(
            action="BUY",
            confidence=80,
            symbol="BTCUSDT",
            position_size=10.0,
            risk_level="MEDIUM",
            risk_score=50,
            model_source="test",
            timeframe="4h"
        )

        self.monitor.record_trading_metrics(
            decision=decision,
            pnl=100.0,
            execution_time=1.0,
            llm_cost=0.02,
            total_cost=0.03
        )

        # 导出报告
        temp_report = tempfile.NamedTemporaryFile(
            delete=False,
            suffix='.json',
            mode='w'
        )
        report_path = temp_report.name
        temp_report.close()

        try:
            self.monitor.export_report(report_path, paper_trader)

            # 检查文件是否创建
            self.assertTrue(os.path.exists(report_path))

            # 验证报告内容
            with open(report_path, 'r', encoding='utf-8') as f:
                report = json.load(f)

            self.assertIn('timestamp', report)
            self.assertIn('performance_summary', report)
            self.assertIn('cost_analysis', report)
            self.assertIn('system_health', report)
            self.assertIn('recent_trades', report)

        finally:
            if os.path.exists(report_path):
                os.unlink(report_path)


class TestDatabaseOperations(unittest.TestCase):
    """数据库操作测试"""

    def setUp(self):
        """测试前准备"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.database_path = self.temp_db.name
        self.temp_db.close()

        self.monitor = PerformanceMonitor(database_path=self.database_path)

    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.database_path):
            os.unlink(self.database_path)

    def test_save_and_retrieve_trading_metrics(self):
        """测试保存和检索交易指标"""
        decision = TradingDecision(
            action="BUY",
            confidence=80,
            symbol="BTCUSDT",
            position_size=10.0,
            risk_level="MEDIUM",
            risk_score=50,
            model_source="test",
            timeframe="4h"
        )

        self.monitor.record_trading_metrics(
            decision=decision,
            pnl=100.0,
            execution_time=1.0,
            llm_cost=0.02,
            total_cost=0.03
        )

        # 直接查询数据库验证
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trading_metrics")
        rows = cursor.fetchall()
        conn.close()

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][2], "BTCUSDT")  # symbol
        self.assertEqual(rows[0][3], "BUY")  # action

    def test_save_and_retrieve_system_metrics(self):
        """测试保存和检索系统指标"""
        self.monitor.record_system_metrics(
            cpu_usage=50.0,
            memory_usage=60.0,
            active_connections=10,
            response_time=0.25,
            cache_hit_rate=0.85,
            error_rate=2.0
        )

        # 直接查询数据库验证
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM system_metrics")
        rows = cursor.fetchall()
        conn.close()

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][2], 50.0)  # cpu_usage
        self.assertEqual(rows[0][3], 60.0)  # memory_usage


if __name__ == '__main__':
    unittest.main()
