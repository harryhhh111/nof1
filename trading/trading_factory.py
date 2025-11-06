"""
交易工厂模块

根据配置创建不同类型的交易器：
- TestnetTrading
- DemoTrading
- PaperTrading
"""

import logging
from typing import Optional
from trading.base import TradingInterface
from trading.testnet_trader import TestnetTrader
from trading.demo_trader import DemoTrader
from trading.paper_trader_impl import PaperTraderImpl
import config

logger = logging.getLogger(__name__)


class TradingFactory:
    """
    交易器工厂类

    根据配置和模式创建对应的交易器实例
    """

    @staticmethod
    def create_trader(mode: Optional[str] = None) -> TradingInterface:
        """
        创建交易器实例

        Args:
            mode: 交易模式 ('testnet', 'demo', 'paper')
                   如果为 None，则根据 config.CURRENT_MODE 自动选择

        Returns:
            交易器实例

        Raises:
            ValueError: 如果配置不正确或模式不支持
        """
        # 如果未指定模式，使用配置中的当前模式
        if mode is None:
            mode = config.CURRENT_MODE

        logger.info(f"创建交易器 - 模式: {mode.upper()}")

        # 根据模式创建对应的交易器
        if mode == 'testnet':
            return TestnetTrader()
        elif mode == 'demo':
            return DemoTrader()
        elif mode == 'paper':
            return PaperTraderImpl()
        elif mode == 'live':
            # 注意：实盘交易需要特别小心
            logger.warning("⚠️  使用实盘交易模式 - 真实资金风险！")
            # 对于实盘，我们可以复用 TestnetTrader 但使用真实API配置
            return TestnetTrader(use_live=True)
        else:
            raise ValueError(
                f"不支持的交易模式: {mode}。支持的模式: testnet, demo, paper, live"
            )

    @staticmethod
    def get_available_modes() -> list:
        """
        获取可用的交易模式列表

        Returns:
            可用模式列表
        """
        return ['testnet', 'demo', 'paper', 'live']

    @staticmethod
    def is_test_mode(mode: str) -> bool:
        """
        检查是否为测试模式（不使用真实资金）

        Args:
            mode: 交易模式

        Returns:
            如果是测试模式返回 True
        """
        return mode in ['testnet', 'demo', 'paper']
