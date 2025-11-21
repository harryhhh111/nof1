"""
Hyperliquid交易器测试

测试Hyperliquid集成功能，包括：
- Agent Wallet认证
- 交易功能
- 持仓查询
- 安全配置
"""

import unittest
import os
from unittest.mock import patch, MagicMock
import sys
sys.path.append('..')

from trading.hyperliquid_trader import HyperliquidTrader


class TestHyperliquidTrader(unittest.TestCase):
    """Hyperliquid交易器测试类"""

    def setUp(self):
        """测试前准备"""
        # 设置测试环境变量
        os.environ['HYPERLIQUID_PRIVATE_KEY'] = '0x1234567890abcdef' * 4  # 64字符测试私钥
        os.environ['HYPERLIQUID_WALLET_ADDRESS'] = '0x1234567890abcdef' * 2 + '12345678'  # 42字符地址

    def test_missing_private_key(self):
        """测试缺少私钥的情况"""
        os.environ['HYPERLIQUID_PRIVATE_KEY'] = ''
        with self.assertRaises(ValueError) as context:
            HyperliquidTrader()
        self.assertIn("Agent钱包私钥", str(context.exception))

    def test_missing_wallet_address(self):
        """测试缺少钱包地址的情况"""
        os.environ['HYPERLIQUID_WALLET_ADDRESS'] = ''
        with self.assertRaises(ValueError) as context:
            HyperliquidTrader()
        self.assertIn("主钱包地址", str(context.exception))

    def test_invalid_wallet_address_format(self):
        """测试钱包地址格式错误"""
        os.environ['HYPERLIQUID_WALLET_ADDRESS'] = 'invalid_address'
        with self.assertRaises(ValueError) as context:
            HyperliquidTrader()
        self.assertIn("地址格式错误", str(context.exception))

    @patch('trading.hyperliquid_trader.hyperliquid')
    def test_initialization_success(self, mock_hyperliquid):
        """测试成功初始化"""
        # Mock Hyperliquid SDK
        mock_exchange = MagicMock()
        mock_info = MagicMock()
        mock_hyperliquid.Exchange.return_value = mock_exchange
        mock_hyperliquid.Info.return_value = mock_info

        # Mock account
        with patch('trading.hyperliquid_trader.Account') as mock_account:
            mock_account_instance = MagicMock()
            mock_account_instance.address = '0x1234567890abcdef' * 2 + '12345678'
            mock_account.from_key.return_value = mock_account_instance

            trader = HyperliquidTrader(use_testnet=True)

            # 验证初始化
            self.assertEqual(trader.agent_private_key, '0x1234567890abcdef' * 4)
            self.assertEqual(trader.main_wallet_address, '0x1234567890abcdef' * 2 + '12345678')
            self.assertTrue(trader.use_testnet)

    @patch('trading.hyperliquid_trader.hyperliquid')
    def test_symbol_conversion(self, mock_hyperliquid):
        """测试symbol转换功能"""
        # Mock Hyperliquid SDK
        mock_exchange = MagicMock()
        mock_info = MagicMock()
        mock_hyperliquid.Exchange.return_value = mock_exchange
        mock_hyperliquid.Info.return_value = mock_info

        with patch('trading.hyperliquid_trader.Account') as mock_account:
            mock_account_instance = MagicMock()
            mock_account_instance.address = '0x1234567890abcdef' * 2 + '12345678'
            mock_account.from_key.return_value = mock_account_instance

            trader = HyperliquidTrader(use_testnet=True)

            # 测试symbol转换
            self.assertEqual(trader._convert_symbol_to_hyperliquid('BTCUSDT'), 'BTC')
            self.assertEqual(trader._convert_symbol_to_hyperliquid('ETHUSDT'), 'ETH')
            self.assertEqual(trader._convert_symbol_from_hyperliquid('BTC'), 'BTCUSDT')
            self.assertEqual(trader._convert_symbol_from_hyperliquid('ETH'), 'ETHUSDT')

    @patch('trading.hyperliquid_trader.hyperliquid')
    def test_mode_name_property(self, mock_hyperliquid):
        """测试模式名称属性"""
        # Mock Hyperliquid SDK
        mock_exchange = MagicMock()
        mock_info = MagicMock()
        mock_hyperliquid.Exchange.return_value = mock_exchange
        mock_hyperliquid.Info.return_value = mock_info

        with patch('trading.hyperliquid_trader.Account') as mock_account:
            mock_account_instance = MagicMock()
            mock_account_instance.address = '0x1234567890abcdef' * 2 + '12345678'
            mock_account.from_key.return_value = mock_account_instance

            # 测试测试网模式
            trader_testnet = HyperliquidTrader(use_testnet=True)
            self.assertEqual(trader_testnet.mode_name, 'Hyperliquid Testnet')

            # 测试主网模式
            trader_mainnet = HyperliquidTrader(use_testnet=False)
            self.assertEqual(trader_mainnet.mode_name, 'Hyperliquid Mainnet')

    @patch('trading.hyperliquid_trader.hyperliquid')
    def test_rounding_functions(self, mock_hyperliquid):
        """测试精度处理函数"""
        # Mock Hyperliquid SDK
        mock_exchange = MagicMock()
        mock_info = MagicMock()
        mock_hyperliquid.Exchange.return_value = mock_exchange

        # Mock meta with szDecimals
        mock_info.meta.return_value = {
            'universe': [
                {'name': 'BTC', 'szDecimals': 3},
                {'name': 'ETH', 'szDecimals': 4}
            ]
        }
        mock_hyperliquid.Info.return_value = mock_info

        with patch('trading.hyperliquid_trader.Account') as mock_account:
            mock_account_instance = MagicMock()
            mock_account_instance.address = '0x1234567890abcdef' * 2 + '12345678'
            mock_account.from_key.return_value = mock_account_instance

            trader = HyperliquidTrader(use_testnet=True)

            # 测试数量精度处理
            self.assertEqual(trader._round_to_sz_decimals('BTC', 0.123456), 0.123)  # 3位小数
            self.assertEqual(trader._round_to_sz_decimals('ETH', 0.123456), 0.1235)  # 4位小数

            # 测试价格精度处理
            self.assertEqual(trader._round_price_to_sigfigs(1234.56789, 5), 1234.6)
            self.assertEqual(trader._round_price_to_sigfigs(0.00123456, 5), 0.0012346)


class TestHyperliquidIntegration(unittest.TestCase):
    """Hyperliquid集成测试（需要真实API密钥）"""

    @unittest.skip("需要真实的Hyperliquid API密钥")
    def test_real_connection(self):
        """测试真实连接（需要设置环境变量）"""
        # 这个测试需要真实的API密钥，默认跳过
        # 在CI/CD环境中可以通过环境变量启用
        pass

    @unittest.skip("需要真实的Hyperliquid API密钥")
    def test_real_trading_functions(self):
        """测试真实交易功能（需要真实API密钥和测试网环境）"""
        # 这个测试需要真实的API密钥，默认跳过
        # 仅在测试网环境中运行，避免真实资金风险
        pass


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)