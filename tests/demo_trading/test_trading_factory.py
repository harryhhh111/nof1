"""
交易工厂模式演示

测试不同交易模式之间的切换
"""

import sys
sys.path.append('/home/claude_user/nof1')

from trading.trading_factory import TradingFactory
from models.trading_decision import TradingDecision

def test_trading_modes():
    """测试不同交易模式"""

    print("=" * 60)
    print("🔧 交易工厂模式演示")
    print("=" * 60)

    # 测试可用模式
    print("\n📋 可用交易模式:")
    for mode in TradingFactory.get_available_modes():
        is_test = TradingFactory.is_test_mode(mode)
        risk_level = "🟢 无风险" if is_test else "🔴 高风险"
        print(f"  - {mode.upper():10s} {risk_level}")

    # 测试 Paper Trading
    print("\n" + "=" * 60)
    print("🧪 测试 Paper Trading (纸交易)")
    print("=" * 60)

    try:
        paper_trader = TradingFactory.create_trader('paper')
        print(f"✅ 创建成功 - 模式: {paper_trader.mode_name}")

        # 测试获取余额
        balance = paper_trader.get_account_balance()
        print(f"💰 初始余额: {balance}")

        # 测试获取价格
        price = paper_trader.get_symbol_price('BTCUSDT')
        print(f"📊 BTCUSDT 当前价格: ${price:,.2f}")

        # 测试下订单
        print("\n📝 测试下买单...")
        result = paper_trader.place_market_order('BTCUSDT', 'buy', 0.001, "纸交易测试")
        print(f"结果: {result}")

        # 测试余额变化
        balance = paper_trader.get_account_balance()
        print(f"💰 下单后余额: {balance}")

        # 测试决策执行
        print("\n🤖 测试交易决策执行...")
        decision = TradingDecision(
            action="BUY",
            confidence=75.0,
            entry_price=price,
            stop_loss=price * 0.95,
            take_profit=price * 1.10,
            position_size=5.0,
            risk_level="MEDIUM",
            reasoning="纸交易决策测试",
            timeframe="4h",
            symbol="ETHUSDT"
        )

        result = paper_trader.execute_decision(decision)
        print(f"决策执行结果: {result}")

        # 测试持仓
        positions = paper_trader.get_open_positions()
        print(f"📦 当前持仓: {positions}")

        # 测试性能摘要
        perf = paper_trader.get_performance_summary()
        print(f"\n📈 性能摘要:")
        print(f"  总价值: ${perf['total_value']:,.2f}")
        print(f"  总盈亏: ${perf['total_pnl']:,.2f}")
        print(f"  盈亏比例: {perf['pnl_percentage']:.2f}%")
        print(f"  交易次数: {perf['total_trades']}")

        paper_trader.close()

    except Exception as e:
        print(f"❌ Paper Trading 测试失败: {e}")

    # 测试 Testnet Trading
    print("\n" + "=" * 60)
    print("🧪 测试 Testnet Trading")
    print("=" * 60)

    try:
        testnet_trader = TradingFactory.create_trader('testnet')
        print(f"✅ 创建成功 - 模式: {testnet_trader.mode_name}")

        # 测试获取余额
        balance = testnet_trader.get_account_balance()
        print(f"💰 Testnet 余额: {balance}")

        # 测试获取价格
        price = testnet_trader.get_symbol_price('BTCUSDT')
        print(f"📊 BTCUSDT 当前价格: ${price:,.2f}")

        testnet_trader.close()
        print("✅ Testnet Trading 测试完成")

    except Exception as e:
        print(f"⚠️  Testnet Trading 测试失败: {e}")
        print("  原因: 可能未配置 Testnet API Key 或网络问题")

    print("\n" + "=" * 60)
    print("✅ 交易工厂模式测试完成")
    print("=" * 60)


if __name__ == "__main__":
    test_trading_modes()
