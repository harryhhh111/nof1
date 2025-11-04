"""
风险管理器测试

测试风险管理功能
"""

import unittest
import numpy as np
from datetime import datetime
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from risk_management.risk_manager import RiskManager, RiskMetrics, PositionSizer
from models.trading_decision import TradingDecision


class TestRiskManager(unittest.TestCase):
    """风险管理器测试"""

    def setUp(self):
        """测试前准备"""
        self.risk_manager = RiskManager(
            account_balance=100000,
            max_position_size=0.1,
            max_leverage=10.0,
            max_portfolio_risk=0.02
        )

    def test_evaluate_valid_decision(self):
        """测试评估有效决策"""
        decision = TradingDecision(
            action="BUY",
            confidence=80,
            symbol="BTCUSDT",
            entry_price=50000,
            stop_loss=49000,
            take_profit=52000,
            position_size=5.0,  # 5%
            risk_level="MEDIUM",
            risk_score=50,
            model_source="test",
            timeframe="4h"
        )

        current_positions = {}
        price_data = {"BTCUSDT": 50000}

        is_passed, message, suggested_size = self.risk_manager.evaluate_decision(
            decision, current_positions, price_data
        )

        self.assertTrue(is_passed)
        self.assertIn("通过风险评估", message)
        self.assertIsNotNone(suggested_size)
        self.assertGreater(suggested_size, 0)

    def test_evaluate_invalid_decision(self):
        """测试评估无效决策"""
        decision = TradingDecision(
            action="BUY",
            confidence=150,  # 无效置信度
            symbol="BTCUSDT",
            entry_price=50000,
            position_size=5.0,
            risk_level="MEDIUM",
            risk_score=50,
            model_source="test",
            timeframe="4h"
        )

        current_positions = {}
        price_data = {"BTCUSDT": 50000}

        is_passed, message, suggested_size = self.risk_manager.evaluate_decision(
            decision, current_positions, price_data
        )

        self.assertFalse(is_passed)
        self.assertIn("置信度无效", message)

    def test_evaluate_excessive_position(self):
        """测试评估超大仓位"""
        decision = TradingDecision(
            action="BUY",
            confidence=80,
            symbol="BTCUSDT",
            entry_price=50000,
            position_size=50.0,  # 50%，超出10%限制
            risk_level="LOW",
            risk_score=30,
            model_source="test",
            timeframe="4h"
        )

        current_positions = {}
        price_data = {"BTCUSDT": 50000}

        is_passed, message, suggested_size = self.risk_manager.evaluate_decision(
            decision, current_positions, price_data
        )

        self.assertFalse(is_passed)
        self.assertIn("仓位过大", message)

    def test_evaluate_excessive_leverage(self):
        """测试评估过高杠杆"""
        decision = TradingDecision(
            action="BUY",
            confidence=80,
            symbol="BTCUSDT",
            entry_price=50000,
            position_size=5.0,
            leverage=20.0,  # 超出10x限制
            risk_level="MEDIUM",
            risk_score=50,
            model_source="test",
            timeframe="4h"
        )

        current_positions = {}
        price_data = {"BTCUSDT": 50000}

        is_passed, message, suggested_size = self.risk_manager.evaluate_decision(
            decision, current_positions, price_data
        )

        self.assertFalse(is_passed)
        self.assertIn("杠杆过高", message)

    def test_calculate_risk_metrics_sufficient_data(self):
        """测试计算风险指标-数据充足"""
        # 生成模拟价格历史
        np.random.seed(42)
        price_history = [50000 + np.random.normal(0, 1000) for _ in range(100)]

        metrics = self.risk_manager.calculate_risk_metrics(
            symbol="BTCUSDT",
            position_size_pct=5.0,
            leverage=1.0,
            price_history=price_history
        )

        self.assertEqual(metrics.symbol, "BTCUSDT")
        self.assertIsInstance(metrics.risk_score, int)
        self.assertGreaterEqual(metrics.risk_score, 0)
        self.assertLessEqual(metrics.risk_score, 100)
        self.assertIn(metrics.risk_level, ["LOW", "MEDIUM", "HIGH"])

    def test_calculate_risk_metrics_insufficient_data(self):
        """测试计算风险指标-数据不足"""
        price_history = [50000, 50100]  # 数据不足

        metrics = self.risk_manager.calculate_risk_metrics(
            symbol="BTCUSDT",
            position_size_pct=5.0,
            leverage=1.0,
            price_history=price_history
        )

        # 数据不足时应返回默认值
        self.assertEqual(metrics.var_1d, 0.0)
        self.assertEqual(metrics.sharpe_ratio, 0.0)
        self.assertEqual(metrics.max_drawdown, 0.0)

    def test_calculate_var(self):
        """测试VaR计算"""
        returns = np.array([0.01, -0.02, 0.015, -0.01, 0.005])

        var = self.risk_manager._calculate_var(returns, 0.05)

        # VaR应为负值（损失）
        self.assertLess(var, 0)

    def test_calculate_sharpe_ratio(self):
        """测试夏普比率计算"""
        returns = np.array([0.01, 0.015, 0.02, 0.005, 0.01])

        sharpe = self.risk_manager._calculate_sharpe(returns)

        # 夏普比率可以为正或负
        self.assertIsInstance(sharpe, float)

    def test_calculate_max_drawdown(self):
        """测试最大回撤计算"""
        prices = [100, 105, 102, 108, 103, 110, 107]

        max_dd = self.risk_manager._calculate_max_drawdown(prices)

        self.assertGreaterEqual(max_dd, 0)
        self.assertLessEqual(max_dd, 1)
        self.assertAlmostEqual(max_dd, (108 - 103) / 108, places=2)

    def test_calculate_risk_score(self):
        """测试风险评分计算"""
        score = self.risk_manager._calculate_risk_score(
            var_1d=0.02,
            volatility=30.0,
            max_drawdown=0.1,
            position_size_pct=5.0,
            leverage=1.0
        )

        self.assertIsInstance(score, int)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_get_risk_summary(self):
        """测试获取风险摘要"""
        positions = {
            "BTCUSDT": {"size": 1.0, "side": "long"}
        }
        price_data = {"BTCUSDT": 50000}

        summary = self.risk_manager.get_risk_summary(positions, price_data)

        self.assertIn('portfolio_risk', summary)
        self.assertIn('total_value', summary)
        self.assertIn('utilization', summary)
        self.assertGreaterEqual(summary['utilization'], 0)

    def test_calculate_position_size(self):
        """测试计算仓位大小"""
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

        position_size = self.risk_manager._calculate_position_size(decision, 50000)

        self.assertIsNotNone(position_size)
        self.assertGreaterEqual(position_size, 0)

    def test_calculate_position_size_hold(self):
        """测试HOLD决策的仓位大小"""
        decision = TradingDecision(
            action="HOLD",
            confidence=50,
            symbol="BTCUSDT",
            position_size=0,
            risk_level="MEDIUM",
            risk_score=50,
            model_source="test",
            timeframe="4h"
        )

        position_size = self.risk_manager._calculate_position_size(decision, 50000)

        self.assertEqual(position_size, 0.0)


class TestPositionSizer(unittest.TestCase):
    """仓位大小计算器测试"""

    def setUp(self):
        """测试前准备"""
        self.risk_manager = RiskManager(account_balance=100000)
        self.position_sizer = PositionSizer(self.risk_manager)

    def test_calculate_position_size_with_history(self):
        """测试带历史数据的仓位计算"""
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

        price_history = [50000 + np.random.normal(0, 1000) for _ in range(100)]

        position_size = self.position_sizer.calculate_position_size(
            decision, 50000, 100000, price_history
        )

        self.assertGreaterEqual(position_size, 0)

    def test_calculate_position_size_without_history(self):
        """测试不带历史数据的仓位计算"""
        decision = TradingDecision(
            action="BUY",
            confidence=80,
            symbol="BTCUSDT",
            entry_price=50000,
            position_size=10.0,
            risk_level="LOW",
            risk_score=30,
            model_source="test",
            timeframe="4h"
        )

        position_size = self.position_sizer.calculate_position_size(
            decision, 50000, 100000
        )

        self.assertGreaterEqual(position_size, 0)
        # LOW风险应该得到更大仓位
        self.assertGreater(position_size, 0)


class TestRiskMetrics(unittest.TestCase):
    """风险指标测试"""

    def test_risk_metrics_creation(self):
        """测试创建风险指标"""
        metrics = RiskMetrics(
            symbol="BTCUSDT",
            position_size_pct=5.0,
            leverage=1.0,
            var_1d=0.02,
            var_5d=0.05,
            sharpe_ratio=1.5,
            max_drawdown=0.1,
            volatility=30.0,
            correlation_risk=0.5,
            liquidity_risk=0.1,
            risk_score=60,
            risk_level="MEDIUM"
        )

        self.assertEqual(metrics.symbol, "BTCUSDT")
        self.assertEqual(metrics.risk_level, "MEDIUM")

    def test_risk_metrics_to_dict(self):
        """测试转换为字典"""
        metrics = RiskMetrics(
            symbol="BTCUSDT",
            position_size_pct=5.0,
            leverage=1.0,
            var_1d=0.02,
            var_5d=0.05,
            sharpe_ratio=1.5,
            max_drawdown=0.1,
            volatility=30.0,
            correlation_risk=0.5,
            liquidity_risk=0.1,
            risk_score=60,
            risk_level="MEDIUM"
        )

        data = metrics.to_dict()

        self.assertIsInstance(data, dict)
        self.assertEqual(data['symbol'], "BTCUSDT")
        self.assertEqual(data['risk_level'], "MEDIUM")


if __name__ == '__main__':
    unittest.main()
