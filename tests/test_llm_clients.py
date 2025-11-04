"""
LLM客户端测试

测试DeepSeek和Qwen客户端的功能
"""

import unittest
import json
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.trading_decision import TradingDecision, DecisionMetadata
from llm_clients.deepseek_client import DeepSeekClient
from llm_clients.qwen_client import QwenClient
from llm_clients.llm_factory import LLMClientFactory


class TestTradingDecision(unittest.TestCase):
    """交易决策模型测试"""

    def test_decision_creation(self):
        """测试决策创建"""
        decision = TradingDecision(
            action="BUY",
            confidence=80,
            reasoning="测试决策",
            entry_price=50000,
            stop_loss=49000,
            take_profit=52000,
            position_size=10,
            risk_level="MEDIUM",
            risk_score=50,
            model_source="test",
            timeframe="4h"
        )

        self.assertEqual(decision.action, "BUY")
        self.assertEqual(decision.confidence, 80)
        self.assertEqual(decision.entry_price, 50000)

    def test_decision_validation_valid(self):
        """测试有效决策验证"""
        decision = TradingDecision(
            action="BUY",
            confidence=75,
            reasoning="测试",
            entry_price=50000,
            stop_loss=49000,
            take_profit=52000,
            position_size=10,
            risk_level="MEDIUM",
            risk_score=50,
            model_source="test",
            timeframe="4h"
        )

        is_valid, msg = decision.validate_decision()
        self.assertTrue(is_valid)
        self.assertEqual(msg, "决策有效")

    def test_decision_validation_invalid_confidence(self):
        """测试无效置信度"""
        decision = TradingDecision(
            action="BUY",
            confidence=150,  # 无效
            reasoning="测试",
            entry_price=50000,
            stop_loss=49000,
            take_profit=52000,
            position_size=10,
            risk_level="MEDIUM",
            risk_score=50,
            model_source="test",
            timeframe="4h"
        )

        is_valid, msg = decision.validate_decision()
        self.assertFalse(is_valid)
        self.assertIn("置信度无效", msg)

    def test_risk_reward_ratio(self):
        """测试风险回报比计算"""
        decision = TradingDecision(
            action="BUY",
            confidence=75,
            reasoning="测试",
            entry_price=50000,
            stop_loss=49000,
            take_profit=52000,
            position_size=10,
            risk_level="MEDIUM",
            risk_score=50,
            model_source="test",
            timeframe="4h"
        )

        ratio = decision.get_risk_reward_ratio()
        self.assertIsNotNone(ratio)
        self.assertAlmostEqual(ratio, 2.0, places=2)  # (52000-50000) / (50000-49000) = 2

    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            "action": "SELL",
            "confidence": 60,
            "reasoning": "测试",
            "position_size": 5,
            "risk_level": "LOW",
            "risk_score": 30,
            "model_source": "test",
            "timeframe": "3m"
        }

        decision = TradingDecision.from_dict(data)
        self.assertEqual(decision.action, "SELL")
        self.assertEqual(decision.confidence, 60)


class TestDeepSeekClient(unittest.TestCase):
    """DeepSeek客户端测试"""

    def setUp(self):
        """测试前准备"""
        self.client = DeepSeekClient("test-key")

    def tearDown(self):
        """测试后清理"""
        self.client.close()

    @patch('requests.Session')
    def test_get_decision_success(self, mock_session):
        """测试获取决策成功"""
        # 模拟响应
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': json.dumps({
                        'action': 'BUY',
                        'confidence': 80,
                        'reasoning': '测试决策',
                        'entry_price': 50000,
                        'stop_loss': 49000,
                        'take_profit': 52000,
                        'position_size': 10,
                        'risk_level': 'MEDIUM',
                        'risk_score': 50,
                        'timeframe': '4h'
                    })
                }
            }],
            'usage': {
                'prompt_tokens': 100,
                'completion_tokens': 50,
                'total_tokens': 150
            }
        }
        mock_response.raise_for_status = Mock()

        mock_session.return_value.post.return_value = mock_response

        decision, metadata = self.client.get_decision("测试提示")

        self.assertIsInstance(decision, TradingDecision)
        self.assertEqual(decision.action, "BUY")
        self.assertEqual(decision.confidence, 80)
        self.assertEqual(decision.model_source, "deepseek")
        self.assertIsInstance(metadata, DecisionMetadata)

    @patch('requests.Session')
    def test_extract_json_valid(self, mock_session):
        """测试JSON提取-有效JSON"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{'message': {'content': '{"action": "BUY", "confidence": 80, "reasoning": "test", "position_size": 10, "risk_level": "MEDIUM", "risk_score": 50, "timeframe": "4h"}'}}],
            'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15}
        }
        mock_response.raise_for_status = Mock()
        mock_session.return_value.post.return_value = mock_response

        decision, _ = self.client.get_decision("测试")
        self.assertEqual(decision.action, "BUY")

    @patch('requests.Session')
    def test_extract_json_code_block(self, mock_session):
        """测试JSON提取-代码块"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': '```json\n{"action": "SELL", "confidence": 70, "reasoning": "test", "position_size": 10, "risk_level": "MEDIUM", "risk_score": 50, "timeframe": "4h"}\n```'
                }
            }],
            'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15}
        }
        mock_response.raise_for_status = Mock()
        mock_session.return_value.post.return_value = mock_response

        decision, _ = self.client.get_decision("测试")
        self.assertEqual(decision.action, "SELL")

    @patch('requests.Session')
    def test_extract_json_fallback(self, mock_session):
        """测试JSON提取-回退"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': '无效的JSON内容'
                }
            }],
            'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15}
        }
        mock_response.raise_for_status = Mock()
        mock_session.return_value.post.return_value = mock_response

        decision, _ = self.client.get_decision("测试")
        self.assertEqual(decision.action, "HOLD")  # 默认决策
        self.assertIn("无法解析", decision.reasoning)

    def test_calculate_cost(self):
        """测试成本计算"""
        cost = self.client._calculate_cost(100, 50)
        self.assertGreater(cost, 0)

    def test_get_cost_estimate(self):
        """测试成本估算"""
        cost = self.client._calculate_cost(1000, 500)
        self.assertAlmostEqual(cost, 1000 * 0.0001 + 500 * 0.0003, places=6)


class TestQwenClient(unittest.TestCase):
    """Qwen客户端测试"""

    def setUp(self):
        """测试前准备"""
        self.client = QwenClient("test-key")

    def tearDown(self):
        """测试后清理"""
        self.client.close()

    @patch('requests.Session')
    def test_get_decision_success(self, mock_session):
        """测试获取决策成功"""
        # 模拟响应
        mock_response = Mock()
        mock_response.json.return_value = {
            'output': {
                'text': json.dumps({
                    'action': 'SELL',
                    'confidence': 70,
                    'reasoning': '测试决策',
                    'entry_price': 50000,
                    'stop_loss': 51000,
                    'take_profit': 48000,
                    'position_size': 15,
                    'risk_level': 'HIGH',
                    'risk_score': 70,
                    'timeframe': '3m'
                })
            },
            'usage': {
                'input_tokens': 100,
                'output_tokens': 50
            }
        }
        mock_response.raise_for_status = Mock()

        mock_session.return_value.post.return_value = mock_response

        decision, metadata = self.client.get_decision("测试提示")

        self.assertIsInstance(decision, TradingDecision)
        self.assertEqual(decision.action, "SELL")
        self.assertEqual(decision.model_source, "qwen")
        self.assertIsInstance(metadata, DecisionMetadata)


class TestLLMClientFactory(unittest.TestCase):
    """LLM客户端工厂测试"""

    def test_factory_creation(self):
        """测试工厂创建"""
        api_keys = {
            'deepseek': 'test-key-1',
            'qwen': 'test-key-2'
        }
        factory = LLMClientFactory(api_keys)

        self.assertIn('deepseek', factory.clients)
        self.assertIn('qwen', factory.clients)

    def test_get_client(self):
        """测试获取客户端"""
        api_keys = {'deepseek': 'test-key'}
        factory = LLMClientFactory(api_keys)

        client = factory.get_client('deepseek')
        self.assertIsNotNone(client)

        client = factory.get_client('nonexistent')
        self.assertIsNone(client)

    def test_list_available_models(self):
        """测试列出可用模型"""
        api_keys = {'deepseek': 'test-key'}
        factory = LLMClientFactory(api_keys)

        models = factory.list_available_models()
        self.assertIn('deepseek', models)

    def test_get_model_info(self):
        """测试获取模型信息"""
        api_keys = {'deepseek': 'test-key'}
        factory = LLMClientFactory(api_keys)

        info = factory.get_model_info('deepseek')
        self.assertIsNotNone(info)
        self.assertIn('model_name', info)
        self.assertIn('cost_per_token', info)
        self.assertTrue(info['available'])

    def test_call_model(self):
        """测试调用模型"""
        api_keys = {'deepseek': 'test-key'}
        factory = LLMClientFactory(api_keys)

        # 由于没有真实API，这里只测试参数传递
        # 实际调用会失败，但可以验证参数处理
        try:
            factory.call_model('deepseek', '测试提示', temperature=0.5)
        except Exception as e:
            # 预期会有连接错误
            self.assertIsInstance(e, (ConnectionError, ValueError))

    def test_parallel_call(self):
        """测试并行调用"""
        api_keys = {'deepseek': 'test-key'}
        factory = LLMClientFactory(api_keys)

        prompts = {'deepseek': '测试提示'}
        results = factory.parallel_call(prompts)

        self.assertIn('deepseek', results)

    def test_cost_estimate(self):
        """测试成本估算"""
        api_keys = {'deepseek': 'test-key'}
        factory = LLMClientFactory(api_keys)

        cost = factory.get_cost_estimate('deepseek', 100, 50)
        self.assertGreaterEqual(cost, 0)

    def test_test_all_clients(self):
        """测试所有客户端连接"""
        api_keys = {'deepseek': 'test-key'}
        factory = LLMClientFactory(api_keys)

        results = factory.test_all_clients()
        self.assertIn('deepseek', results)
        # 由于使用假密钥，连接会失败
        self.assertFalse(results['deepseek'])

    def test_close_all(self):
        """测试关闭所有客户端"""
        api_keys = {'deepseek': 'test-key'}
        factory = LLMClientFactory(api_keys)

        factory.close_all()
        self.assertEqual(len(factory.clients), 0)


class TestDecisionMetadata(unittest.TestCase):
    """决策元数据测试"""

    def test_metadata_creation(self):
        """测试元数据创建"""
        metadata = DecisionMetadata(
            request_id="test-001",
            model_name="test-model",
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            processing_time=1.5,
            cost=0.05
        )

        self.assertEqual(metadata.request_id, "test-001")
        self.assertEqual(metadata.total_tokens, 150)
        self.assertAlmostEqual(metadata.processing_time, 1.5, places=1)


if __name__ == '__main__':
    unittest.main()
