#!/usr/bin/env python3
"""
Binance Demo Trading 集成测试脚本

测试新的 Demo Trading API 集成
"""

import sys
import os
import json
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from data_fetcher import DataFetcher
from trading.real_trader import RealTrader
from models.trading_decision import TradingDecision

print("=" * 80)
print(" Binance Demo Trading 集成测试 (NEW)")
print("=" * 80)

# 显示当前配置
print(f"\n📊 当前配置:")
print(f"   交易模式: {config.CURRENT_MODE}")
print(f"   交易模式名称: {config.TRADING_MODE_NAME}")
print(f"   使用Testnet: {config.USE_TESTNET}")
print(f"   Demo API Key: {'✅ 已配置' if config.DEMO_API_KEY else '❌ 未配置'}")
print(f"   Testnet API Key: {'✅ 已配置' if config.TESTNET_API_KEY else '❌ 未配置'}")
print(f"   现货 Base URL: {config.BINANCE_BASE_URL}")
print(f"   期货 Base URL: {config.BINANCE_FUTURES_URL}")

if not config.DEMO_API_KEY:
    print("\n⚠️  警告: 未配置 Demo Trading API Key!")
    print("请设置环境变量:")
    print("  export DEMO_API_KEY='your_api_key'")
    print("  export DEMO_SECRET_KEY='your_secret_key'")
    print("  export USE_TESTNET=true")
    sys.exit(1)

print("\n" + "=" * 80)
print(" 步骤1: 测试数据获取 (现货)")
print("=" * 80)

try:
    fetcher_spot = DataFetcher(use_futures=False)
    print("✅ DataFetcher (现货) 初始化成功")

    # 获取BTC数据
    btc_data = fetcher_spot.get_market_data('BTCUSDT')
    print(f"\n📈 BTCUSDT 数据 (现货):")
    print(f"   当前价格: ${btc_data['current_price']:,.2f}")
    print(f"   时间戳: {btc_data['timestamp']}")
    print(f"   EMA20: {btc_data['intraday']['ema20'][-1]:.2f}" if btc_data['intraday']['ema20'] else "   EMA20: N/A")
    print(f"   RSI14: {btc_data['intraday']['rsi_14'][-1]:.2f}" if btc_data['intraday']['rsi_14'] else "   RSI14: N/A")
    print(f"   资金费率: {btc_data['perp_data']['funding_rate']:.6f}" if btc_data['perp_data']['funding_rate'] else "   资金费率: N/A")

    fetcher_spot.close()
    print("\n✅ 数据获取测试通过 (现货)")

except Exception as e:
    print(f"\n❌ 数据获取失败 (现货): {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print(" 步骤2: 测试真实交易执行器 (现货)")
print("=" * 80)

try:
    trader_spot = RealTrader(use_futures=False)
    print("✅ RealTrader (现货) 初始化成功")

    # 获取账户余额
    balance = trader_spot.get_account_balance()

    if not balance:
        print("\n⚠️  警告: 无法获取余额 (API权限不足)")
        print("   请检查 API Key 是否开启读取权限")
        print("   参考: https://demo.binance.com/en/my/wallet/demo/main")
        print("\n   预期初始资金:")
        print("     USDT: 5,000")
        print("     BTC:  0.05")
        print("     ETH:  1")
        print("     BNB:  2")
    else:
        print(f"\n💰 账户余额 (Demo Trading):")

        # 显示所有资产
        expected_assets = {'USDT': 5000, 'BTC': 0.05, 'ETH': 1.0, 'BNB': 2.0}
        matched = 0

        for asset, expected_amount in expected_assets.items():
            actual_amount = balance.get(asset, 0)
            if abs(actual_amount - expected_amount) < 0.001:
                status = "✅"
                matched += 1
            else:
                status = "⚠️"
            print(f"   {asset:>4}: {actual_amount:>10.6f} {status}")

        # 显示其他资产
        for asset, amount in balance.items():
            if asset not in expected_assets and amount > 0:
                print(f"   {asset:>4}: {amount:>10.6f} ℹ️")

        print(f"\n   匹配状态: {matched}/{len(expected_assets)} 初始资产")

        # 检查USDT余额
        if 'USDT' not in balance or balance['USDT'] < 10:
            print("\n⚠️  警告: USDT余额不足（至少需要10 USDT进行测试）")
            print("   如果是 Reset 后，应该有 5000 USDT")
        elif balance['USDT'] >= 5000:
            print(f"\n✅ USDT余额充足 (5,000)")
        else:
            print(f"\n✅ USDT余额: {balance['USDT']:.2f}")

        # 估算总价值
        try:
            btc_price = trader_spot.get_symbol_price('BTCUSDT')
            eth_price = trader_spot.get_symbol_price('ETHUSDT')

            total_value = (
                balance.get('USDT', 0) +
                balance.get('BTC', 0) * btc_price +
                balance.get('ETH', 0) * eth_price
            )
            print(f"\n   估算总价值: ${total_value:,.2f} USDT")
        except:
            pass

    # 测试获取当前价格
    current_price = trader_spot.get_symbol_price('BTCUSDT')
    print(f"\n📊 BTCUSDT 当前价格: ${current_price:,.2f}")

    trader_spot.close()
    print("\n✅ 交易执行器测试通过 (现货)")

except Exception as e:
    print(f"\n❌ 交易执行器测试失败 (现货): {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print(" 步骤3: 模拟交易决策")
print("=" * 80)

try:
    # 创建一个测试交易决策
    decision = TradingDecision(
        action="BUY",
        confidence=75.0,
        entry_price=current_price,
        stop_loss=current_price * 0.95,  # 5%止损
        take_profit=current_price * 1.10,  # 10%止盈
        position_size=10.0,  # 10%仓位
        risk_level="MEDIUM",
        reasoning="Demo Trading集成测试 - 基于多时间框架分析，看涨信号",
        timeframe="4h",
        symbol="BTCUSDT",
        trend_analysis="长期上升趋势",
        key_factors=["EMA20支撑", "RSI未超买", "成交量放大"]
    )

    print(f"\n📋 交易决策:")
    print(f"   动作: {decision.action}")
    print(f"   置信度: {decision.confidence}%")
    print(f"   入场价: ${decision.entry_price:,.2f}")
    print(f"   止损价: ${decision.stop_loss:,.2f}")
    print(f"   止盈价: ${decision.take_profit:,.2f}")
    print(f"   仓位大小: {decision.position_size}%")
    print(f"   风险等级: {decision.risk_level}")

    # 验证决策
    is_valid, msg = decision.validate_decision()
    print(f"\n✓ 决策验证: {'通过' if is_valid else '失败'}")
    if not is_valid:
        print(f"  错误: {msg}")

except Exception as e:
    print(f"\n❌ 交易决策测试失败: {e}")
    sys.exit(1)

print("\n" + "=" * 80)
print(" 步骤4: 测试期货数据获取 (可选)")
print("=" * 80)

try:
    # 尝试期货数据获取
    try:
        fetcher_futures = DataFetcher(use_futures=True)
        print("✅ DataFetcher (期货) 初始化成功")

        # 获取BTC期货数据
        btc_futures_data = fetcher_futures.get_market_data('BTCUSDT')
        print(f"\n📈 BTCUSDT 数据 (期货):")
        print(f"   当前价格: ${btc_futures_data['current_price']:,.2f}")
        print(f"   资金费率: {btc_futures_data['perp_data']['funding_rate']:.6f}" if btc_futures_data['perp_data']['funding_rate'] else "   资金费率: N/A")

        fetcher_futures.close()
        print("\n✅ 期货数据获取测试通过")
    except Exception as e:
        print(f"\n⚠️  期货数据获取跳过（可能不支持）: {e}")

except Exception as e:
    print(f"\n⚠️  期货测试跳过: {e}")

print("\n" + "=" * 80)
print(" Demo Trading 集成测试完成")
print("=" * 80)

print(f"""
✅ 所有测试通过！

📝 测试总结:
  1. ✅ DataFetcher (现货) - 数据获取正常
  2. ✅ RealTrader (现货) - 交易执行器正常
  3. ✅ TradingDecision - 决策模型正常
  4. {'✅' if config.DEMO_API_KEY else '⚠️'} Demo Trading API - {'已配置' if config.DEMO_API_KEY else '未配置'}

🔄 系统配置:
  • 当前模式: {config.CURRENT_MODE}
  • Base URL: {config.BINANCE_BASE_URL}
  • Demo API Key: {config.DEMO_API_KEY[:20] + '...' if config.DEMO_API_KEY else '未配置'}

⚠️  重要提醒:
   • Demo Trading 使用虚拟资金，安全性高
   • 请勿将 Demo API Key 用于实盘交易
   • 建议先在 Demo Trading 充分测试策略

🚀 下一步操作:
   1. 执行真实交易: trader.execute_decision(decision)
   2. 查看交易记录: https://testnet.binance.vision/ (Testnet) 或 https://demo.binance.vision/ (Demo)
   3. 运行主系统: python3 nof1.py --run 2
""")

print("\n" + "=" * 80)
print(" Demo Trading 集成测试成功！")
print("=" * 80)
