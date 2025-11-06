"""
交易模块抽象基类

定义统一的交易接口，支持不同交易模式：
- TestnetTrading (使用 Binance Testnet API)
- DemoTrading (使用 Binance Demo Trading API)
- PaperTrading (纯模拟交易)
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass

from models.trading_decision import TradingDecision


@dataclass
class OrderInfo:
    """订单信息"""

    order_id: str
    symbol: str
    side: str  # 'buy' or 'sell'
    type: str  # 'market' or 'limit'
    amount: float
    price: Optional[float]
    status: str  # 'pending', 'filled', 'cancelled', 'rejected'
    filled_amount: float = 0.0
    filled_price: Optional[float] = None
    timestamp: datetime = None
    fee: float = 0.0
    pnl: float = 0.0

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            'order_id': self.order_id,
            'symbol': self.symbol,
            'side': self.side,
            'type': self.type,
            'amount': self.amount,
            'price': self.price,
            'status': self.status,
            'filled_amount': self.filled_amount,
            'filled_price': self.filled_price,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'fee': self.fee,
            'pnl': self.pnl
        }
        return result


class TradingInterface(ABC):
    """
    交易接口抽象基类

    定义所有交易器必须实现的方法
    """

    @abstractmethod
    def get_account_balance(self) -> Dict[str, float]:
        """
        获取账户余额

        Returns:
            余额字典 {asset: amount}
        """
        pass

    @abstractmethod
    def get_symbol_price(self, symbol: str) -> float:
        """
        获取当前价格

        Args:
            symbol: 交易对

        Returns:
            当前价格
        """
        pass

    @abstractmethod
    def place_market_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        reason: str = ""
    ) -> Dict[str, Any]:
        """
        下市价单

        Args:
            symbol: 交易对
            side: 买卖方向
            amount: 数量
            reason: 原因

        Returns:
            执行结果
        """
        pass

    @abstractmethod
    def place_limit_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        price: float,
        reason: str = ""
    ) -> Dict[str, Any]:
        """
        下限价单

        Args:
            symbol: 交易对
            side: 买卖方向
            amount: 数量
            price: 价格
            reason: 原因

        Returns:
            执行结果
        """
        pass

    @abstractmethod
    def cancel_order(self, symbol: str, order_id: str) -> Dict[str, Any]:
        """
        撤单

        Args:
            symbol: 交易对
            order_id: 订单ID

        Returns:
            执行结果
        """
        pass

    @abstractmethod
    def get_order_status(self, symbol: str, order_id: str) -> Dict[str, Any]:
        """
        获取订单状态

        Args:
            symbol: 交易对
            order_id: 订单ID

        Returns:
            订单状态
        """
        pass

    @abstractmethod
    def get_open_positions(self) -> List[Dict[str, Any]]:
        """
        获取所有持仓

        Returns:
            持仓列表
        """
        pass

    @abstractmethod
    def set_stop_loss(
        self,
        symbol: str,
        side: str,
        amount: float,
        stop_price: float,
        reason: str = ""
    ) -> Dict[str, Any]:
        """
        设置止损单

        Args:
            symbol: 交易对
            side: 持仓方向
            amount: 数量
            stop_price: 触发价格
            reason: 原因

        Returns:
            执行结果
        """
        pass

    @abstractmethod
    def execute_decision(
        self,
        decision: TradingDecision,
        price_override: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        执行交易决策

        Args:
            decision: 交易决策
            price_override: 价格覆盖（用于测试）

        Returns:
            执行结果
        """
        pass

    @abstractmethod
    def get_trades(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取交易记录

        Args:
            limit: 返回条数限制

        Returns:
            交易记录列表
        """
        pass

    @abstractmethod
    def close(self):
        """
        关闭连接/清理资源
        """
        pass

    @property
    @abstractmethod
    def mode_name(self) -> str:
        """
        获取交易模式名称

        Returns:
            模式名称
        """
        pass
