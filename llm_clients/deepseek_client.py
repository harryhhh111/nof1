"""
DeepSeek API客户端

支持调用 DeepSeek API 获取交易决策
"""

import json
import time
from typing import Dict, Optional, Any
import requests
from datetime import datetime

from models.trading_decision import TradingDecision, DecisionMetadata


class DeepSeekClient:
    """DeepSeek API客户端"""

    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com/v1"):
        """
        初始化DeepSeek客户端

        Args:
            api_key: DeepSeek API密钥
            base_url: API基础URL
        """
        self.api_key = api_key
        self.base_url = base_url

    def get_decision(
        self,
        prompt: str,
        model: str = "deepseek-chat",
        temperature: float = 0.3,
        max_tokens: int = 1500,
        timeout: int = 30
    ) -> tuple[TradingDecision, DecisionMetadata]:
        """
        调用DeepSeek API获取交易决策

        Args:
            prompt: 提示词
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大Token数
            timeout: 超时时间（秒）

        Returns:
            tuple: (决策, 元数据)
        """
        start_time = time.time()

        try:
            # 构建请求
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }

            # 创建临时session
            session = requests.Session()
            session.headers.update({
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            })

            # 发送请求
            response = session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=timeout
            )
            response.raise_for_status()
            session.close()

            # 解析响应
            response_data = response.json()
            content = response_data['choices'][0]['message']['content']

            # 提取JSON
            decision_dict = self._extract_json(content)

            # 创建决策对象
            decision = TradingDecision.from_dict(decision_dict)
            decision.model_source = "deepseek"

            # 计算元数据
            processing_time = time.time() - start_time
            usage = response_data.get('usage', {})
            prompt_tokens = usage.get('prompt_tokens', 0)
            completion_tokens = usage.get('completion_tokens', 0)
            total_tokens = usage.get('total_tokens', 0)

            metadata = DecisionMetadata(
                request_id=f"deepseek_{int(time.time())}",
                model_name=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                processing_time=processing_time,
                cost=self._calculate_cost(prompt_tokens, completion_tokens)
            )

            return decision, metadata

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"DeepSeek API请求失败: {e}")
        except (KeyError, json.JSONDecodeError) as e:
            raise ValueError(f"DeepSeek响应解析失败: {e}")
        except Exception as e:
            raise RuntimeError(f"DeepSeek调用异常: {e}")

    def _extract_json(self, content: str) -> Dict[str, Any]:
        """
        从响应内容中提取JSON

        Args:
            content: 响应内容

        Returns:
            解析后的JSON字典
        """
        # 尝试直接解析
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # 尝试从代码块中提取
        if '```' in content:
            for block in content.split('```'):
                if block.strip().startswith('json'):
                    json_str = block.strip()[4:].strip()
                    try:
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        continue

        # 尝试提取花括号包裹的内容
        start = content.find('{')
        end = content.rfind('}') + 1
        if start >= 0 and end > start:
            json_str = content[start:end]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

        # 如果都无法解析，尝试修复常见问题
        try:
            # 修复单引号问题
            content_fixed = content.replace("'", '"')
            return json.loads(content_fixed)
        except json.JSONDecodeError:
            pass

        # 尝试提取可能的键值对
        decision = {
            "action": "HOLD",
            "confidence": 50,
            "reasoning": f"无法解析LLM响应: {content[:100]}",
            "entry_price": None,
            "stop_loss": None,
            "take_profit": None,
            "position_size": 0,
            "risk_level": "MEDIUM",
            "risk_score": 50,
            "timeframe": "unknown"
        }
        return decision

    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        计算调用成本

        Args:
            prompt_tokens: 提示Token数
            completion_tokens: 回复Token数

        Returns:
            成本（美元）
        """
        # DeepSeek定价（示例价格，实际请参考官网）
        input_cost_per_token = 0.0001  # $0.0001 / token
        output_cost_per_token = 0.0003  # $0.0003 / token

        return prompt_tokens * input_cost_per_token + completion_tokens * output_cost_per_token

    async def get_decision_async(
        self,
        prompt: str,
        model: str = "deepseek-chat",
        temperature: float = 0.3,
        max_tokens: int = 1500,
        timeout: int = 30
    ) -> tuple[TradingDecision, DecisionMetadata]:
        """
        异步调用DeepSeek API（未来扩展）

        Args:
            prompt: 提示词
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大Token数
            timeout: 超时时间（秒）

        Returns:
            tuple: (决策, 元数据)
        """
        # 这里使用同步实现，未来可以改为异步
        return self.get_decision(prompt, model, temperature, max_tokens, timeout)

    def test_connection(self) -> bool:
        """
        测试API连接

        Returns:
            连接是否成功
        """
        try:
            test_prompt = "请回答：1+1=?"
            decision, _ = self.get_decision(test_prompt, max_tokens=10)
            return True
        except Exception:
            return False

    def close(self):
        """关闭会话"""
        pass  # 不再使用session


class DeepSeekError(Exception):
    """DeepSeek API异常"""
    pass
