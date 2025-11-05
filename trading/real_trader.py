"""
真实交易执行器

使用Binance Testnet或真实交易所API进行交易
支持市价单、限价单、止损止盈等
"""

import ccxt
import json
import sqlite3
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import logging
from pathlib import Path

from models.trading_decision import TradingDecision

logger = logging.getLogger(__name__)


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
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class RealTrader:
    """
    真实交易执行器

    支持：
    - Binance Testnet
    - 真实交易所API
    - 市价单/限价单
    - 止损止盈
    - 订单管理
    - 持仓追踪
    """

    def __init__(
        self,
        database_path: Optional[str] = None,
        fee_rate: float = 0.001,  # 0.1% 手续费
        use_futures: bool = False  # 是否使用期货交易
    ):
        """
        初始化真实交易执行器

        Args:
            database_path: 数据库路径
            fee_rate: 手续费率
            use_futures: 是否使用期货交易（否则使用现货）
        """
        import config

        self.fee_rate = fee_rate
        self.use_testnet = config.USE_TESTNET
        self.use_futures = use_futures
        self.database_path = database_path or "real_trading.db"
        self.positions: Dict[str, Dict] = {}
        self.orders: List[OrderInfo] = []

        # 选择合适的交易所配置
        if use_futures:
            self.exchange = ccxt.binance({
                **config.FUTURES_CONFIG,
                'type': 'future'  # 期货交易
            })
            mode_name = f"{config.CURRENT_MODE.upper()} (Futures)"
        else:
            self.exchange = ccxt.binance({
                **config.EXCHANGE_CONFIG,
                'type': 'spot'  # 现货交易
            })
            mode_name = f"{config.CURRENT_MODE.upper()} (Spot)"

        # 验证API Key
        if not config.BINANCE_API_KEY or not config.BINANCE_SECRET_KEY:
            error_msg = f"未配置API Key！请检查config.py中的配置"
            logger.error(error_msg)
            if config.DEMO_API_KEY:
                error_msg += f"\n发现 Demo API Key: {config.DEMO_API_KEY[:20]}..."
            raise ValueError(error_msg)

        self._init_database()
        logger.info(f"交易执行器已初始化 - 模式: {mode_name}")
        logger.info(f"Base URL: {config.BINANCE_BASE_URL}")

    def _init_database(self):
        """初始化数据库"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()

            # 创建订单表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    order_id TEXT PRIMARY KEY,
                    symbol TEXT,
                    side TEXT,
                    type TEXT,
                    amount REAL,
                    price REAL,
                    status TEXT,
                    filled_amount REAL,
                    filled_price REAL,
                    timestamp TEXT,
                    fee REAL,
                    pnl REAL
                )
            ''')

            # 创建持仓表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS positions (
                    symbol TEXT PRIMARY KEY,
                    side TEXT,
                    size REAL,
                    entry_price REAL,
                    entry_time TEXT,
                    current_price REAL,
                    unrealized_pnl REAL,
                    realized_pnl REAL,
                    stop_loss REAL,
                    take_profit REAL
                )
            ''')

            # 创建余额表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS balances (
                    asset TEXT PRIMARY KEY,
                    free REAL,
                    locked REAL,
                    total REAL
                )
            ''')

            conn.commit()
            conn.close()
            logger.info("数据库初始化成功")
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise

    def get_account_balance(self) -> Dict[str, float]:
        """
        获取账户余额

        Returns:
            余额字典 {asset: amount}
        """
        try:
            balance = self.exchange.fetch_balance()
            # 只返回可用余额
            result = {}
            for asset, amount in balance['total'].items():
                if amount > 0:
                    result[asset] = amount
            logger.info(f"获取余额: {result}")
            self._save_balances(result)
            return result
        except Exception as e:
            logger.error(f"获取余额失败: {e}")
            return {}

    def get_symbol_price(self, symbol: str) -> float:
        """
        获取当前价格

        Args:
            symbol: 交易对

        Returns:
            当前价格
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            price = ticker['last']
            logger.debug(f"{symbol} 当前价格: {price}")
            return price
        except Exception as e:
            logger.error(f"获取 {symbol} 价格失败: {e}")
            raise

    def place_market_order(
        self,
        symbol: str,
        side: str,  # 'buy' or 'sell'
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
        try:
            order = self.exchange.create_market_order(symbol, side, amount)

            # 创建订单信息
            order_info = OrderInfo(
                order_id=str(order['id']),
                symbol=symbol,
                side=side,
                type='market',
                amount=amount,
                price=order.get('price'),
                status=order['status'],
                filled_amount=order.get('filled', 0),
                filled_price=order.get('average'),
                fee=order.get('fee', {}).get('cost', 0)
            )
            self.orders.append(order_info)
            self._save_order(order_info)

            # 更新持仓
            self._update_position_from_order(order_info)

            logger.info(f"市价单执行成功: {symbol} {side} {amount}")
            return {
                "status": "success",
                "order_id": order_info.order_id,
                "symbol": symbol,
                "side": side,
                "amount": amount,
                "price": order_info.filled_price,
                "fee": order_info.fee,
                "message": reason
            }

        except Exception as e:
            logger.error(f"下市价单失败: {e}")
            return {
                "status": "error",
                "message": str(e),
                "symbol": symbol,
                "side": side,
                "amount": amount
            }

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
        try:
            order = self.exchange.create_limit_order(symbol, side, amount, price)

            order_info = OrderInfo(
                order_id=str(order['id']),
                symbol=symbol,
                side=side,
                type='limit',
                amount=amount,
                price=price,
                status=order['status']
            )
            self.orders.append(order_info)
            self._save_order(order_info)

            logger.info(f"限价单提交成功: {symbol} {side} {amount} @ {price}")
            return {
                "status": "success",
                "order_id": order_info.order_id,
                "symbol": symbol,
                "side": side,
                "amount": amount,
                "price": price,
                "message": reason
            }

        except Exception as e:
            logger.error(f"下限价单失败: {e}")
            return {
                "status": "error",
                "message": str(e),
                "symbol": symbol,
                "side": side,
                "amount": amount,
                "price": price
            }

    def cancel_order(self, symbol: str, order_id: str) -> Dict[str, Any]:
        """
        撤单

        Args:
            symbol: 交易对
            order_id: 订单ID

        Returns:
            执行结果
        """
        try:
            self.exchange.cancel_order(order_id, symbol)
            logger.info(f"撤单成功: {symbol} {order_id}")
            return {"status": "success", "message": "撤单成功"}
        except Exception as e:
            logger.error(f"撤单失败: {e}")
            return {"status": "error", "message": str(e)}

    def get_order_status(self, symbol: str, order_id: str) -> Dict[str, Any]:
        """
        获取订单状态

        Args:
            symbol: 交易对
            order_id: 订单ID

        Returns:
            订单状态
        """
        try:
            order = self.exchange.fetch_order(order_id, symbol)
            return {
                "status": "success",
                "order": order
            }
        except Exception as e:
            logger.error(f"查询订单失败: {e}")
            return {"status": "error", "message": str(e)}

    def get_open_positions(self) -> List[Dict[str, Any]]:
        """
        获取所有持仓

        Returns:
            持仓列表
        """
        try:
            # 注意: Demo Trading 期货持仓查询可能不可用
            # 使用现货余额作为持仓信息
            if self.use_futures:
                # 期货模式：尝试获取持仓，如果失败则返回空
                try:
                    positions = self.exchange.fetch_positions()
                    # 过滤非零持仓
                    open_positions = [p for p in positions if abs(float(p['contracts'])) > 0]
                    return open_positions
                except Exception as e:
                    logger.warning(f"期货持仓查询不可用: {e}")
                    logger.info("   (Demo Trading 可能不支持期货持仓查询)")
                    return []
            else:
                # 现货模式：获取现货余额
                balance = self.get_account_balance()
                positions = []
                for asset, amount in balance.items():
                    if asset not in ['USDT', 'USDC', 'BUSD'] and amount > 0:
                        positions.append({
                            'symbol': asset + 'USDT',
                            'contracts': amount,
                            'side': 'long',
                            'entryPrice': 0,
                            'margin': 0,
                            'percentage': 0
                        })
                return positions
        except Exception as e:
            logger.error(f"获取持仓失败: {e}")
            return []

    def set_stop_loss(
        self,
        symbol: str,
        side: str,  # 'long' or 'short'
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
        try:
            # 止损限价单
            # Buy stop-limit: 价格上涨到stop_price后，以limit_price买入
            # Sell stop-limit: 价格下跌到stop_price后，以limit_price卖出

            if side.lower() == 'long':
                # 多头止损：价格下跌到stop_price时触发
                limit_price = stop_price * 0.995  # 略低于触发价
            else:
                # 空头止损：价格上涨到stop_price时触发
                limit_price = stop_price * 1.005  # 略高于触发价

            order = self.exchange.create_order(
                symbol=symbol,
                type='stop',
                side='sell' if side.lower() == 'long' else 'buy',
                amount=amount,
                price=stop_price,
                params={'stopPrice': stop_price}
            )

            logger.info(f"止损单设置成功: {symbol} {side} {amount} @ {stop_price}")
            return {
                "status": "success",
                "order_id": order['id'],
                "symbol": symbol,
                "side": side,
                "amount": amount,
                "stop_price": stop_price,
                "limit_price": limit_price,
                "message": reason
            }

        except Exception as e:
            logger.error(f"设置止损失败: {e}")
            return {"status": "error", "message": str(e)}

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
        if not decision.symbol:
            return {"status": "error", "message": "缺少交易对符号"}

        # 验证决策
        is_valid, msg = decision.validate_decision()
        if not is_valid:
            return {"status": "error", "message": f"决策无效: {msg}"}

        try:
            # 获取当前价格
            current_price = price_override or self.get_symbol_price(decision.symbol)

            if decision.action == "BUY":
                # 计算仓位大小（基于余额）
                balance = self.get_account_balance()
                if 'USDT' not in balance or balance['USDT'] <= 0:
                    return {"status": "error", "message": "余额不足"}

                # 按百分比计算数量
                usdt_amount = balance['USDT'] * (decision.position_size / 100)
                amount = usdt_amount / current_price

                # 下单
                order_result = self.place_market_order(
                    symbol=decision.symbol,
                    side='buy',
                    amount=amount,
                    reason=decision.reasoning
                )

                if order_result["status"] == "success" and decision.stop_loss:
                    # 设置止损
                    self.set_stop_loss(
                        symbol=decision.symbol,
                        side='long',
                        amount=amount,
                        stop_price=decision.stop_loss,
                        reason=f"止损-{decision.reasoning[:50]}"
                    )

                return order_result

            elif decision.action == "SELL":
                # 检查是否有持仓
                positions = self.get_open_positions()
                btc_position = None
                for pos in positions:
                    if pos['symbol'] == decision.symbol and float(pos['contracts']) > 0:
                        btc_position = pos
                        break

                if not btc_position:
                    return {"status": "error", "message": f"未找到 {decision.symbol} 的持仓"}

                # 按百分比平仓
                amount = float(btc_position['contracts']) * (decision.position_size / 100)

                # 下单
                order_result = self.place_market_order(
                    symbol=decision.symbol,
                    side='sell',
                    amount=amount,
                    reason=decision.reasoning
                )

                return order_result

            else:  # HOLD
                return {
                    "status": "hold",
                    "message": "HOLD决策，无操作",
                    "symbol": decision.symbol,
                    "action": "HOLD"
                }

        except Exception as e:
            logger.error(f"执行交易决策失败: {e}")
            return {"status": "error", "message": str(e)}

    def _update_position_from_order(self, order: OrderInfo):
        """从订单更新持仓"""
        # 这里可以添加持仓更新逻辑
        # 由于Binance期货API会处理持仓，我们主要通过API查询
        pass

    def _save_order(self, order: OrderInfo):
        """保存订单到数据库"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO orders
                (order_id, symbol, side, type, amount, price, status,
                 filled_amount, filled_price, timestamp, fee, pnl)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                order.order_id, order.symbol, order.side, order.type,
                order.amount, order.price, order.status,
                order.filled_amount, order.filled_price,
                order.timestamp.isoformat(), order.fee, order.pnl
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"保存订单失败: {e}")

    def _save_balances(self, balances: Dict[str, float]):
        """保存余额到数据库"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            for asset, amount in balances.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO balances
                    (asset, free, locked, total)
                    VALUES (?, ?, ?, ?)
                ''', (asset, amount, 0, amount))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"保存余额失败: {e}")

    def get_trades(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取交易记录"""
        return [order.to_dict() for order in self.orders[-limit:]]

    def close(self):
        """关闭连接"""
        logger.info("真实交易执行器已关闭")
