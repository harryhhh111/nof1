#!/usr/bin/env python3
"""
测试运行脚本

运行所有单元测试和集成测试。
"""

import unittest
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入所有测试模块
from tests.test_config import TestConfig
from tests.test_indicators import TestTechnicalIndicators
from tests.test_database import TestDatabase
from tests.test_data_fetcher import TestDataFetcher
from tests.test_scheduler import TestDataScheduler, TestScheduledTask
from tests.test_integration import TestSystemIntegration


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("Nof1 数据获取系统 - 测试套件")
    print("=" * 60)

    # 创建测试套件
    test_suite = unittest.TestSuite()

    # 添加测试类
    test_classes = [
        TestConfig,
        TestTechnicalIndicators,
        TestDatabase,
        TestDataFetcher,
        TestDataScheduler,
        TestScheduledTask,
        TestSystemIntegration
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # 输出结果
    print("\n" + "=" * 60)
    print("测试结果")
    print("=" * 60)
    print(f"运行测试: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")

    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")

    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
