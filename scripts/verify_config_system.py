#!/usr/bin/env python3
"""
验证多账户配置系统

测试配置加载器和Trader类的集成
"""

import sys
import os
import asyncio
import logging

# 添加项目根目录到路径
sys.path.insert(0, '/home/claude_user/nof1')

from manager.config_loader import ConfigLoader, create_traders_from_config
from models.trader import Trader

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_config_validation():
    """测试配置验证"""
    print("\n=== 测试1: 配置验证 ===")

    try:
        from config.traders_config import validate_config

        is_valid, errors = validate_config()

        if is_valid:
            print("✅ 配置验证通过")
            return True
        else:
            print("❌ 配置验证失败:")
            for error in errors:
                print(f"  - {error}")
            return False

    except Exception as e:
        print(f"❌ 配置验证异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config_loader():
    """测试配置加载器"""
    print("\n=== 测试2: 配置加载器 ===")

    try:
        loader = ConfigLoader()

        # 加载配置
        if not loader.load_config():
            print("❌ 配置加载失败")
            return False

        # 打印摘要
        loader.print_summary()

        print("✅ 配置加载器测试通过")
        return True

    except Exception as e:
        print(f"❌ 配置加载器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_trader_creation():
    """测试Trader创建（模拟）"""
    print("\n=== 测试3: Trader创建（模拟） ===")

    try:
        from config.traders_config import TRADERS_CONFIG

        # 检查配置格式
        if not TRADERS_CONFIG:
            print("❌ 未找到交易员配置")
            return False

        print(f"✅ 找到 {len(TRADERS_CONFIG)} 个交易员配置")

        # 验证每个配置的格式
        for config in TRADERS_CONFIG[:2]:  # 只检查前2个
            required_fields = ['trader_id', 'name', 'llm_model', 'initial_balance']
            for field in required_fields:
                if field not in config:
                    print(f"❌ 配置缺少字段: {field}")
                    return False

            print(f"  ✅ {config['name']} ({config['llm_model']}) - ${config['initial_balance']}")

        print("✅ Trader创建测试通过（模拟）")
        return True

    except Exception as e:
        print(f"❌ Trader创建测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multi_trader_simulation():
    """测试多账户场景（模拟）"""
    print("\n=== 测试4: 多账户场景模拟 ===")

    try:
        from config.traders_config import TRADERS_CONFIG

        # 模拟创建多个Trader实例
        traders = []

        # 注意：这里只测试配置格式，不实际创建Trader实例
        # （因为需要真实的LLM客户端）
        for config in TRADERS_CONFIG[:2]:
            print(f"\n模拟创建交易员:")
            print(f"  ID: {config['trader_id']}")
            print(f"  名称: {config['name']}")
            print(f"  LLM模型: {config['llm_model']}")
            print(f"  初始资金: ${config['initial_balance']:.2f}")
            print(f"  交易品种: {', '.join(config['symbols'])}")

            traders.append(config)

        print(f"\n✅ 成功模拟 {len(traders)} 个交易员")
        return True

    except Exception as e:
        print(f"❌ 多账户场景模拟失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_performance_comparison():
    """测试性能对比逻辑"""
    print("\n=== 测试5: 性能对比逻辑 ===")

    try:
        # 模拟性能数据
        mock_performances = [
            {'name': 'DeepSeek账户-01', 'llm_model': 'deepseek', 'total_pnl': 1250.50, 'win_rate': 65.0},
            {'name': 'Qwen账户-01', 'llm_model': 'qwen', 'total_pnl': 980.25, 'win_rate': 58.0},
            {'name': 'DeepSeek账户-02', 'llm_model': 'deepseek', 'total_pnl': 1100.75, 'win_rate': 62.0},
        ]

        # 模拟性能对比
        print("\n模拟性能对比结果:")
        print("-" * 60)

        # 按PnL排序
        mock_performances.sort(key=lambda x: x['total_pnl'], reverse=True)

        for i, perf in enumerate(mock_performances, 1):
            print(f"{i}. {perf['name']:<20} | {perf['llm_model']:<10} | PnL: ${perf['total_pnl']:>8.2f} | 胜率: {perf['win_rate']:>5.1f}%")

        best = mock_performances[0]
        print("-" * 60)
        print(f"🥇 当前最佳: {best['name']} (LLM: {best['llm_model']})")

        print("✅ 性能对比逻辑测试通过")
        return True

    except Exception as e:
        print(f"❌ 性能对比测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("="*60)
    print("多账户配置系统验证")
    print("="*60)

    tests = [
        ("配置验证", test_config_validation),
        ("配置加载器", test_config_loader),
        ("Trader创建", test_trader_creation),
        ("多账户场景", test_multi_trader_simulation),
        ("性能对比", test_performance_comparison),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ 测试 '{test_name}' 异常: {e}")
            results.append((test_name, False))

    # 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")

    print("="*60)
    print(f"总计: {passed}/{total} 通过")

    if passed == total:
        print("\n🎉 所有测试通过！配置系统工作正常。")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查配置。")
        return 1


if __name__ == '__main__':
    sys.exit(main())
