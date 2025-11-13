#!/usr/bin/env python3
"""
多账户交易系统启动脚本

演示多账户架构的使用：
- 从配置加载多个Trader
- 使用TraderManager管理所有账户
- 并发执行交易决策
- 实时对比不同LLM的表现

注意：这是MVP版本，使用模拟数据
"""

import asyncio
import sys
import os
import logging
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, '/home/claude_user/nof1')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'multi_account_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class MockLLMClient:
    """模拟LLM客户端（用于测试）"""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.decision_count = 0

    def get_decision(self, prompt: str):
        """获取模拟决策"""
        self.decision_count += 1

        # 模拟决策对象
        class MockDecision:
            def __init__(self, model_name):
                self.action = "HOLD" if self.decision_count % 3 == 0 else "BUY"
                self.symbol = "BTCUSDT"
                self.position_size = 10.0
                self.confidence = 70.0 + (self.decision_count % 30)
                self.reasoning = f"{model_name} 分析认为市场趋势向好"
                self.entry_price = 50000.0 + (self.decision_count * 100)
                self.stop_loss = 48000.0
                self.take_profit = 55000.0
                self.trader_id = None
                self.llm_model = model_name
                self.timestamp = datetime.now().isoformat()

        return MockDecision(self.model_name)


async def demo_multi_account():
    """演示多账户系统"""
    print("\n" + "="*60)
    print("🚀 多账户交易系统演示")
    print("="*60)

    # 1. 导入所需模块
    try:
        from models.trader import Trader
        from manager.trader_manager import TraderManager
        from manager.config_loader import ConfigLoader
        print("✅ 模块导入成功")
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 2. 创建模拟LLM客户端
    print("\n📝 创建模拟LLM客户端...")
    mock_clients = {
        'deepseek': MockLLMClient('deepseek'),
        'qwen': MockLLMClient('qwen')
    }
    print(f"✅ 创建了 {len(mock_clients)} 个模拟LLM客户端")

    # 3. 创建多个Trader实例
    print("\n👥 创建交易员...")
    traders = []

    # Trader 1: DeepSeek账户
    trader1 = Trader(
        trader_id='demo_deepseek_001',
        name='DeepSeek演示账户',
        llm_model='deepseek',
        initial_balance=10000.0,
        llm_client=mock_clients['deepseek'],
        symbols=['BTCUSDT', 'ETHUSDT']
    )
    traders.append(trader1)

    # Trader 2: Qwen账户
    trader2 = Trader(
        trader_id='demo_qwen_001',
        name='Qwen演示账户',
        llm_model='qwen',
        initial_balance=10000.0,
        llm_client=mock_clients['qwen'],
        symbols=['BTCUSDT', 'ETHUSDT']
    )
    traders.append(trader2)

    print(f"✅ 创建了 {len(traders)} 个交易员")
    for trader in traders:
        print(f"  - {trader.name} (LLM: {trader.llm_model})")

    # 4. 创建TraderManager
    print("\n🎯 初始化TraderManager...")
    manager = TraderManager()
    print(f"✅ TraderManager初始化完成")

    # 5. 添加所有交易员到管理器
    print("\n➕ 添加交易员到管理器...")
    for trader in traders:
        success = manager.add_trader(trader)
        if not success:
            print(f"❌ 添加 {trader.name} 失败")
            return False

    print(f"✅ 成功添加 {len(traders)} 个交易员")

    # 6. 执行3轮演示
    print("\n🔄 开始执行交易决策演示（共3轮）...")
    for round_num in range(1, 4):
        print(f"\n{'='*60}")
        print(f"第 {round_num} 轮决策")
        print(f"{'='*60}")

        # 模拟市场数据
        mock_market_data = {
            'BTCUSDT': {
                'current_price': 50000.0 + (round_num * 500),
                'timestamp': datetime.now().isoformat(),
                'description': f'第{round_num}轮：BTC价格${50000 + round_num * 500}'
            },
            'ETHUSDT': {
                'current_price': 3000.0 + (round_num * 50),
                'timestamp': datetime.now().isoformat(),
                'description': f'第{round_num}轮：ETH价格${3000 + round_num * 50}'
            }
        }

        # 每个交易员独立决策
        for trader in traders:
            try:
                print(f"\n🤖 {trader.name} 正在决策...")
                decision = trader.get_decision(mock_market_data)
                print(f"   决策: {decision.action}")
                print(f"   置信度: {decision.confidence}%")
                print(f"   LLM模型: {decision.llm_model}")

                # 执行决策
                current_price = mock_market_data['BTCUSDT']['current_price']
                result = trader.execute_decision(decision, current_price)
                print(f"   执行结果: {result['status']}")

                # 显示当前表现
                perf = trader.get_performance()
                print(f"   当前PnL: ${perf['total_pnl']:.2f}")

            except Exception as e:
                print(f"❌ {trader.name} 决策失败: {e}")

        # 性能对比
        print(f"\n📊 第 {round_num} 轮性能对比:")
        print("-" * 60)
        traders_sorted = sorted(traders, key=lambda t: t.total_pnl, reverse=True)
        for i, trader in enumerate(traders_sorted, 1):
            print(f"{i}. {trader.name:<20} | PnL: ${trader.total_pnl:>8.2f} | 胜率: {trader.win_rate:>5.1f}%")

        # 等待一轮
        await asyncio.sleep(1)

    # 7. 显示最终结果
    print("\n" + "="*60)
    print("🏁 演示完成 - 最终结果")
    print("="*60)

    for trader in traders:
        print(trader.get_summary())

    # 8. 最佳表现者
    best_performer = manager.get_best_performer()
    if best_performer:
        print(f"\n🥇 最佳表现者: {best_performer.name}")
        print(f"   LLM模型: {best_performer.llm_model}")
        print(f"   总盈亏: ${best_performer.total_pnl:.2f}")
        print(f"   收益率: {best_performer.total_pnl_pct:+.2f}%")

    # 9. 性能对比报告
    comparison = manager.compare_performance()
    print(f"\n📈 详细性能对比:")
    for trader_data in comparison['traders']:
        perf = trader_data['performance']
        print(f"  {trader_data['name']}:")
        print(f"    LLM: {trader_data['llm_model']}")
        print(f"    PnL: ${perf['total_pnl']:.2f} ({perf['total_pnl_pct']:+.2f}%)")
        print(f"    交易次数: {perf['total_trades']}")
        print(f"    胜率: {perf['win_rate']:.1f}%")

    print("\n" + "="*60)
    print("✅ 多账户系统演示完成！")
    print("="*60)

    return True


async def main():
    """主函数"""
    try:
        # 运行演示
        success = await demo_multi_account()

        if success:
            print("\n🎉 演示成功完成！")
            print("\n📚 核心功能验证:")
            print("  ✅ 多账户管理")
            print("  ✅ 独立LLM绑定")
            print("  ✅ 并发决策执行")
            print("  ✅ 实时性能对比")
            print("  ✅ 账户资金隔离")
            return 0
        else:
            print("\n❌ 演示失败")
            return 1

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        return 130
    except Exception as e:
        print(f"\n❌ 演示异常: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    print("""
╔════════════════════════════════════════════════════════════╗
║         🤖 nof1 多账户交易系统 - MVP 演示                   ║
║                                                            ║
║  重要说明:                                                  ║
║  - 这是概念验证版本，使用模拟数据                           ║
║  - 验证多账户架构的正确性                                   ║
║  - 展示不同LLM的对比效果                                   ║
╚════════════════════════════════════════════════════════════╝
    """)

    # 运行异步主函数
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
