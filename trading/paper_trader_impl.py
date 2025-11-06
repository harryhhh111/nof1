"""
纸交易模拟器

纯模拟交易，不调用真实API
用于策略回测、风险评估和开发测试
"""

import sqlite3
import random
from typing import Dict, Optional, List, Any
from datetime import datetime
import logging
from copy import deepcopy

from trading.base import TradingInterface, OrderInfo
from models.trading_decision import TradingDecision
from data_fetcher import DataFetcher

logger = logging.getLogger(__name__)


class PaperTraderImpl(TradingInterface):
    """
    纸交易模拟器

    特点：
    - 纯模拟交易，不调用真实API
    - 基于实时市场价格
    - 完整的订单和持仓管理
    - 无真实资金风险
    """

    def __init__(
        self,
        database_path: Optional[str] = None,
        fee_rate: float = 0.001,
        use_futures: bool = False,
        initial_balance: Optional[Dict[str, float]] = None
    ):
        """
        初始化纸交易模拟器

        Args:
            database_path: 数据库路径
            fee_rate: 手续费率
            use_futures: 是否使用期货交易
            initial_balance: 初始余额，默认为 10000 USDT
        """
        self.fee_rate = fee_rate
        self.use_futures = use_futures
        self.database_path = database_path or "paper_trading.db"

        # 初始化余额
        if initial_balance is None:
            self.initial_balance = {
                'USDT': 10000.0,  # 初始 10000 USDT
                'BTC': 0.0,
                'ETH': 0.0,
                'BNB': 0.0,
                'SOL': 0.0,
                'XRP': 0.0,
                'DOGE': 0.0,
            }
        else:
            self.initial_balance = deepcopy(initial_balance)

        self.balances = deepcopy(self.initial_balance)
        self.orders: List[OrderInfo] = []
        self.positions: Dict[str, Dict] = {}  # symbol -> position info

        # 创建数据获取器用于获取实时价格
        self.data_fetcher = DataFetcher(use_futures=use_futures)

        self._mode_name = "PAPER TRADING (Simulator)"
        self._init_database()
        logger.info(f"纸交易模拟器已初始化 - 模式: {self._mode_name}")
        logger.info(f"初始余额: {self.balances}")

    def _init_database(self):
        """初始化数据库"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()

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

    def _generate_order_id(self) -> str:
        """生成订单ID"""
        import uuid
        return str(uuid.uuid4())[:8]

    def get_account_balance(self) -> Dict[str, float]:
        """
        获取账户余额

        Returns:
            余额字典
        """
        logger.debug(f"纸交易余额: {self.balances}")
        return self.balances.copy()

    def get_symbol_price(self, symbol: str) -> float:
        """
        获取当前价格（从真实市场获取）

        Args:
            symbol: 交易对

        Returns:
            当前价格
        """
        try:
            ticker = self.data_fetcher.get_ticker(symbol)
            price = float(ticker['last'])
            logger.debug(f"纸交易 {symbol} 当前价格: {price}")
            return price
        except Exception as e:
            logger.error(f"纸交易获取 {symbol} 价格失败: {e}")
            # 如果获取失败，返回一个默认值
            if symbol == 'BTCUSDT':
                return 50000.0
            elif symbol == 'ETHUSDT':
                return 3000.0
            else:
                return 100.0

    def place_market_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        reason: str = ""
    ) -> Dict[str, Any]:
        """
        下市价单（模拟执行）

        Args:
            symbol: 交易对
            side: 买卖方向
            amount: 数量
            reason: 原因

        Returns:
            执行结果
        """
        try:
            # 获取当前价格
            current_price = self.get_symbol_price(symbol)
            base_asset = symbol.replace('USDT', '')
            quote_asset = 'USDT'

            # 计算订单价值
            order_value = amount * current_price

            if side.lower() == 'buy':
                # 检查余额
                if self.balances.get(quote_asset, 0) < order_value:
                    return {
                        "status": "error",
                        "message": f"余额不足，需要 {quote_asset} {order_value:.2f}，实际 {self.balances.get(quote_asset, 0):.2f}",
                        "symbol": symbol,
                        "side": side,
                        "amount": amount
                    }

                # 扣除资金
                self.balances[quote_asset] -= order_value
                fee = order_value * self.fee_rate
                self.balances[quote_asset] -= fee

                # 增加资产
                self.balances[base_asset] = self.balances.get(base_asset, 0) + amount

                # 更新持仓
                self._update_position(symbol, 'buy', amount, current_price)

                status = 'filled'
                filled_price = current_price

            else:  # sell
                # 检查资产余额
                if self.balances.get(base_asset, 0) < amount:
                    return {
                        "status": "error",
                        "message": f"资产不足，需要 {base_asset} {amount:.6f}，实际 {self.balances.get(base_asset, 0):.6f}",
                        "symbol": symbol,
                        "side": side,
                        "amount": amount
                    }

                # 扣除资产
                self.balances[base_asset] -= amount

                # 增加资金
                self.balances[quote_asset] = self.balances.get(quote_asset, 0) + order_value
                fee = order_value * self.fee_rate
                self.balances[quote_asset] -= fee

                # 更新持仓
                self._update_position(symbol, 'sell', amount, current_price)

                status = 'filled'
                filled_price = current_price

            # 创建订单信息
            order_info = OrderInfo(
                order_id=self._generate_order_id(),
                symbol=symbol,
                side=side,
                type='market',
                amount=amount,
                price=current_price,
                status=status,
                filled_amount=amount,
                filled_price=filled_price,
                fee=fee if side.lower() == 'buy' else order_value * self.fee_rate
            )
            self.orders.append(order_info)
            self._save_order(order_info)
            self._save_balances(self.balances)

            logger.info(f"纸交易市价单执行: {symbol} {side} {amount} @ {current_price:.4f}")
            return {
                "status": "success",
                "order_id": order_info.order_id,
                "symbol": symbol,
                "side": side,
                "amount": amount,
                "price": filled_price,
                "fee": order_info.fee,
                "message": f"{reason} (Paper Trading)"
            }

        except Exception as e:
            logger.error(f"纸交易下市价单失败: {e}")
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
        下限价单（模拟执行）

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
            current_price = self.get_symbol_price(symbol)
            base_asset = symbol.replace('USDT', '')
            quote_asset = 'USDT'

            # 检查是否应该立即成交
            should_fill = False
            if side.lower() == 'buy' and current_price <= price:
                should_fill = True
            elif side.lower() == 'sell' and current_price >= price:
                should_fill = True

            if should_fill:
                # 立即成交
                return self.place_market_order(symbol, side, amount, f"{reason} (Limit filled)")
            else:
                # 创建挂单
                order_info = OrderInfo(
                    order_id=self._generate_order_id(),
                    symbol=symbol,
                    side=side,
                    type='limit',
                    amount=amount,
                    price=price,
                    status='pending'
                )
                self.orders.append(order_info)
                self._save_order(order_info)

                logger.info(f"纸交易限价单提交: {symbol} {side} {amount} @ {price} (等待成交)")
                return {
                    "status": "success",
                    "order_id": order_info.order_id,
                    "symbol": symbol,
                    "side": side,
                    "amount": amount,
                    "price": price,
                    "status": "pending",
                    "message": f"{reason} (Paper Trading - Pending)"
                }

        except Exception as e:
            logger.error(f"纸交易下限价单失败: {e}")
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
        撤单（模拟）

        Args:
            symbol: 交易对
            order_id: 订单ID

        Returns:
            执行结果
        """
        for order in self.orders:
            if order.order_id == order_id and order.symbol == symbol:
                if order.status == 'pending':
                    order.status = 'cancelled'
                    self._save_order(order)
                    logger.info(f"纸交易撤单成功: {symbol} {order_id}")
                    return {"status": "success", "message": "撤单成功"}
                else:
                    return {"status": "error", "message": "订单已成交，无法撤单"}

        return {"status": "error", "message": "订单不存在"}

    def get_order_status(self, symbol: str, order_id: str) -> Dict[str, Any]:
        """
        获取订单状态

        Args:
            symbol: 交易对
            order_id: 订单ID

        Returns:
            订单状态
        """
        for order in self.orders:
            if order.order_id == order_id and order.symbol == symbol:
                return {
                    "status": "success",
                    "order": order.to_dict()
                }

        return {"status": "error", "message": "订单不存在"}

    def get_open_positions(self) -> List[Dict[str, Any]]:
        """
        获取所有持仓

        Returns:
            持仓列表
        """
        positions = []
        for symbol, pos_info in self.positions.items():
            base_asset = symbol.replace('USDT', '')
            amount = self.balances.get(base_asset, 0)

            if amount > 0:
                try:
                    current_price = self.get_symbol_price(symbol)
                    value = amount * current_price
                    positions.append({
                        'symbol': symbol,
                        'contracts': amount,
                        'side': 'long',
                        'entryPrice': pos_info.get('entry_price', 0),
                        'margin': 0,
                        'percentage': 0,
                        'current_price': current_price,
                        'value': value,
                        'unrealized_pnl': value - (amount * pos_info.get('entry_price', 0)),
                        'is_initial_asset': False,
                        'asset': base_asset,
                        'mode': 'Paper Trading'
                    })
                except Exception:
                    positions.append({
                        'symbol': symbol,
                        'contracts': amount,
                        'side': 'long',
                        'entryPrice': pos_info.get('entry_price', 0),
                        'margin': 0,
                        'percentage': 0,
                        'current_price': None,
                        'value': None,
                        'unrealized_pnl': None,
                        'is_initial_asset': False,
                        'asset': base_asset,
                        'mode': 'Paper Trading'
                    })

        return positions

    def set_stop_loss(
        self,
        symbol: str,
        side: str,
        amount: float,
        stop_price: float,
        reason: str = ""
    ) -> Dict[str, Any]:
        """
        设置止损单（模拟）

        Args:
            symbol: 交易对
            side: 持仓方向
            amount: 数量
            stop_price: 触发价格
            reason: 原因

        Returns:
            执行结果
        """
        # 在纸交易中，我们可以记录止损设置但不实际执行
        logger.info(f"纸交易止损单设置: {symbol} {side} {amount} @ {stop_price}")
        return {
            "status": "success",
            "order_id": self._generate_order_id(),
            "symbol": symbol,
            "side": side,
            "amount": amount,
            "stop_price": stop_price,
            "message": f"{reason} (Paper Trading - Simulated)"
        }

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

        is_valid, msg = decision.validate_decision()
        if not is_valid:
            return {"status": "error", "message": f"决策无效: {msg}"}

        try:
            # 如果有价格覆盖，使用覆盖价格
            if price_override is not None:
                original_get_price = self.get_symbol_price
                self.get_symbol_price = lambda x: price_override

            current_price = price_override or self.get_symbol_price(decision.symbol)

            # 恢复原始方法
            if price_override is not None:
                self.get_symbol_price = original_get_price

            if decision.action == "BUY":
                balance = self.get_account_balance()
                if 'USDT' not in balance or balance['USDT'] <= 0:
                    return {"status": "error", "message": "纸交易余额不足"}

                usdt_amount = balance['USDT'] * (decision.position_size / 100)
                amount = usdt_amount / current_price

                order_result = self.place_market_order(
                    symbol=decision.symbol,
                    side='buy',
                    amount=amount,
                    reason=decision.reasoning
                )

                if order_result["status"] == "success" and decision.stop_loss:
                    self.set_stop_loss(
                        symbol=decision.symbol,
                        side='long',
                        amount=amount,
                        stop_price=decision.stop_loss,
                        reason=f"止损-{decision.reasoning[:50]}"
                    )

                return order_result

            elif decision.action == "SELL":
                balance = self.get_account_balance()
                base_asset = decision.symbol.replace('USDT', '').replace('BTC', '').replace('ETH', '').replace('BNB', '')
                if decision.symbol.endswith('BTCUSDT'):
                    base_asset = 'BTC'
                elif decision.symbol.endswith('ETHUSDT'):
                    base_asset = 'ETH'
                elif decision.symbol.endswith('BNBUSDT'):
                    base_asset = 'BNB'
                elif decision.symbol.endswith('SOLUSDT'):
                    base_asset = 'SOL'
                elif decision.symbol.endswith('XRPUSDT'):
                    base_asset = 'XRP'
                elif decision.symbol.endswith('DOGEUSDT'):
                    base_asset = 'DOGE'

                if base_asset not in balance or balance[base_asset] <= 0:
                    return {
                        "status": "error",
                        "message": f"纸交易 {base_asset} 余额不足，无法卖出",
                        "hint": "先买入资产才能卖出"
                    }

                # 按百分比卖出
                amount = balance[base_asset] * (decision.position_size / 100)

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
            logger.error(f"纸交易执行决策失败: {e}")
            return {"status": "error", "message": str(e)}

    def _update_position(self, symbol: str, side: str, amount: float, price: float):
        """更新持仓信息"""
        if symbol not in self.positions:
            self.positions[symbol] = {
                'entry_price': price,
                'total_amount': 0,
                'total_cost': 0
            }

        if side.lower() == 'buy':
            self.positions[symbol]['total_amount'] += amount
            self.positions[symbol]['total_cost'] += amount * price
            self.positions[symbol]['entry_price'] = self.positions[symbol]['total_cost'] / self.positions[symbol]['total_amount']
        else:  # sell
            self.positions[symbol]['total_amount'] -= amount
            if self.positions[symbol]['total_amount'] <= 0:
                self.positions[symbol]['total_amount'] = 0
                self.positions[symbol]['entry_price'] = 0

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

    def reset_account(self, initial_balance: Optional[Dict[str, float]] = None):
        """
        重置账户（用于回测）

        Args:
            initial_balance: 新的初始余额
        """
        if initial_balance:
            self.initial_balance = deepcopy(initial_balance)
        self.balances = deepcopy(self.initial_balance)
        self.orders = []
        self.positions = {}
        logger.info(f"纸交易账户已重置，余额: {self.balances}")

    def get_performance_summary(self) -> Dict[str, Any]:
        """
        获取性能摘要

        Returns:
            性能摘要
        """
        current_value = 0
        total_cost = 0

        # 计算总资产价值
        for asset, amount in self.balances.items():
            if asset == 'USDT':
                current_value += amount
            else:
                try:
                    symbol = f"{asset}USDT"
                    price = self.get_symbol_price(symbol)
                    current_value += amount * price
                except Exception:
                    pass

        # 计算总成本
        for order in self.orders:
            if order.side == 'buy':
                total_cost += order.amount * order.filled_price + order.fee
            else:
                total_cost -= order.amount * order.filled_price - order.fee

        pnl = current_value - sum(self.initial_balance.values())
        pnl_percentage = (pnl / sum(self.initial_balance.values())) * 100 if sum(self.initial_balance.values()) > 0 else 0

        return {
            "mode": "Paper Trading",
            "initial_balance": self.initial_balance,
            "current_balance": self.balances,
            "total_value": current_value,
            "total_pnl": pnl,
            "pnl_percentage": pnl_percentage,
            "total_trades": len([o for o in self.orders if o.status == 'filled']),
            "winning_trades": len([o for o in self.orders if o.status == 'filled' and o.pnl > 0]),
            "losing_trades": len([o for o in self.orders if o.status == 'filled' and o.pnl < 0])
        }

    def close(self):
        """关闭连接"""
        if hasattr(self.data_fetcher, 'close'):
            self.data_fetcher.close()
        logger.info("纸交易模拟器已关闭")

    @property
    def mode_name(self) -> str:
        """获取交易模式名称"""
        return self._mode_name

    @mode_name.setter
    def mode_name(self, value: str):
        """设置交易模式名称"""
        self._mode_name = value
