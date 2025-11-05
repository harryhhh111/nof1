#!/usr/bin/env python3
"""
持仓查询调试工具

逐步调试持仓查询问题，找出失败原因
"""

import sys
import os

# 添加项目根目录
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from trading.real_trader import RealTrader

def debug_step_by_step():
    """逐步调试持仓查询"""
    print("=" * 80)
    print(" 持仓查询调试工具")
    print("=" * 80)

    try:
        trader = RealTrader(use_futures=False)
        print("✅ RealTrader 初始化成功")

        # 步骤1: 测试获取余额
        print("\n" + "=" * 80)
        print(" 步骤1: 测试获取余额")
        print("=" * 80)

        try:
            balance = trader.get_account_balance()
            if not balance:
                print("❌ 获取余额失败")
                print("\n💡 可能原因:")
                print("   1. API Key 未配置或无效")
                print("   2. API Key 权限不足 (需要 'Enable Reading')")
                print("   3. IP 被限制")
                print("\n🔧 解决方案:")
                print("   1. 检查 .env 文件中的 DEMO_API_KEY")
                print("   2. 在 https://demo.binance.com/ 开启读取权限")
                print("   3. 重启程序")
                return
            else:
                print(f"✅ 获取余额成功，共 {len(balance)} 个资产")
                print("\n余额详情:")
                for asset, amount in balance.items():
                    if amount > 0:
                        print(f"   {asset:>6}: {amount:>15.8f}")
        except Exception as e:
            print(f"❌ 获取余额异常: {e}")
            return

        # 步骤2: 测试获取单个价格
        print("\n" + "=" * 80)
        print(" 步骤2: 测试获取单个价格")
        print("=" * 80)

        test_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
        for symbol in test_symbols:
            try:
                price = trader.get_symbol_price(symbol)
                print(f"✅ {symbol}: ${price:,.2f}")
            except Exception as e:
                print(f"❌ {symbol}: {e}")

        # 步骤3: 测试获取持仓
        print("\n" + "=" * 80)
        print(" 步骤3: 测试获取持仓")
        print("=" * 80)

        try:
            positions = trader.get_open_positions()
            if not positions:
                print("⚠️  当前无持仓")
            else:
                print(f"✅ 获取持仓成功，共 {len(positions)} 个")
                print("\n持仓详情:")
                for pos in positions:
                    symbol = pos['symbol']
                    amount = pos.get('contracts', 0)
                    asset = pos.get('asset', 'N/A')
                    is_initial = pos.get('is_initial_asset', False)
                    price = pos.get('current_price')
                    value = pos.get('value')

                    initial_mark = "🏆" if is_initial else "  "
                    print(f"{initial_mark} {symbol}: {amount:.8f} {asset}")
                    if price and value:
                        print(f"   └─ ${price:,.2f} x {amount:.8f} = ${value:,.2f}")
        except Exception as e:
            print(f"❌ 获取持仓异常: {e}")
            import traceback
            traceback.print_exc()
            return

        # 步骤4: 详细调试持仓查询
        print("\n" + "=" * 80)
        print(" 步骤4: 详细调试持仓查询逻辑")
        print("=" * 80)

        print("\n🔍 调试信息:")
        print(f"   use_futures: {trader.use_futures}")
        print(f"   exchange type: {trader.exchange.type if hasattr(trader.exchange, 'type') else 'unknown'}")

        # 尝试手动获取所有资产
        print("\n📊 手动分析余额资产:")
        for asset, amount in balance.items():
            if asset not in ['USDT', 'USDC', 'BUSD'] and amount > 0.000001:
                symbol = asset + 'USDT'
                try:
                    price = trader.get_symbol_price(symbol)
                    value = amount * price
                    print(f"   {asset}: {amount:.8f} @ ${price:,.2f} = ${value:.2f}")
                except Exception as e:
                    print(f"   {asset}: {amount:.8f} @ ❌ {e}")

        trader.close()
        print("\n✅ 调试完成")

    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()

def test_ccxt_directly():
    """直接测试 CCXT 库"""
    print("\n" + "=" * 80)
    print(" 直接测试 CCXT 库")
    print("=" * 80)

    try:
        import ccxt

        print(f"\n📡 CCXT 版本: {ccxt.__version__}")
        print(f"🔧 交易所: Binance")

        # 创建交易所实例
        exchange_config = {
            'apiKey': config.BINANCE_API_KEY,
            'secret': config.BINANCE_SECRET_KEY,
            'sandbox': config.USE_TESTNET,
            'enableRateLimit': True,
            'baseUrl': config.BINANCE_BASE_URL if config.USE_TESTNET else None,
        }

        exchange = ccxt.binance(exchange_config)
        print(f"✅ 交易所实例创建成功")

        # 测试获取余额
        print("\n💰 测试获取余额:")
        try:
            balance = exchange.fetch_balance()
            total = balance.get('total', {})
            non_zero = {k: v for k, v in total.items() if v > 0}
            print(f"✅ 获取成功，共 {len(non_zero)} 个非零资产")
            for asset, amount in non_zero.items():
                print(f"   {asset:>6}: {amount:>15.8f}")
        except Exception as e:
            print(f"❌ 获取余额失败: {e}")
            return

        # 测试获取价格
        print("\n📊 测试获取价格:")
        try:
            ticker = exchange.fetch_ticker('BTCUSDT')
            print(f"✅ BTCUSDT: ${ticker['last']:,.2f}")
        except Exception as e:
            print(f"❌ 获取价格失败: {e}")

    except Exception as e:
        print(f"\n❌ CCXT 测试失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("\n" + "=" * 80)
    print(" 持仓查询调试指南")
    print("=" * 80)
    print("""
   此工具用于逐步调试持仓查询问题

   🔍 检查项目:
   1. API Key 配置和权限
   2. 余额获取
   3. 价格查询
   4. 持仓计算

   ⚠️  常见问题:
   • API Key 权限不足
   • 网络连接问题
   • 余额获取失败
   • 价格查询失败

   💡 解决方案:
   • 检查 DEMO_API_KEY 权限
   • 确认开启 'Enable Reading'
   • 重启程序
    """)

    # 步骤1: 调试持仓查询
    debug_step_by_step()

    # 步骤2: 直接测试 CCXT
    test_ccxt_directly()

    print("\n" + "=" * 80)
    print(" 📋 调试总结")
    print("=" * 80)
    print("""
   如果持仓查询失败，请检查:

   1. ✅ API Key 配置
      • 检查 .env 文件中的 DEMO_API_KEY
      • 确认 API Key 有效且未过期

   2. ✅ API Key 权限
      • 登录 https://demo.binance.com/
      • 进入 API 管理页面
      • 确保开启 'Enable Reading' 权限

   3. ✅ 网络连接
      • 确保网络可以访问 demo.binance.vision
      • 检查防火墙设置

   4. ✅ 程序重启
      • 重启程序
      • 重新加载配置

   📞 如需帮助:
   • 查看 DEMO_TRADING_INITIAL_FUNDS.md
   • 检查 config.py 中的配置
   • 运行 demo_quick_test.py 验证连接
    """)

if __name__ == '__main__':
    main()
