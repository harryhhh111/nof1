#!/usr/bin/env python3
"""
检查 Binance Demo Trading 初始资金

验证 Demo Trading 账户的初始资产配置
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from trading.real_trader import RealTrader

def check_initial_funds():
    """检查初始资金"""
    print("=" * 80)
    print(" Binance Demo Trading 初始资金检查")
    print("=" * 80)

    # 显示预期初始资金
    print("\n📋 预期初始资金 (Demo Trading Reset 后):")
    print("   ┌──────┬─────────────┬──────────────────────────┐")
    print("   │ 资产 │   数量      │         价值估算          │")
    print("   ├──────┼─────────────┼──────────────────────────┤")
    print("   │ USDT │   5,000     │ 基准货币，主要交易资产     │")
    print("   │ BTC  │   0.05      │ 比特币初始持仓             │")
    print("   │ ETH  │   1         │ 以太坊初始持仓             │")
    print("   │ BNB  │   2         │ 币安币初始持仓             │")
    print("   └──────┴─────────────┴──────────────────────────┘")

    # 显示当前配置
    print(f"\n🔧 当前配置:")
    print(f"   交易模式: {config.CURRENT_MODE.upper()}")
    print(f"   Demo API: {config.DEMO_API_KEY[:20]}..." if config.DEMO_API_KEY else "   Demo API: ❌ 未配置")
    print(f"   平台 URL: {config.BINANCE_BASE_URL}")

    # 获取实际余额
    print(f"\n📊 正在获取实际余额...")
    try:
        trader = RealTrader(use_futures=False)
        balance = trader.get_account_balance()

        if not balance:
            print("\n⚠️  警告: 无法获取余额 (API权限不足)")
            print("   请检查:")
            print("   1. API Key 是否开启 'Enable Reading' 权限")
            print("   2. 是否使用正确的 Demo Trading API Key")
            print("   3. 参考: https://demo.binance.com/en/my/wallet/demo/main")
            return

        print("\n✅ 实际余额:")
        print("   ┌──────┬─────────────┬──────────────────────────┐")
        print("   │ 资产 │   数量      │         状态             │")
        print("   ├──────┼─────────────┼──────────────────────────┤")

        # 预期初始资产
        expected_assets = {
            'USDT': 5000,
            'BTC': 0.05,
            'ETH': 1.0,
            'BNB': 2.0
        }

        matched_assets = []
        for asset, expected_amount in expected_assets.items():
            actual_amount = balance.get(asset, 0)
            if abs(actual_amount - expected_amount) < 0.001:
                status = "✅ 匹配"
                matched_assets.append(asset)
            else:
                status = f"⚠️  差异: {actual_amount}"
            print(f"   │ {asset:<4} │ {actual_amount:>9.6f} │ {status:<24} │")

        # 显示其他资产
        for asset, amount in balance.items():
            if asset not in expected_assets and amount > 0:
                print(f"   │ {asset:<4} │ {amount:>9.6f} │ ℹ️  其他资产          │")

        print("   └──────┴─────────────┴──────────────────────────┘")

        # 计算总价值
        try:
            btc_price = trader.get_symbol_price('BTCUSDT')
            eth_price = trader.get_symbol_price('ETHUSDT')
            # bnb_price = trader.get_symbol_price('BNBUSDT')  # 可能获取失败

            usdt_value = balance.get('USDT', 0)
            btc_value = balance.get('BTC', 0) * btc_price
            eth_value = balance.get('ETH', 0) * eth_price

            total_value = usdt_value + btc_value + eth_value

            print(f"\n💰 价值估算:")
            print(f"   USDT:  ${usdt_value:,.2f}")
            print(f"   BTC:   ${btc_value:,.2f}  ({balance.get('BTC', 0):.6f} @ ${btc_price:,.2f})")
            print(f"   ETH:   ${eth_value:,.2f}  ({balance.get('ETH', 0):.6f} @ ${eth_price:,.2f})")
            print(f"   ─────────────────────")
            print(f"   总计:  ${total_value:,.2f} USDT")
        except Exception as e:
            print(f"\n⚠️  价值估算部分失败: {e}")

        # 检查匹配情况
        print(f"\n📋 匹配检查:")
        if len(matched_assets) == len(expected_assets):
            print(f"   ✅ 所有初始资产匹配! ({len(matched_assets)}/{len(expected_assets)})")
        else:
            print(f"   ⚠️  部分匹配: {len(matched_assets)}/{len(expected_assets)}")
            if matched_assets:
                print(f"      匹配: {', '.join(matched_assets)}")
            missing = set(expected_assets.keys()) - set(matched_assets)
            if missing:
                print(f"      缺失: {', '.join(missing)}")

        trader.close()

    except Exception as e:
        print(f"\n❌ 获取余额失败: {e}")
        print("\n可能原因:")
        print("  1. API Key 无效或权限不足")
        print("  2. 网络连接问题")
        print("  3. Demo Trading 平台维护")
        print("\n解决方案:")
        print("  1. 检查 .env 文件中的 API Key 配置")
        print("  2. 确认 API Key 开启读取权限")
        print("  3. 访问 https://demo.binance.com/ 重置账户")

def main():
    """主函数"""
    try:
        check_initial_funds()

        print("\n" + "=" * 80)
        print(" 📝 说明")
        print("=" * 80)
        print("""
   • Demo Trading 账户 Reset 后会获得初始资金
   • 如果余额不匹配，可以在 https://demo.binance.com/ 进行 Reset
   • API Key 需要开启 "Enable Reading" 权限才能查询余额
   • Nof1 系统主要使用 USDT 进行交易决策

   🔗 相关链接:
   • Demo Trading: https://demo.binance.com/
   • 钱包: https://demo.binance.com/en/my/wallet/demo/main
   • API 管理: https://demo.binance.com/en/my/settings/api-management

   📚 文档:
   • 初始资金说明: DEMO_TRADING_INITIAL_FUNDS.md
   • 升级指南: DEMO_TRADING_UPGRADE.md
   • 迁移报告: DEMO_TRADING_MIGRATION_REPORT.md
        """)

        print("\n" + "=" * 80)
        print(" ✅ 检查完成")
        print("=" * 80)

    except KeyboardInterrupt:
        print("\n\n   👋 已取消")
    except Exception as e:
        print(f"\n\n   ❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
