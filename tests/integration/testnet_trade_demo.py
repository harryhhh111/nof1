#!/usr/bin/env python3
"""
Testnet 交易演示脚本

演示如何在Binance Testnet中执行一笔小交易
"""

import sys
import os

# 添加项目根目录
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trading.real_trader import RealTrader
from models.trading_decision import TradingDecision

print("\n" + "=" * 80)
print(" Binance Testnet 交易演示")
print("=" * 80)

trader = RealTrader()

# 获取当前价格
btc_price = trader.get_symbol_price('BTCUSDT')
print(f"\n📊 BTCUSDT 当前价格: ${btc_price:,.2f}")

# 检查余额
balance = trader.get_account_balance()
usdt_balance = balance.get('USDT', 0)
print(f"💰 USDT余额: {usdt_balance:.2f}")

# 计算小仓位（1% of 10,000 USDT = $100）
test_amount_usdt = 100.0
btc_amount = test_amount_usdt / btc_price

print(f"\n💡 交易计划:")
print(f"   交易对: BTCUSDT")
print(f"   方向: BUY (买入)")
print(f"   数量: {btc_amount:.6f} BTC (≈${test_amount_usdt:.2f} USDT)")
print(f"   资金来源: 1% 虚拟资金")

confirm = input(f"\n❓ 确认执行测试交易？(输入 'yes' 确认): ")
if confirm.lower() != 'yes':
    print("   ❌ 已取消")
    trader.close()
    sys.exit(0)

print("\n" + "=" * 80)
print(" 执行交易...")
print("=" * 80)

try:
    # 执行市价买入
    result = trader.place_market_order(
        symbol='BTCUSDT',
        side='buy',
        amount=btc_amount,
        reason="Testnet演示交易 - 小仓位测试"
    )

    if result['status'] == 'success':
        print("\n✅ 交易成功！")
        print(f"   订单ID: {result['order_id']}")
        print(f"   成交价格: ${result['price']:,.2f}")
        print(f"   手续费: {result['fee']:.6f} BTC")

        # 检查余额变化
        new_balance = trader.get_account_balance()
        new_btc = new_balance.get('BTC', 0)
        new_usdt = new_balance.get('USDT', 0)

        print(f"\n📊 交易后余额:")
        print(f"   BTC: {new_btc:.6f}")
        print(f"   USDT: {new_usdt:.2f}")

        # 获取交易记录
        trades = trader.get_trades(1)
        if trades:
            latest_trade = trades[-1]
            print(f"\n📈 最新交易:")
            print(f"   时间: {latest_trade.get('timestamp', 'N/A')}")
            print(f"   方向: {latest_trade.get('side', 'N/A')}")
            print(f"   数量: {latest_trade.get('amount', 0):.6f}")
            print(f"   价格: ${latest_trade.get('price', 0):,.2f}")

    else:
        print(f"\n❌ 交易失败: {result.get('message', '未知错误')}")

except Exception as e:
    print(f"\n❌ 交易异常: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print(" 查看更多详情:")
print("=" * 80)
print("""
   • Web界面: https://testnet.binance.vision/
   • 查看完整余额: trader.get_account_balance()
   • 查看交易记录: trader.get_trades(100)
   • 运行查看器: python3 testnet_viewer.py

⚠️  重要提醒:
   • 这是模拟交易，使用虚拟资金
   • Testnet数据与实盘可能略有差异
   • 实盘交易前请充分测试
""")

trader.close()
