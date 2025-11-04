"""
决策缓存

用于避免重复调用LLM API，节省成本
"""

import time
import hashlib
import json
from typing import Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class DecisionCache:
    """
    决策缓存

    用于缓存LLM决策，避免重复调用
    """

    def __init__(self, ttl_seconds: int = 600):
        """
        初始化缓存

        Args:
            ttl_seconds: 缓存生存时间（秒），默认10分钟
        """
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Tuple[Any, float]] = {}  # {cache_key: (data, timestamp)}

    def _generate_key(
        self,
        symbol: str,
        timeframe_data: Dict[str, Any],
        prompt_hash: Optional[str] = None
    ) -> str:
        """
        生成缓存键

        Args:
            symbol: 交易对
            timeframe_data: 时间框架数据
            prompt_hash: 提示哈希（可选）

        Returns:
            缓存键
        """
        # 创建内容摘要
        content = {
            'symbol': symbol,
            'data': timeframe_data
        }

        # 如果有提示哈希，添加到内容中
        if prompt_hash:
            content['prompt_hash'] = prompt_hash

        # 生成JSON字符串并计算哈希
        content_str = json.dumps(content, sort_keys=True, default=str)
        cache_key = hashlib.md5(content_str.encode()).hexdigest()

        return cache_key

    def get(
        self,
        symbol: str,
        timeframe_data: Dict[str, Any]
    ) -> Optional[Tuple[Any, float]]:
        """
        获取缓存的决策

        Args:
            symbol: 交易对
            timeframe_data: 时间框架数据

        Returns:
            (决策, 缓存时间戳) 或 None
        """
        cache_key = self._generate_key(symbol, timeframe_data)

        if cache_key not in self.cache:
            return None

        cached_data, timestamp = self.cache[cache_key]

        # 检查是否过期
        if time.time() - timestamp > self.ttl_seconds:
            del self.cache[cache_key]
            return None

        return cached_data, timestamp

    def set(
        self,
        symbol: str,
        timeframe_data: Dict[str, Any],
        decision: Any,
        timestamp: Optional[float] = None
    ):
        """
        设置缓存

        Args:
            symbol: 交易对
            timeframe_data: 时间框架数据
            decision: 决策
            timestamp: 时间戳（默认当前时间）
        """
        if timestamp is None:
            timestamp = time.time()

        cache_key = self._generate_key(symbol, timeframe_data)
        self.cache[cache_key] = (decision, timestamp)

        # 清理过期缓存
        self._cleanup()

    def is_valid(
        self,
        symbol: str,
        timeframe_data: Dict[str, Any]
    ) -> bool:
        """
        检查缓存是否有效

        Args:
            symbol: 交易对
            timeframe_data: 时间框架数据

        Returns:
            是否有效
        """
        cached_data = self.get(symbol, timeframe_data)
        return cached_data is not None

    def _cleanup(self):
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = []

        for key, (_, timestamp) in self.cache.items():
            if current_time - timestamp > self.ttl_seconds:
                expired_keys.append(key)

        for key in expired_keys:
            del self.cache[key]

    def clear(self):
        """清空缓存"""
        self.cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计

        Returns:
            统计信息
        """
        current_time = time.time()
        valid_count = 0
        expired_count = 0

        for _, timestamp in self.cache.values():
            if current_time - timestamp > self.ttl_seconds:
                expired_count += 1
            else:
                valid_count += 1

        return {
            'total_entries': len(self.cache),
            'valid_entries': valid_count,
            'expired_entries': expired_count,
            'ttl_seconds': self.ttl_seconds,
            'hit_rate': self._calculate_hit_rate()
        }

    def _calculate_hit_rate(self) -> float:
        """计算命中率（简化版本）"""
        # 这里简化处理，实际可以在生产环境中添加更详细的跟踪
        return 0.0

    def get_memory_usage(self) -> int:
        """
        获取内存使用量

        Returns:
            内存使用量（字节）
        """
        size = 0
        for key, (value, _) in self.cache.items():
            size += len(key)  # 键大小
            if isinstance(value, str):
                size += len(value)
            else:
                size += len(json.dumps(value, default=str))
        return size


class PromptCache:
    """
    提示缓存

    用于缓存提示的哈希值，避免重复生成
    """

    def __init__(self):
        self.cache: Dict[str, str] = {}

    def get_hash(self, prompt: str) -> str:
        """
        获取提示的哈希值

        Args:
            prompt: 提示文本

        Returns:
            哈希值
        """
        if prompt not in self.cache:
            self.cache[prompt] = hashlib.md5(prompt.encode()).hexdigest()
        return self.cache[prompt]

    def clear(self):
        """清空缓存"""
        self.cache.clear()


class MultiLevelCache:
    """
    多级缓存

    支持不同TTL的缓存层级
    """

    def __init__(self, levels: Dict[str, int]):
        """
        初始化多级缓存

        Args:
            levels: {level_name: ttl_seconds} 字典
        """
        # 确保总是有default级别
        if 'default' not in levels:
            levels['default'] = 600  # 默认10分钟

        self.levels = {
            name: DecisionCache(ttl) for name, ttl in levels.items()
        }
        self.current_level = 'default'

    def get_level(self, name: str) -> DecisionCache:
        """
        获取指定级别的缓存

        Args:
            name: 级别名称

        Returns:
            缓存实例
        """
        if name in self.levels:
            return self.levels[name]
        # 如果指定级别不存在，返回当前级别
        return self.levels[self.current_level]

    def set_level(self, name: str):
        """
        设置当前级别

        Args:
            name: 级别名称
        """
        if name in self.levels:
            self.current_level = name

    def get(self, symbol: str, timeframe_data: Dict[str, Any], level: str = 'default') -> Optional[Tuple[Any, float]]:
        """获取缓存"""
        cache = self.get_level(level)
        return cache.get(symbol, timeframe_data)

    def set(self, symbol: str, timeframe_data: Dict[str, Any], decision: Any, level: str = 'default'):
        """设置缓存"""
        cache = self.get_level(level)
        cache.set(symbol, timeframe_data, decision)

    def is_valid(self, symbol: str, timeframe_data: Dict[str, Any], level: str = 'default') -> bool:
        """检查缓存是否有效"""
        cache = self.get_level(level)
        return cache.is_valid(symbol, timeframe_data)

    def get_all_stats(self) -> Dict[str, Any]:
        """获取所有级别的统计"""
        stats = {}
        for name, cache in self.levels.items():
            stats[name] = cache.get_stats()
        return stats
