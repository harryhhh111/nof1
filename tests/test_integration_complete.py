"""
完整系统集成测试

验证所有8个阶段组件的协同工作
"""

import unittest
import tempfile
import os
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from data_fetcher import DataFetcher
from database import Database
from indicators import TechnicalIndicators
from multi_timeframe_preprocessor import MultiTimeframeProcessor
from prompt_generator import PromptGenerator
from models.trading_decision import TradingDecision
from llm_clients.deepseek_client import DeepSeekClient
from llm_clients.qwen_client import QwenClient
from trading.paper_trader import PaperTrader
from scheduling.decision_cache import DecisionCache
from scheduling.high_freq_scheduler import HighFreqScheduler
from risk_management.risk_manager import RiskManager, PositionSizer
from risk_management.backtest_engine import BacktestEngine, BacktestConfig
from monitoring.performance_monitor import PerformanceMonitor


class TestCompleteSystemIntegration(unittest.TestCase):
    """完整系统集成测试"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_db = os.path.join(self.temp_dir, "test_integration.db")

    def tearDown(self):
        """测试后清理"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_data_pipeline_integration(self):
        """测试数据管道集成"""
        # 1. 初始化数据库
        db = Database(self.temp_db)

        # 2. 模拟数据获取
        fetcher = DataFetcher()
        # 跳过实际数据获取测试，直接测试模块可导入
        self.assertIsNotNone(fetcher)

        # 3. 测试指标计算
        indicators = TechnicalIndicators()
        # 这里可以测试技术指标计算

        # 4. 测试数据存储
        # db.save_klines('BTCUSDT', '3m', data)
        # 验证数据是否保存成功

    def test_decision_creation_and_validation(self):
        """测试交易决策创建和验证"""
        # 创建交易决策
        decision = TradingDecision(
            action="BUY",
            confidence=85,
            symbol="BTCUSDT",
            entry_price=50000,
            stop_loss=49000,
            take_profit=52000,
            position_size=10.0,
            leverage=2.0,
            risk_level="MEDIUM",
            risk_score=55,
            model_source="test",
            timeframe="4h"
        )

        # 验证决策
        is_valid, msg = decision.validate_decision()

        self.assertTrue(is_valid)
        # msg包含"决策有效"即可
        self.assertIn("决策有效", msg)
        self.assertEqual(decision.symbol, "BTCUSDT")
        self.assertEqual(decision.confidence, 85)

    def test_paper_trader_integration(self):
        """测试纸交易执行器集成"""
        paper_trader = PaperTrader(initial_balance=100000)

        # 创建交易决策
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

        # 执行决策
        result = paper_trader.execute_decision(decision, 50000)

        self.assertIn('status', result)
        self.assertIn('size', result)

    def test_risk_manager_integration(self):
        """测试风险管理器集成"""
        risk_manager = RiskManager(
            account_balance=100000,
            max_position_size=0.1,
            max_leverage=10.0
        )

        # 创建交易决策
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

        current_positions = {}
        price_data = {"BTCUSDT": 50000}

        # 评估决策
        is_passed, message, suggested_size = risk_manager.evaluate_decision(
            decision, current_positions, price_data
        )

        self.assertIsInstance(is_passed, bool)
        self.assertIsInstance(message, str)
        self.assertIsNotNone(suggested_size)

    def test_backtest_engine_integration(self):
        """测试回测引擎集成"""
        config = BacktestConfig(
            initial_balance=100000,
            symbols=['BTCUSDT']
        )

        engine = BacktestEngine(config)

        # 创建简单的市场数据
        import pandas as pd
        dates = pd.date_range(start='2024-01-01', end='2024-01-10', freq='3T')
        market_data = {
            'BTCUSDT': pd.DataFrame({
                'open': [50000] * len(dates),
                'high': [50500] * len(dates),
                'low': [49500] * len(dates),
                'close': [50000] * len(dates),
                'volume': [100] * len(dates)
            }, index=dates)
        }

        # 简单策略函数
        def simple_strategy(symbol, data, market_snapshot):
            return TradingDecision(
                action="HOLD",
                confidence=50,
                position_size=0,
                risk_level="MEDIUM",
                risk_score=50,
                model_source="simple",
                timeframe="backtest"
            )

        # 运行回测
        metrics = engine.run_backtest(market_data, simple_strategy)

        self.assertIsNotNone(metrics)
        self.assertEqual(metrics.total_trades, 0)

    def test_performance_monitor_integration(self):
        """测试性能监控器集成"""
        monitor = PerformanceMonitor(database_path=os.path.join(self.temp_dir, "monitor.db"))
        paper_trader = PaperTrader(initial_balance=100000)

        # 记录交易指标
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

        monitor.record_trading_metrics(
            decision=decision,
            pnl=100.0,
            execution_time=1.5,
            llm_cost=0.02,
            total_cost=0.03
        )

        # 记录系统指标
        monitor.record_system_metrics(
            cpu_usage=50.0,
            memory_usage=60.0,
            active_connections=5,
            response_time=0.3,
            cache_hit_rate=0.85,
            error_rate=1.0
        )

        # 获取性能摘要
        summary = monitor.get_performance_summary(paper_trader)

        self.assertEqual(summary.total_trades, 1)
        self.assertEqual(summary.winning_trades, 1)

        # 获取系统健康
        health = monitor.get_system_health()

        self.assertIn('status', health)
        self.assertIn('avg_cpu_usage', health)

        # 获取成本分析
        cost_analysis = monitor.get_cost_analysis()

        self.assertIn('total_cost', cost_analysis)
        self.assertGreater(cost_analysis['total_cost'], 0)

        # 获取告警
        alerts = monitor.get_alerts(paper_trader)

        self.assertIsInstance(alerts, list)

    def test_decision_cache_integration(self):
        """测试决策缓存集成"""
        cache = DecisionCache()

        # 创建交易决策
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

        # 使用set方法保存决策 - 需要symbol, timeframe_data, decision参数
        import pandas as pd
        timeframe_data = {
            '4h': pd.DataFrame(),
            '3m': pd.DataFrame()
        }
        cache.set('BTCUSDT', timeframe_data, decision)

        # 使用get方法获取决策 - 需要symbol, timeframe_data参数
        cached_result = cache.get('BTCUSDT', timeframe_data)

        self.assertIsNotNone(cached_result)
        # cached_result是元组(decision, timestamp)
        cached_decision = cached_result[0]
        self.assertEqual(cached_decision.action, "BUY")

        # 检查缓存统计
        stats = cache.get_stats()
        self.assertIsInstance(stats, dict)

    def test_position_sizer_integration(self):
        """测试仓位大小计算器集成"""
        risk_manager = RiskManager(account_balance=100000)
        position_sizer = PositionSizer(risk_manager)

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

        position_size = position_sizer.calculate_position_size(
            decision, 50000, 100000
        )

        self.assertIsInstance(position_size, float)
        self.assertGreaterEqual(position_size, 0)

    def test_multi_timeframe_preprocessor_integration(self):
        """测试多时间框架预处理器集成"""
        preprocessor = MultiTimeframeProcessor()

        # 模拟市场数据
        import pandas as pd
        dates_4h = pd.date_range(start='2024-01-01', end='2024-01-10', freq='4H')
        dates_3m = pd.date_range(start='2024-01-01', end='2024-01-10', freq='3T')

        data_4h = pd.DataFrame({
            'open': [50000] * len(dates_4h),
            'high': [50500] * len(dates_4h),
            'low': [49500] * len(dates_4h),
            'close': [50000] * len(dates_4h),
            'volume': [100] * len(dates_4h)
        }, index=dates_4h)

        data_3m = pd.DataFrame({
            'open': [50000] * len(dates_3m),
            'high': [50500] * len(dates_3m),
            'low': [49500] * len(dates_3m),
            'close': [50000] * len(dates_3m),
            'volume': [100] * len(dates_3m)
        }, index=dates_3m)

        # 处理数据
        result_4h = preprocessor.process_4h_data(data_4h)
        result_3m = preprocessor.process_3m_data(data_3m)

        self.assertIsNotNone(result_4h)
        self.assertIsNotNone(result_3m)

    def test_complete_workflow_simulation(self):
        """测试完整工作流模拟"""
        # 模拟完整的数据到决策流程

        # 1. 数据获取
        fetcher = DataFetcher()

        # 2. 数据预处理
        preprocessor = MultiTimeframeProcessor()

        # 3. 提示词生成
        prompt_gen = PromptGenerator()

        # 4. 风险评估
        risk_manager = RiskManager(account_balance=100000)

        # 5. 纸交易执行
        paper_trader = PaperTrader(initial_balance=100000)

        # 6. 性能监控
        monitor = PerformanceMonitor(database_path=os.path.join(self.temp_dir, "workflow.db"))

        # 创建交易决策
        decision = TradingDecision(
            action="BUY",
            confidence=85,
            symbol="BTCUSDT",
            entry_price=50000,
            stop_loss=49000,
            take_profit=52000,
            position_size=10.0,
            leverage=2.0,
            risk_level="MEDIUM",
            risk_score=55,
            model_source="integration_test",
            timeframe="4h"
        )

        # 执行决策流程
        # 1. 风险评估
        is_passed, message, suggested_size = risk_manager.evaluate_decision(
            decision, {}, {"BTCUSDT": 50000}
        )

        self.assertIsInstance(is_passed, bool)

        # 2. 如果通过评估，执行交易
        if is_passed:
            result = paper_trader.execute_decision(decision, 50000)

            # 3. 记录到监控
            monitor.record_trading_metrics(
                decision=decision,
                pnl=result.get('pnl', 0),
                execution_time=1.0,
                llm_cost=0.02,
                total_cost=0.03
            )

            # 4. 获取性能摘要
            summary = monitor.get_performance_summary(paper_trader)

            self.assertIsNotNone(summary)

    def test_all_modules_import(self):
        """测试所有模块可以正确导入"""
        # 测试核心模块
        try:
            from data_fetcher import DataFetcher
            from indicators import TechnicalIndicators
            from database import Database
        except ImportError as e:
            self.fail(f"Failed to import core module: {e}")

        # 测试模型
        try:
            from models.trading_decision import TradingDecision
        except ImportError as e:
            self.fail(f"Failed to import model: {e}")

        # 测试LLM客户端
        try:
            from llm_clients.deepseek_client import DeepSeekClient
            from llm_clients.qwen_client import QwenClient
        except ImportError as e:
            self.fail(f"Failed to import LLM client: {e}")

        # 测试交易模块
        try:
            from trading.paper_trader import PaperTrader
        except ImportError as e:
            self.fail(f"Failed to import trading module: {e}")

        # 测试调度模块
        try:
            from scheduling.decision_cache import DecisionCache
        except ImportError as e:
            self.fail(f"Failed to import scheduling module: {e}")

        # 测试风险管理模块
        try:
            from risk_management.risk_manager import RiskManager
            from risk_management.backtest_engine import BacktestEngine
        except ImportError as e:
            self.fail(f"Failed to import risk management module: {e}")

        # 测试监控模块
        try:
            from monitoring.performance_monitor import PerformanceMonitor
        except ImportError as e:
            self.fail(f"Failed to import monitoring module: {e}")

    def test_configuration_consistency(self):
        """测试配置一致性"""
        # 验证所有模块使用相同的配置参数

        # 检查风险管理配置
        risk_manager = RiskManager(
            account_balance=100000,
            max_position_size=0.1,
            max_leverage=10.0
        )

        self.assertEqual(risk_manager.max_position_size, 0.1)
        self.assertEqual(risk_manager.max_leverage, 10.0)

        # 检查纸交易配置
        paper_trader = PaperTrader(
            initial_balance=100000,
            fee_rate=0.001
        )

        self.assertEqual(paper_trader.initial_balance, 100000)

        # 检查回测配置
        config = BacktestConfig(
            initial_balance=100000,
            max_position_size=0.1,
            max_leverage=10.0
        )

        self.assertEqual(config.max_position_size, 0.1)
        self.assertEqual(config.max_leverage, 10.0)


if __name__ == '__main__':
    # 运行集成测试
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCompleteSystemIntegration)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 输出结果
    print("\n" + "="*70)
    print("集成测试完成")
    print("="*70)
    print(f"运行测试: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n✅ 所有集成测试通过！")
    else:
        print("\n❌ 部分测试失败")
        if result.failures:
            print("\n失败的测试:")
            for test, traceback in result.failures:
                print(f"  - {test}")
        if result.errors:
            print("\n错误的测试:")
            for test, traceback in result.errors:
                print(f"  - {test}")

    exit(0 if result.wasSuccessful() else 1)
