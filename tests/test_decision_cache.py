"""
决策缓存测试

测试缓存机制
"""

import unittest
import time
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scheduling.decision_cache import DecisionCache, PromptCache, MultiLevelCache


class TestDecisionCache(unittest.TestCase):
    """决策缓存测试"""

    def test_cache_set_and_get(self):
        """测试缓存设置和获取"""
        cache = DecisionCache(ttl_seconds=60)

        # 设置缓存
        symbol = "BTCUSDT"
        timeframe_data = {"price": 50000, "trend": "UP"}
        decision = {"action": "BUY", "confidence": 80}
        cache.set(symbol, timeframe_data, decision)

        # 获取缓存
        cached = cache.get(symbol, timeframe_data)

        self.assertIsNotNone(cached)
        self.assertEqual(cached[0], decision)

    def test_cache_expiration(self):
        """测试缓存过期"""
        cache = DecisionCache(ttl_seconds=1)  # 1秒过期

        symbol = "BTCUSDT"
        timeframe_data = {"price": 50000}
        decision = {"action": "SELL"}

        cache.set(symbol, timeframe_data, decision)
        self.assertIsNotNone(cache.get(symbol, timeframe_data))

        # 等待过期
        time.sleep(1.1)
        self.assertIsNone(cache.get(symbol, timeframe_data))

    def test_cache_key_generation(self):
        """测试缓存键生成"""
        cache = DecisionCache()

        data1 = {"price": 50000, "trend": "UP"}
        data2 = {"trend": "UP", "price": 50000}  # 顺序不同但内容相同

        key1 = cache._generate_key("BTCUSDT", data1)
        key2 = cache._generate_key("BTCUSDT", data2)

        # 相同数据应生成相同键
        self.assertEqual(key1, key2)

    def test_cache_is_valid(self):
        """测试缓存有效性检查"""
        cache = DecisionCache(ttl_seconds=60)

        symbol = "BTCUSDT"
        timeframe_data = {"price": 50000}
        decision = {"action": "HOLD"}

        # 设置前无效
        self.assertFalse(cache.is_valid(symbol, timeframe_data))

        # 设置后有效
        cache.set(symbol, timeframe_data, decision)
        self.assertTrue(cache.is_valid(symbol, timeframe_data))

    def test_cache_cleanup(self):
        """测试缓存清理"""
        cache = DecisionCache(ttl_seconds=1)

        # 设置多个缓存
        for i in range(5):
            cache.set(f"SYMBOL{i}", {"price": 50000}, {"action": "BUY"})

        # 等待过期
        time.sleep(1.1)

        # 清理后应该没有有效缓存
        self.assertEqual(cache.get_stats()['valid_entries'], 0)

    def test_cache_stats(self):
        """测试缓存统计"""
        cache = DecisionCache(ttl_seconds=60)

        # 初始统计
        stats = cache.get_stats()
        self.assertEqual(stats['total_entries'], 0)

        # 设置缓存
        cache.set("BTCUSDT", {"price": 50000}, {"action": "BUY"})
        cache.set("ETHUSDT", {"price": 3000}, {"action": "SELL"})

        stats = cache.get_stats()
        self.assertEqual(stats['total_entries'], 2)
        self.assertEqual(stats['valid_entries'], 2)

    def test_cache_memory_usage(self):
        """测试内存使用量"""
        cache = DecisionCache()

        cache.set("BTCUSDT", {"price": 50000}, {"action": "BUY"})
        memory = cache.get_memory_usage()

        self.assertGreater(memory, 0)


class TestPromptCache(unittest.TestCase):
    """提示缓存测试"""

    def test_prompt_hash(self):
        """测试提示哈希"""
        cache = PromptCache()

        prompt = "这是一个测试提示"
        hash1 = cache.get_hash(prompt)
        hash2 = cache.get_hash(prompt)

        # 相同提示应生成相同哈希
        self.assertEqual(hash1, hash2)

        # 不同提示应生成不同哈希
        prompt2 = "这是另一个测试提示"
        hash3 = cache.get_hash(prompt2)
        self.assertNotEqual(hash1, hash3)

    def test_cache_clear(self):
        """测试清空缓存"""
        cache = PromptCache()

        cache.get_hash("提示1")
        cache.get_hash("提示2")
        cache.get_hash("提示3")

        self.assertEqual(len(cache.cache), 3)

        cache.clear()
        self.assertEqual(len(cache.cache), 0)


class TestMultiLevelCache(unittest.TestCase):
    """多级缓存测试"""

    def test_multi_level_initialization(self):
        """测试多级缓存初始化"""
        levels = {
            'fast': 300,   # 5分钟
            'default': 600, # 10分钟
            'slow': 900     # 15分钟
        }

        multi_cache = MultiLevelCache(levels)

        # 验证所有级别都已创建
        self.assertIn('fast', multi_cache.levels)
        self.assertIn('default', multi_cache.levels)
        self.assertIn('slow', multi_cache.levels)

    def test_level_get_and_set(self):
        """测试级别获取和设置"""
        levels = {
            'fast': 300,
            'slow': 900
        }

        multi_cache = MultiLevelCache(levels)

        # 设置默认级别缓存
        multi_cache.set("BTCUSDT", {"price": 50000}, {"action": "BUY"})

        # 获取默认级别缓存
        cached = multi_cache.get("BTCUSDT", {"price": 50000})
        self.assertIsNotNone(cached)

        # 设置快速级别缓存
        multi_cache.set("ETHUSDT", {"price": 3000}, {"action": "SELL"}, level='fast')

        # 获取快速级别缓存
        cached_fast = multi_cache.get("ETHUSDT", {"price": 3000}, level='fast')
        self.assertIsNotNone(cached_fast)

    def test_set_level(self):
        """测试设置当前级别"""
        multi_cache = MultiLevelCache({'fast': 300, 'slow': 900})

        # 初始级别
        self.assertEqual(multi_cache.current_level, 'default')

        # 切换级别
        multi_cache.set_level('fast')
        self.assertEqual(multi_cache.current_level, 'fast')

    def test_all_stats(self):
        """测试获取所有级别统计"""
        levels = {
            'fast': 300,
            'slow': 900
        }

        multi_cache = MultiLevelCache(levels)

        # 设置缓存
        multi_cache.set("BTCUSDT", {"price": 50000}, {"action": "BUY"}, level='fast')
        multi_cache.set("ETHUSDT", {"price": 3000}, {"action": "SELL"}, level='slow')

        # 获取所有统计
        all_stats = multi_cache.get_all_stats()

        self.assertIn('fast', all_stats)
        self.assertIn('slow', all_stats)
        self.assertEqual(all_stats['fast']['total_entries'], 1)
        self.assertEqual(all_stats['slow']['total_entries'], 1)


if __name__ == '__main__':
    unittest.main()
