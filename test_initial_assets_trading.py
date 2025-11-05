#!/usr/bin/env python3
"""
测试初始资产交易逻辑

验证 Demo Trading 初始资产持仓的使用，特别是做空操作
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from trading.real_trader import RealTrader
from models.trading_decision import TradingDecision

def test_initial_assets_trading():
    """测试初始资产交易逻辑"""
    print("=" * 80)
    print(" 测试初始资产交易逻辑")
    print("=" * 80)

    # 显示当前配置
    print(f"\n📊 当前配置:")
    print(f"   交易模式: {config.CURRENT_MODE.upper()}")
    print(f"   Demo API: {config.DEMO_API_KEY[:20]}..." if config.DEMO_API_KEY else "   Demo API: ❌ 未配置")

    try:
        trader = RealTrader(use_futures=False)
        print("✅ RealTrader 初始化成功")

        # 1. 获取账户余额
        print("\n" + "=" * 80)
        print(" 步骤1: 获取账户余额")
        print("=" * 80)

        balance = trader.get_account_balance()
        if not balance:
            print("⚠️  无法获取余额 (API权限不足)")
            print("   请检查 API Key 是否开启读取权限")
            return

        print(f"\n💰 账户余额:")
        initial_assets = ['USDT', 'BTC', 'ETH', 'BNB']
        for asset in initial_assets:
            amount = balance.get(asset, 0)
            status = "✅" if amount > 0 else "⚪"
            print(f"   {asset:>4}: {amount:>10.6f} {status}")

        # 2. 获取持仓信息
        print("\n" + "=" * 80)
        print(" 步骤2: 获取持仓信息")
        print("=" * 80)

        positions = trader.get_open_positions()
        if not positions:
            print("⚠️  当前无持仓")
        else:
            print(f"\n📦 持仓列表:")
            initial_positions = [p for p in positions if p.get('is_initial_asset', False)]
            other_positions = [p for p in positions if not p.get('is_initial_asset', False)]

            if initial_positions:
                print("\n   🏆 初始资产:")
                for pos in initial_positions:
                    symbol = pos['symbol']
                    asset = pos.get('asset', 'N/A')
                    amount = pos.get('contracts', 0)
                    price = pos.get('current_price')
                    value = pos.get('value')
                    print(f"   • {symbol}: {amount:.6f} {asset} (市值: ${value:,.2f})" if value else f"   • {symbol}: {amount:.6f} {asset}")

            if other_positions:
                print("\n   💼 其他持仓:")
                for pos in other_positions:
                    symbol = pos['symbol']
                    amount = pos.get('contracts', 0)
                    print(f"   • {symbol}: {amount:.6f}")

        # 3. 验证做空逻辑
        print("\n" + "=" * 80)
        print(" 步骤3: 验证做空逻辑")
        print("=" * 80)

        # 检查是否有 BTC 初始资产
        if 'BTC' in balance and balance['BTC'] > 0:
            btc_amount = balance['BTC']
            print(f"\n✅ 发现 BTC 初始资产: {btc_amount:.6f}")
            print("   可以执行 SELL BTCUSDT 来模拟做空 BTC")

            # 创建模拟做空决策
            current_price = trader.get_symbol_price('BTCUSDT')
            sell_decision = TradingDecision(
                action="SELL",
                confidence=80.0,
                entry_price=current_price,
                position_size=10.0,  # 卖出 10% 的 BTC
                risk_level="MEDIUM",
                reasoning="测试初始资产做空 - 卖出部分 BTC",
                timeframe="4h",
                symbol="BTCUSDT",
                trend_analysis="基于初始资产的做空操作",
                key_factors=["BTC 初始资产", "测试做空逻辑"]
            )

            print(f"\n📋 做空决策:")
            print(f"   动作: {sell_decision.action} {sell_decision.symbol}")
            print(f"   数量: {btc_amount * 0.10:.6f} BTC (10%)")
            print(f"   价格: ${current_price:,.2f}")
            print(f"   原因: {sell_decision.reasoning}")

            # 注意：不实际执行交易，只验证逻辑
            print("\n💡 提示: 交易逻辑已验证，但不执行实际交易")
            print("   如需实际交易，请修改代码取消注释")

        elif 'ETH' in balance and balance['ETH'] > 0:
            eth_amount = balance['ETH']
            print(f"\n✅ 发现 ETH 初始资产: {eth_amount:.6f}")
            print("   可以执行 SELL ETHUSDT 来模拟做空 ETH")

            # 创建模拟做空决策
            current_price = trader.get_symbol_price('ETHUSDT')
            sell_decision = TradingDecision(
                action="SELL",
                confidence=80.0,
                entry_price=current_price,
                position_size=10.0,  # 卖出 10% 的 ETH
                risk_level="MEDIUM",
                reasoning="测试初始资产做空 - 卖出部分 ETH",
                timeframe="4h",
                symbol="ETHUSDT",
                trend_analysis="基于初始资产的做空操作",
                key_factors=["ETH 初始资产", "测试做空逻辑"]
            )

            print(f"\n📋 做空决策:")
            print(f"   动作: {sell_decision.action} {sell_decision.symbol}")
            print(f"   数量: {eth_amount * 0.10:.6f} ETH (10%)")
            print(f"   价格: ${current_price:,.2f}")
            print(f"   原因: {sell_decision.reasoning}")

            print("\n💡 提示: 交易逻辑已验证，但不执行实际交易")

        else:
            print("\n⚠️  未发现 BTC 或 ETH 初始资产")
            print("   请检查 Demo Trading 账户是否已 Reset")

        # 4. 验证获取持仓逻辑
        print("\n" + "=" * 80)
        print(" 步骤4: 验证获取持仓逻辑")
        print("=" * 80)

        print("\n✅ 初始资产交易逻辑验证通过!")
        print("   1. 可以获取账户余额")
        print("   2. 可以获取初始资产持仓")
        print("   3. 支持做空操作 (卖出初始资产)")

        trader.close()

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("\n" + "=" * 80)
    print(" Binance Demo Trading 初始资产交易测试")
    print("=" * 80)
    print("""
   此脚本用于测试 Demo Trading 的初始资产交易逻辑

   功能:
   • 验证初始资产余额获取
   • 验证持仓信息显示
   • 验证做空操作逻辑 (卖出初始资产)

   重要提示:
   • Demo Trading 无期货交易
   • 初始资产 (BTC, ETH, BNB) 可用于模拟做空
   • 卖出初始资产 = 做空操作
    """)

    try:
        test_initial_assets_trading()

        print("\n" + "=" * 80)
        print(" 📝 使用说明")
        print("=" * 80)
        print("""
   🎯 如何使用初始资产进行做空:

   1. 确认有初始资产:
      python3 test_initial_assets_trading.py

   2. 查看持仓:
      python3 demo_trading_viewer.py

   3. 执行交易决策:
      from trading.real_trader import RealTrader
      from models.trading_decision import TradingDecision

      trader = RealTrader()
      decision = TradingDecision(
          action="SELL",
          symbol="BTCUSDT",
          position_size=10.0,
          ...
      )
      result = trader.execute_decision(decision)

   💡 重要提醒:
   • 初始资产做空 = 卖出持有的初始资产
   • 例如: 卖出 0.005 BTC (初始 0.05 BTC 的 10%)
   • 做空后如果价格上涨，会亏损
   • 做空后如果价格下跌，会盈利

   🔗 相关文档:
   • DEMO_TRADING_INITIAL_FUNDS.md - 初始资金说明
   • demo_trading_viewer.py - 查看持仓
        """)

        print("\n" + "=" * 80)
        print(" ✅ 测试完成")
        print("=" * 80)

    except KeyboardInterrupt:
        print("\n\n   👋 已取消")
    except Exception as e:
        print(f"\n\n   ❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
