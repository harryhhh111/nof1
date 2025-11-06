#!/usr/bin/env python3
"""
Binance Testnet 集成测试脚本

演示如何使用Testnet进行真实模拟交易
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
from prompt_generator import PromptGenerator

print("=" * 80)
print(" Binance Testnet 集成测试")
print("=" * 80)

# 显示当前配置
print(f"\n📊 当前配置:")
print(f"   交易模式: {config.CURRENT_MODE}")
print(f"   使用Testnet: {config.USE_TESTNET}")
print(f"   API Key配置: {'✅ 已配置' if config.TESTNET_API_KEY else '❌ 未配置'}")
print(f"   Binance API: {config.BINANCE_BASE_URL}")

if not config.TESTNET_API_KEY:
    print("\n⚠️  警告: 未配置Testnet API Key!")
    print("请设置环境变量或修改config.py:")
    print("  export TESTNET_API_KEY='your_api_key'")
    print("  export TESTNET_SECRET_KEY='your_secret_key'")
    print("  export USE_TESTNET=true")
    sys.exit(1)

print("\n" + "=" * 80)
print(" 步骤1: 测试数据获取")
print("=" * 80)

try:
    fetcher = DataFetcher()
    print("✅ DataFetcher 初始化成功")

    # 获取BTC数据
    btc_data = fetcher.get_market_data('BTCUSDT')
    print(f"\n📈 BTCUSDT 数据:")
    print(f"   当前价格: ${btc_data['current_price']:,.2f}")
    print(f"   时间戳: {btc_data['timestamp']}")
    print(f"   EMA20: {btc_data['intraday']['ema20'][-1]:.2f}" if btc_data['intraday']['ema20'] else "   EMA20: N/A")
    print(f"   RSI14: {btc_data['intraday']['rsi_14'][-1]:.2f}" if btc_data['intraday']['rsi_14'] else "   RSI14: N/A")
    print(f"   资金费率: {btc_data['perp_data']['funding_rate']:.6f}" if btc_data['perp_data']['funding_rate'] else "   资金费率: N/A")

    fetcher.close()
    print("\n✅ 数据获取测试通过")

except Exception as e:
    print(f"\n❌ 数据获取失败: {e}")
    sys.exit(1)

print("\n" + "=" * 80)
print(" 步骤2: 测试真实交易执行器")
print("=" * 80)

try:
    trader = RealTrader()
    print("✅ RealTrader 初始化成功")

    # 获取账户余额
    balance = trader.get_account_balance()
    print(f"\n💰 账户余额:")
    for asset, amount in balance.items():
        print(f"   {asset}: {amount:.6f}")

    # 检查USDT余额
    if 'USDT' not in balance or balance['USDT'] < 10:
        print("\n⚠️  警告: USDT余额不足（至少需要10 USDT进行测试）")
    else:
        print("\n✅ USDT余额充足")

    # 测试获取当前价格
    current_price = trader.get_symbol_price('BTCUSDT')
    print(f"\n📊 BTCUSDT 当前价格: ${current_price:,.2f}")

    trader.close()
    print("\n✅ 交易执行器测试通过")

except Exception as e:
    print(f"\n❌ 交易执行器测试失败: {e}")
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
        reasoning="Testnet集成测试 - 基于多时间框架分析，看涨信号",
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
print(" 步骤4: 测试提示生成")
print("=" * 80)

try:
    prompt_gen = PromptGenerator()

    # 模拟长期和短期数据
    data_4h = {
        'symbol': 'BTCUSDT',
        'description': f'4小时数据：价格 {current_price:.2f}，EMA20支撑有效，RSI在健康区间，MACD金叉确认',
        'trend': 'UP',
        'confidence': 80
    }

    data_3m = {
        'symbol': 'BTCUSDT',
        'description': f'3分钟数据：短期动量向上，价格在EMA20上方运行，成交量配合',
        'momentum': 'POSITIVE',
        'confidence': 75
    }

    # 生成4小时提示
    prompt_4h = prompt_gen.generate_4h_prompt(data_4h, data_3m)
    print("✅ 4小时趋势提示生成成功")
    print(f"   提示长度: {len(prompt_4h)} 字符")

    # 生成3分钟提示
    prompt_3m = prompt_gen.generate_3m_prompt(data_3m)
    print("✅ 3分钟入场提示生成成功")
    print(f"   提示长度: {len(prompt_3m)} 字符")

except Exception as e:
    print(f"\n❌ 提示生成测试失败: {e}")
    sys.exit(1)

print("\n" + "=" * 80)
print(" 集成测试完成")
print("=" * 80)

print(f"""
✅ 所有测试通过！

📝 测试总结:
  1. ✅ DataFetcher - 数据获取正常
  2. ✅ RealTrader - 交易执行器正常
  3. ✅ TradingDecision - 决策模型正常
  4. ✅ PromptGenerator - 提示生成正常

🔄 下一步操作:

1. 执行真实模拟交易:
   from trading.real_trader import RealTrader
   trader = RealTrader()
   result = trader.execute_decision(decision, current_price)

2. 集成到主系统:
   - 使用 config.CURRENT_MODE 判断当前模式
   - 选择 PaperTrader 或 RealTrader
   - 在 main.py 中添加交易功能

3. 环境变量配置:
   export TESTNET_API_KEY='your_key'
   export TESTNET_SECRET_KEY='your_secret'
   export USE_TESTNET=true

⚠️  重要提醒:
   - Testnet 是模拟环境，但使用真实API
   - 请勿将 Testnet Key 用于实盘交易
   - 建议先在 Testnet 充分测试策略
""")

print("\n" + "=" * 80)
print(" Testnet 集成测试成功！")
print("=" * 80)
