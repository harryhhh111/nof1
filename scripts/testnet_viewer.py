#!/usr/bin/env python3
"""
Testnet 持仓和交易查看器

实时查看Binance Testnet的账户余额、持仓和交易记录
"""

import sys
import os
from datetime import datetime
from decimal import Decimal

# 添加项目根目录
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database

from trading.real_trader import RealTrader

def format_currency(amount, symbol='USDT'):
    """格式化货币显示"""
    if isinstance(amount, (int, float)):
        if symbol in ['BTC', 'ETH', 'BNB', 'SOL']:
            return f"{amount:.6f} {symbol}"
        else:
            return f"{amount:.2f} {symbol}"
    return f"{amount} {symbol}"

def show_account_balance(trader):
    """显示账户余额"""
    print("\n" + "=" * 80)
    print(" 💰 账户余额")
    print("=" * 80)

    balance = trader.get_account_balance()

    # 按余额大小排序
    sorted_balance = sorted(balance.items(), key=lambda x: x[1], reverse=True)

    # 计算USDT价值（简化）
    btc_price = trader.get_symbol_price('BTCUSDT')
    eth_price = trader.get_symbol_price('ETHUSDT')

    usdt_value = 0
    for asset, amount in sorted_balance:
        if amount > 0:
            value_str = format_currency(amount, asset)
            print(f"   {asset:12} : {value_str}")

            # 粗略估算USDT价值
            if asset == 'USDT':
                usdt_value += amount
            elif asset == 'BTC':
                usdt_value += amount * btc_price
            elif asset == 'ETH':
                usdt_value += amount * eth_price

    print(f"\n   {'估算总价值':12} ≈ ${usdt_value:,.2f} USDT")

def show_positions(trader):
    """显示持仓信息"""
    print("\n" + "=" * 80)
    print(" 📊 当前持仓")
    print("=" * 80)

    try:
        positions = trader.get_open_positions()

        if not positions:
            print("   📭 当前无持仓")
            return

        for pos in positions:
            symbol = pos['symbol']
            size = float(pos.get('contracts', 0))
            side = pos['side']
            entry_price = float(pos.get('entryPrice', 0))
            margin = float(pos.get('margin', 0))

            if abs(size) > 0.0001:  # 只显示有效持仓
                print(f"\n   {symbol}")
                print(f"   ├─ 方向: {side}")
                print(f"   ├─ 数量: {size:.6f}")
                print(f"   ├─ 入场价: ${entry_price:,.2f}")
                print(f"   ├─ 保证金: ${margin:,.2f}")
                print(f"   └─ 保证金率: {pos.get('percentage', 0):.2f}%")

    except Exception as e:
        print(f"   ⚠️  获取持仓信息失败: {e}")

def show_recent_trades(trader, limit=20):
    """显示最近的交易记录"""
    print("\n" + "=" * 80)
    print(f" 📈 最近 {limit} 笔交易")
    print("=" * 80)

    trades = trader.get_trades(limit=limit)

    if not trades:
        print("   📭 暂无交易记录")
        return

    # 显示表头
    print("   时间                  交易对         方向   数量           价格        PnL")
    print("   " + "-" * 75)

    for trade in trades[-limit:]:  # 显示最近的交易
        timestamp = trade.get('timestamp', '')
        if isinstance(timestamp, str):
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                time_str = timestamp[:19]
        else:
            time_str = str(timestamp)

        symbol = trade.get('symbol', 'N/A')[:12]
        side = trade.get('side', 'N/A')[:6]
        amount = trade.get('filled_amount', 0) or trade.get('amount', 0)
        price = trade.get('filled_price', 0) or trade.get('price', 0)
        pnl = trade.get('pnl', 0)

        print(f"   {time_str:<20} {symbol:<13} {side:<7} {amount:>12.6f} {price:>12.2f} {pnl:>10.2f}")

def show_trading_pairs(trader):
    """显示热门交易对信息"""
    print("\n" + "=" * 80)
    print(" 📊 热门交易对价格")
    print("=" * 80)

    pairs = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'DOGEUSDT']

    for pair in pairs:
        try:
            price = trader.get_symbol_price(pair)
            base, quote = pair[:-4], pair[-4:]
            print(f"   {base:8} / {quote:4} : ${price:>15,.2f}")
        except Exception as e:
            print(f"   {pair:<15} : ⚠️  获取失败 ({e})")

def main():
    """主函数"""
    print("\n" + "=" * 80)
    print(" Binance Testnet 持仓与交易查看器")
    print("=" * 80)

    try:
        # 初始化交易器
        trader = RealTrader()

        # 显示所有信息
        show_account_balance(trader)
        show_positions(trader)
        show_recent_trades(trader)
        show_trading_pairs(trader)

        print("\n" + "=" * 80)
        print(" 💡 提示")
        print("=" * 80)
        print("""
   • 这是模拟交易环境，使用虚拟资金
   • 查看完整交易记录: trader.get_trades(100)
   • 下单示例:
       trader.place_market_order('BTCUSDT', 'buy', 0.001)
   • 设置止损:
       trader.set_stop_loss('BTCUSDT', 'long', 0.001, 95000)
        """)

        trader.close()

    except KeyboardInterrupt:
        print("\n\n   👋 已退出")
    except Exception as e:
        print(f"\n\n   ❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
