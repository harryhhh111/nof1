"""
纸交易执行器测试

测试模拟交易功能
"""

import unittest
import tempfile
import os
import sys
from datetime import datetime
from unittest.mock import Mock

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trading.paper_trader import PaperTrader, Position, Trade
from models.trading_decision import TradingDecision


class TestPaperTrader(unittest.TestCase):
    """纸交易执行器测试"""

    def setUp(self):
        """测试前准备"""
        # 使用临时数据库
        self.temp_db = tempfile.mktemp(suffix='.db')
        self.trader = PaperTrader(
            initial_balance=100000,
            database_path=self.temp_db,
            fee_rate=0.001
        )

    def tearDown(self):
        """测试后清理"""
        self.trader.close()
        if os.path.exists(self.temp_db):
            os.remove(self.temp_db)

    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.trader.initial_balance, 100000)
        self.assertEqual(self.trader.balance, 100000)
        self.assertEqual(len(self.trader.positions), 0)
        self.assertEqual(len(self.trader.trades), 0)

    def test_buy_new_position(self):
        """测试新建多头仓位"""
        # 创建买入决策
        decision = TradingDecision(
            action="BUY",
            confidence=80,
            symbol="BTCUSDT",
            entry_price=50000,
            stop_loss=49000,
            take_profit=52000,
            position_size=50.0,  # 50%仓位
            risk_level="MEDIUM",
            risk_score=50,
            model_source="test",
            timeframe="4h"
        )

        result = self.trader.execute_decision(decision, 50000)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["action"], "buy")
        self.assertIn("BTCUSDT", self.trader.positions)

        # 计算期望余额：初始余额100000 - (50000 * 1 + 50 * 0.1%)
        # position_size=50% = 50000美元，买入数量=50000/50000=1 BTC
        # 手续费=50000 * 1 * 0.1% = 50美元
        # 总成本=50000 + 50 = 50050
        # 余额=100000 - 50050 = 49950
        expected_balance = 49950.0
        self.assertAlmostEqual(self.trader.balance, expected_balance, places=0)

    def test_sell_position(self):
        """测试平仓"""
        # 先买入
        buy_decision = TradingDecision(
            action="BUY",
            confidence=80,
            symbol="BTCUSDT",
            entry_price=50000,
            position_size=50.0,
            risk_level="MEDIUM",
            risk_score=50,
            model_source="test",
            timeframe="4h"
        )
        self.trader.execute_decision(buy_decision, 50000)

        # 卖出
        sell_decision = TradingDecision(
            action="SELL",
            confidence=80,
            symbol="BTCUSDT",
            entry_price=51000,
            position_size=100.0,
            risk_level="MEDIUM",
            risk_score=50,
            model_source="test",
            timeframe="4h"
        )

        result = self.trader.execute_decision(sell_decision, 51000)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["action"], "close")
        self.assertNotIn("BTCUSDT", self.trader.positions)
        self.assertGreater(self.trader.balance, 100000)  # 盈利

    def test_hold_decision(self):
        """测试HOLD决策"""
        decision = TradingDecision(
            action="HOLD",
            confidence=50,
            symbol="BTCUSDT",
            risk_level="MEDIUM",
            risk_score=50,
            model_source="test",
            timeframe="4h"
        )

        result = self.trader.execute_decision(decision, 50000)

        self.assertEqual(result["status"], "hold")
        self.assertEqual(self.trader.balance, 100000)  # 余额不变

    def test_update_prices(self):
        """测试更新价格"""
        # 建立仓位
        decision = TradingDecision(
            action="BUY",
            confidence=80,
            symbol="BTCUSDT",
            entry_price=50000,
            position_size=50.0,
            risk_level="MEDIUM",
            risk_score=50,
            model_source="test",
            timeframe="4h"
        )
        self.trader.execute_decision(decision, 50000)

        # 更新价格
        price_data = {"BTCUSDT": 52000}
        self.trader.update_prices(price_data)

        position = self.trader.positions["BTCUSDT"]
        self.assertEqual(position.current_price, 52000)
        self.assertAlmostEqual(position.unrealized_pnl, 2000, places=2)

    def test_stop_loss_trigger(self):
        """测试止损触发"""
        # 建立带止损的仓位
        decision = TradingDecision(
            action="BUY",
            confidence=80,
            symbol="BTCUSDT",
            entry_price=50000,
            stop_loss=49000,  # 止损
            take_profit=52000,
            position_size=50.0,
            risk_level="MEDIUM",
            risk_score=50,
            model_source="test",
            timeframe="4h"
        )
        self.trader.execute_decision(decision, 50000)

        # 触发止损
        price_data = {"BTCUSDT": 48500}
        self.trader.update_prices(price_data)

        # 应该已平仓
        self.assertNotIn("BTCUSDT", self.trader.positions)

    def test_take_profit_trigger(self):
        """测试止盈触发"""
        # 建立带止盈的仓位
        decision = TradingDecision(
            action="BUY",
            confidence=80,
            symbol="BTCUSDT",
            entry_price=50000,
            stop_loss=49000,
            take_profit=52000,  # 止盈
            position_size=50.0,
            risk_level="MEDIUM",
            risk_score=50,
            model_source="test",
            timeframe="4h"
        )
        self.trader.execute_decision(decision, 50000)

        # 触发止盈
        price_data = {"BTCUSDT": 52500}
        self.trader.update_prices(price_data)

        # 应该已平仓
        self.assertNotIn("BTCUSDT", self.trader.positions)

    def test_get_portfolio_value(self):
        """测试投资组合价值计算"""
        # 建立仓位
        decision = TradingDecision(
            action="BUY",
            confidence=80,
            symbol="BTCUSDT",
            entry_price=50000,
            position_size=50.0,
            risk_level="MEDIUM",
            risk_score=50,
            model_source="test",
            timeframe="4h"
        )
        self.trader.execute_decision(decision, 50000)

        # 计算投资组合价值
        price_data = {"BTCUSDT": 51000}
        value = self.trader.get_portfolio_value(price_data)

        # 价值 = 现金余额 + 持仓价值
        # 持仓价值 = 1 * 51000 = 51000
        # 现金余额 = 100000 - (50000 + 50) = 49950
        # 总价值 ≈ 100950
        self.assertGreater(value, 100000)

    def test_get_pnl(self):
        """测试PnL计算"""
        # 建立仓位
        decision = TradingDecision(
            action="BUY",
            confidence=80,
            symbol="BTCUSDT",
            entry_price=50000,
            position_size=50.0,
            risk_level="MEDIUM",
            risk_score=50,
            model_source="test",
            timeframe="4h"
        )
        self.trader.execute_decision(decision, 50000)

        # 计算PnL
        price_data = {"BTCUSDT": 52000}
        pnl = self.trader.get_pnl(price_data)

        self.assertIn("unrealized_pnl", pnl)
        self.assertIn("realized_pnl", pnl)
        self.assertIn("total_pnl", pnl)
        self.assertGreater(pnl["unrealized_pnl"], 0)

    def test_get_performance_metrics(self):
        """测试性能指标计算"""
        metrics = self.trader.get_performance_metrics()

        self.assertIn("total_trades", metrics)
        self.assertIn("win_rate", metrics)
        self.assertIn("total_return", metrics)
        self.assertEqual(metrics["total_trades"], 0)
        self.assertEqual(metrics["win_rate"], 0)

    def test_get_positions(self):
        """测试获取持仓"""
        positions = self.trader.get_positions()
        self.assertEqual(positions, [])

        # 建立仓位
        decision = TradingDecision(
            action="BUY",
            confidence=80,
            symbol="BTCUSDT",
            entry_price=50000,
            position_size=50.0,
            risk_level="MEDIUM",
            risk_score=50,
            model_source="test",
            timeframe="4h"
        )
        self.trader.execute_decision(decision, 50000)

        positions = self.trader.get_positions()
        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0]["symbol"], "BTCUSDT")

    def test_get_trades(self):
        """测试获取交易记录"""
        trades = self.trader.get_trades()
        self.assertEqual(len(trades), 0)

        # 买入
        decision = TradingDecision(
            action="BUY",
            confidence=80,
            symbol="BTCUSDT",
            entry_price=50000,
            position_size=50.0,
            risk_level="MEDIUM",
            risk_score=50,
            model_source="test",
            timeframe="4h"
        )
        self.trader.execute_decision(decision, 50000)

        trades = self.trader.get_trades()
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0]["side"], "buy")

    def test_export_trades(self):
        """测试导出交易记录"""
        # 创建临时文件
        temp_file = tempfile.mktemp(suffix='.json')

        try:
            # 买入
            decision = TradingDecision(
                action="BUY",
                confidence=80,
                symbol="BTCUSDT",
                entry_price=50000,
                position_size=50.0,
                risk_level="MEDIUM",
                risk_score=50,
                model_source="test",
                timeframe="4h"
            )
            self.trader.execute_decision(decision, 50000)

            # 导出
            self.trader.export_trades(temp_file)

            # 验证文件存在
            self.assertTrue(os.path.exists(temp_file))

            # 读取并验证
            import json
            with open(temp_file, 'r') as f:
                data = json.load(f)
            self.assertEqual(len(data), 1)

        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_reset(self):
        """测试重置账户"""
        # 买入
        decision = TradingDecision(
            action="BUY",
            confidence=80,
            symbol="BTCUSDT",
            entry_price=50000,
            position_size=50.0,
            risk_level="MEDIUM",
            risk_score=50,
            model_source="test",
            timeframe="4h"
        )
        self.trader.execute_decision(decision, 50000)

        # 重置
        self.trader.reset()

        # 验证
        self.assertEqual(self.trader.balance, 100000)
        self.assertEqual(len(self.trader.positions), 0)
        self.assertEqual(len(self.trader.trades), 0)

    def test_insufficient_balance(self):
        """测试余额不足"""
        decision = TradingDecision(
            action="BUY",
            confidence=80,
            symbol="BTCUSDT",
            entry_price=200000,  # 高价格
            position_size=100.0,  # 100%仓位
            risk_level="MEDIUM",
            risk_score=50,
            model_source="test",
            timeframe="4h"
        )

        result = self.trader.execute_decision(decision, 200000)

        self.assertEqual(result["status"], "error")
        self.assertIn("余额不足", result["message"])

    def test_invalid_decision(self):
        """测试无效决策"""
        decision = TradingDecision(
            action="BUY",
            confidence=150,  # 无效置信度
            symbol="BTCUSDT",
            entry_price=50000,
            position_size=50.0,
            risk_level="MEDIUM",
            risk_score=50,
            model_source="test",
            timeframe="4h"
        )

        result = self.trader.execute_decision(decision, 50000)

        self.assertEqual(result["status"], "error")
        self.assertIn("决策无效", result["message"])


class TestPosition(unittest.TestCase):
    """持仓测试"""

    def test_position_creation(self):
        """测试持仓创建"""
        position = Position(
            symbol="BTCUSDT",
            side="long",
            size=1.0,
            entry_price=50000,
            entry_time=datetime.now(),
            current_price=50000
        )

        self.assertEqual(position.symbol, "BTCUSDT")
        self.assertEqual(position.side, "long")
        self.assertEqual(position.size, 1.0)
        self.assertEqual(position.entry_price, 50000)
        self.assertEqual(position.unrealized_pnl, 0)

    def test_update_price_long(self):
        """测试更新价格-多头"""
        position = Position(
            symbol="BTCUSDT",
            side="long",
            size=1.0,
            entry_price=50000,
            entry_time=datetime.now(),
            current_price=50000
        )

        position.update_price(52000)

        self.assertEqual(position.current_price, 52000)
        self.assertEqual(position.unrealized_pnl, 2000)

    def test_update_price_short(self):
        """测试更新价格-空头"""
        position = Position(
            symbol="BTCUSDT",
            side="short",
            size=1.0,
            entry_price=50000,
            entry_time=datetime.now(),
            current_price=50000
        )

        position.update_price(48000)

        self.assertEqual(position.current_price, 48000)
        self.assertEqual(position.unrealized_pnl, 2000)

    def test_to_dict(self):
        """测试转换为字典"""
        entry_time = datetime.now()
        position = Position(
            symbol="BTCUSDT",
            side="long",
            size=1.0,
            entry_price=50000,
            entry_time=entry_time,
            current_price=50000
        )

        data = position.to_dict()

        self.assertEqual(data["symbol"], "BTCUSDT")
        self.assertEqual(data["side"], "long")
        self.assertEqual(data["size"], 1.0)
        self.assertEqual(data["entry_price"], 50000)
        self.assertIsInstance(data["entry_time"], str)


class TestTrade(unittest.TestCase):
    """交易测试"""

    def test_trade_creation(self):
        """测试交易创建"""
        trade = Trade(
            trade_id="test_001",
            symbol="BTCUSDT",
            side="buy",
            size=1.0,
            price=50000,
            timestamp=datetime.now()
        )

        self.assertEqual(trade.trade_id, "test_001")
        self.assertEqual(trade.symbol, "BTCUSDT")
        self.assertEqual(trade.side, "buy")
        self.assertEqual(trade.size, 1.0)
        self.assertEqual(trade.price, 50000)

    def test_to_dict(self):
        """测试转换为字典"""
        timestamp = datetime.now()
        trade = Trade(
            trade_id="test_001",
            symbol="BTCUSDT",
            side="buy",
            size=1.0,
            price=50000,
            timestamp=timestamp
        )

        data = trade.to_dict()

        self.assertEqual(data["trade_id"], "test_001")
        self.assertEqual(data["symbol"], "BTCUSDT")
        self.assertEqual(data["side"], "buy")
        self.assertEqual(data["size"], 1.0)
        self.assertEqual(data["price"], 50000)
        self.assertIsInstance(data["timestamp"], str)


if __name__ == '__main__':
    unittest.main()
