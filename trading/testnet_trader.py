"""
Testnet 交易器

使用 Binance Testnet API 进行真实模拟交易
支持市价单、限价单、止损止盈等
"""

import ccxt
import json
import sqlite3
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
import logging
from pathlib import Path

from trading.base import TradingInterface, OrderInfo
from models.trading_decision import TradingDecision

logger = logging.getLogger(__name__)


class TestnetTrader(TradingInterface):
    """
    Testnet 交易器

    使用 Binance Testnet (testnet.binance.vision) 进行交易
    - 真实 API 调用
    - 虚拟资金
    - 完整的订单管理
    """

    def __init__(
        self,
        database_path: Optional[str] = None,
        fee_rate: float = 0.001,
        use_futures: bool = False,
        use_live: bool = False
    ):
        """
        初始化 Testnet 交易器

        Args:
            database_path: 数据库路径
            fee_rate: 手续费率
            use_futures: 是否使用期货交易
            use_live: 是否使用真实API（测试用）
        """
        import config

        self.fee_rate = fee_rate
        self.use_futures = use_futures
        self.use_live = use_live
        self.database_path = database_path or "real_trading.db"
        self.positions: Dict[str, Dict] = {}
        self.orders: List[OrderInfo] = []

        # 选择合适的交易所配置
        if use_live:
            # 使用真实API（注意：这是高风险操作）
            if use_futures:
                self.exchange = ccxt.binance({
                    'apiKey': config.BINANCE_API_KEY,
                    'secret': config.BINANCE_SECRET_KEY,
                    'type': 'future',
                    'enableRateLimit': True,
                })
                self._mode_name = "LIVE (Futures)"
            else:
                self.exchange = ccxt.binance({
                    'apiKey': config.BINANCE_API_KEY,
                    'secret': config.BINANCE_SECRET_KEY,
                    'type': 'spot',
                    'enableRateLimit': True,
                })
                self._mode_name = "LIVE (Spot)"
            logger.warning("⚠️  使用真实API - 真实资金风险！")
        else:
            # 使用 Testnet
            if use_futures:
                self.exchange = ccxt.binance({
                    **config.FUTURES_CONFIG,
                    'type': 'future'
                })
                self._mode_name = "TESTNET (Futures)"
            else:
                self.exchange = ccxt.binance({
                    **config.EXCHANGE_CONFIG,
                    'type': 'spot'
                })
                self._mode_name = "TESTNET (Spot)"

        # 验证API Key
        if not config.BINANCE_API_KEY or not config.BINANCE_SECRET_KEY:
            error_msg = f"未配置API Key！请检查config.py中的配置"
            logger.error(error_msg)
            raise ValueError(error_msg)

        self._init_database()
        logger.info(f"Testnet交易器已初始化 - 模式: {self.mode_name}")
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
        """获取账户余额"""
        try:
            balance = self.exchange.fetch_balance()
            result = {asset: amount for asset, amount in balance['total'].items() if amount > 0}
            logger.debug(f"获取余额: {result}")
            self._save_balances(result)
            return result
        except Exception as e:
            logger.error(f"获取余额失败: {e}")
            return {}

    def get_symbol_price(self, symbol: str) -> float:
        """获取当前价格"""
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
        side: str,
        amount: float,
        reason: str = ""
    ) -> Dict[str, Any]:
        """下市价单"""
        try:
            order = self.exchange.create_market_order(symbol, side, amount)

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
        """下限价单"""
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
        """撤单"""
        try:
            self.exchange.cancel_order(order_id, symbol)
            logger.info(f"撤单成功: {symbol} {order_id}")
            return {"status": "success", "message": "撤单成功"}
        except Exception as e:
            logger.error(f"撤单失败: {e}")
            return {"status": "error", "message": str(e)}

    def get_order_status(self, symbol: str, order_id: str) -> Dict[str, Any]:
        """获取订单状态"""
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
        """获取所有持仓"""
        try:
            balance = self.get_account_balance()
            positions = []

            # 过滤出非稳定币资产（初始资产）
            initial_assets = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'DOGE', 'ADA', 'DOT', 'AVAX', 'MATIC']
            for asset, amount in balance.items():
                if asset not in ['USDT', 'USDC', 'BUSD', 'TUSD', 'FDUSD'] and amount > 0.000001:
                    symbol = asset + 'USDT'
                    try:
                        current_price = self.get_symbol_price(symbol)
                        value = amount * current_price
                        positions.append({
                            'symbol': symbol,
                            'contracts': amount,
                            'side': 'long',
                            'entryPrice': 0,
                            'margin': 0,
                            'percentage': 0,
                            'current_price': current_price,
                            'value': value,
                            'is_initial_asset': asset in initial_assets,
                            'asset': asset
                        })
                    except Exception:
                        positions.append({
                            'symbol': symbol,
                            'contracts': amount,
                            'side': 'long',
                            'entryPrice': 0,
                            'margin': 0,
                            'percentage': 0,
                            'current_price': None,
                            'value': None,
                            'is_initial_asset': asset in initial_assets,
                            'asset': asset
                        })

            return positions
        except Exception as e:
            logger.error(f"获取持仓失败: {e}")
            return []

    def set_stop_loss(
        self,
        symbol: str,
        side: str,
        amount: float,
        stop_price: float,
        reason: str = ""
    ) -> Dict[str, Any]:
        """设置止损单"""
        try:
            if side.lower() == 'long':
                limit_price = stop_price * 0.995
            else:
                limit_price = stop_price * 1.005

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
        """执行交易决策"""
        if not decision.symbol:
            return {"status": "error", "message": "缺少交易对符号"}

        is_valid, msg = decision.validate_decision()
        if not is_valid:
            return {"status": "error", "message": f"决策无效: {msg}"}

        try:
            current_price = price_override or self.get_symbol_price(decision.symbol)

            if decision.action == "BUY":
                balance = self.get_account_balance()
                if 'USDT' not in balance or balance['USDT'] <= 0:
                    return {"status": "error", "message": "余额不足"}

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
                positions = self.get_open_positions()
                position = None
                for pos in positions:
                    if pos['symbol'] == decision.symbol and float(pos['contracts']) > 0:
                        position = pos
                        break

                if not position:
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

                    if base_asset in balance and balance[base_asset] > 0:
                        initial_balance = balance[base_asset]
                        amount = initial_balance * (decision.position_size / 100)
                        logger.info(f"使用初始 {base_asset} 持仓进行做空: {amount}")
                    else:
                        return {
                            "status": "error",
                            "message": f"未找到 {decision.symbol} 的持仓且无初始 {base_asset} 资产",
                            "hint": "Testnet 可使用初始资产进行做空操作"
                        }
                else:
                    amount = float(position['contracts']) * (decision.position_size / 100)

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
        # Testnet 模式下，持仓由 API 自动管理
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
        logger.info("Testnet交易器已关闭")

    @property
    def mode_name(self) -> str:
        """获取交易模式名称"""
        return self._mode_name

    @mode_name.setter
    def mode_name(self, value: str):
        """设置交易模式名称"""
        self._mode_name = value
