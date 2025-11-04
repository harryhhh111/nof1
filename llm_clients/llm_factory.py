"""
LLM客户端工厂

统一管理多个LLM客户端，支持创建和调用不同模型
"""

import os
from typing import Dict, Optional, Any, Union
from datetime import datetime

from .deepseek_client import DeepSeekClient
from .qwen_client import QwenClient


class LLMClientFactory:
    """LLM客户端工厂"""

    # 模型配置
    MODEL_CONFIG = {
        'deepseek': {
            'client_class': DeepSeekClient,
            'model_name': 'deepseek-chat',
            'cost_per_token': 0.0002,
            'capabilities': ['trading', 'analysis', 'reasoning'],
            'default_params': {
                'temperature': 0.3,
                'max_tokens': 1500
            }
        },
        'qwen': {
            'client_class': QwenClient,
            'model_name': 'qwen-turbo',
            'cost_per_token': 0.0004,
            'capabilities': ['trading', 'analysis', 'creative'],
            'default_params': {
                'temperature': 0.3,
                'max_tokens': 1500
            }
        }
    }

    def __init__(self, api_keys: Dict[str, str], base_urls: Optional[Dict[str, str]] = None):
        """
        初始化LLM工厂

        Args:
            api_keys: API密钥字典，如 {'deepseek': 'xxx', 'qwen': 'xxx'}
            base_urls: 基础URL字典（可选）
        """
        self.api_keys = api_keys
        self.base_urls = base_urls or {}
        self.clients = {}  # 缓存客户端实例
        self._init_clients()

    def _init_clients(self):
        """初始化所有客户端"""
        for model_name, config in self.MODEL_CONFIG.items():
            if model_name in self.api_keys:
                base_url = self.base_urls.get(model_name)
                client = config['client_class'](
                    api_key=self.api_keys[model_name],
                    base_url=base_url
                )
                self.clients[model_name] = client

    def get_client(self, model_name: str) -> Optional[Union[DeepSeekClient, QwenClient]]:
        """
        获取指定模型的客户端

        Args:
            model_name: 模型名称

        Returns:
            客户端实例或None
        """
        return self.clients.get(model_name)

    def list_available_models(self) -> list:
        """获取可用模型列表"""
        return list(self.clients.keys())

    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """获取模型信息"""
        if model_name in self.MODEL_CONFIG:
            config = self.MODEL_CONFIG[model_name].copy()
            config['available'] = model_name in self.clients
            return config
        return None

    def call_model(
        self,
        model_name: str,
        prompt: str,
        **kwargs
    ) -> tuple:
        """
        调用指定模型

        Args:
            model_name: 模型名称
            prompt: 提示词
            **kwargs: 其他参数（temperature, max_tokens等）

        Returns:
            tuple: (决策, 元数据)
        """
        client = self.get_client(model_name)
        if not client:
            raise ValueError(f"模型 {model_name} 不可用或未配置")

        # 合并默认参数和自定义参数
        params = self.MODEL_CONFIG[model_name]['default_params'].copy()
        params.update(kwargs)

        return client.get_decision(prompt, **params)

    def parallel_call(
        self,
        prompts: Dict[str, str],
        **kwargs
    ) -> Dict[str, tuple]:
        """
        并行调用多个模型

        Args:
            prompts: {model_name: prompt} 字典
            **kwargs: 其他参数

        Returns:
            {model_name: (decision, metadata)} 字典
        """
        results = {}

        # 简化版本：顺序调用（可改为真正的异步）
        for model_name, prompt in prompts.items():
            try:
                results[model_name] = self.call_model(model_name, prompt, **kwargs)
            except Exception as e:
                print(f"调用模型 {model_name} 失败: {e}")
                results[model_name] = (None, str(e))

        return results

    def get_cost_estimate(
        self,
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> float:
        """
        计算模型调用成本

        Args:
            model_name: 模型名称
            prompt_tokens: 提示Token数
            completion_tokens: 回复Token数

        Returns:
            估算成本（美元）
        """
        config = self.MODEL_CONFIG.get(model_name)
        if not config:
            return 0.0

        # 简化估算（可根据实际API使用量调整）
        cost_per_token = config.get('cost_per_token', 0)
        return (prompt_tokens + completion_tokens) * cost_per_token

    def test_all_clients(self) -> Dict[str, bool]:
        """
        测试所有客户端连接

        Returns:
            {model_name: 是否成功}
        """
        results = {}
        for model_name, client in self.clients.items():
            results[model_name] = client.test_connection()
        return results

    def get_usage_stats(self) -> Dict[str, Any]:
        """获取使用统计（未来扩展）"""
        return {
            'available_models': self.list_available_models(),
            'total_models': len(self.MODEL_CONFIG),
            'initialized_models': len(self.clients)
        }

    def close_all(self):
        """关闭所有客户端"""
        for client in self.clients.values():
            client.close()
        self.clients.clear()


# 全局工厂实例（单例）
_global_factory = None

def get_llm_factory(api_keys: Optional[Dict[str, str]] = None) -> LLMClientFactory:
    """
    获取全局LLM工厂实例

    Args:
        api_keys: API密钥（首次调用时必需）

    Returns:
        工厂实例
    """
    global _global_factory
    if _global_factory is None:
        if api_keys is None:
            raise ValueError("首次调用需要提供API密钥")
        _global_factory = LLMClientFactory(api_keys)
    return _global_factory


def create_llm_factory_from_env() -> LLMClientFactory:
    """
    从环境变量创建LLM工厂

    期望的环境变量：
    - DEEPSEEK_API_KEY
    - QWEN_API_KEY
    - DEEPSEEK_BASE_URL (可选)
    - QWEN_BASE_URL (可选)

    Returns:
        工厂实例
    """
    api_keys = {}
    base_urls = {}

    # DeepSeek
    deepseek_key = os.getenv('DEEPSEEK_API_KEY')
    if deepseek_key:
        api_keys['deepseek'] = deepseek_key
        base_url = os.getenv('DEEPSEEK_BASE_URL')
        if base_url:
            base_urls['deepseek'] = base_url

    # Qwen
    qwen_key = os.getenv('QWEN_API_KEY')
    if qwen_key:
        api_keys['qwen'] = qwen_key
        base_url = os.getenv('QWEN_BASE_URL')
        if base_url:
            base_urls['qwen'] = base_url

    if not api_keys:
        raise ValueError("未找到任何API密钥，请设置环境变量")

    return LLMClientFactory(api_keys, base_urls)


if __name__ == '__main__':
    # 测试代码
    print("LLM客户端工厂模块")
    print("=" * 50)

    print("\n支持模型:")
    for name, config in LLMClientFactory.MODEL_CONFIG.items():
        print(f"- {name}: {config['model_name']}")
        print(f"  成本: ${config['cost_per_token']}/token")
        print(f"  能力: {', '.join(config['capabilities'])}")

    print("\n环境变量示例:")
    print("export DEEPSEEK_API_KEY='your-key'")
    print("export QWEN_API_KEY='your-key'")
