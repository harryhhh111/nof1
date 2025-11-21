"""
Hyperliquid交易执行器

使用Hyperliquid API进行交易
支持Agent Wallet安全模式、市价单、限价单、止损止盈等
"""

import os
import json
import sqlite3
import logging
from typing import Dict, Optional, List, Any
from datetime import datetime
from dataclasses import dataclass, asdict
import asyncio
from threading import Lock

from trading.base import TradingInterface, OrderInfo
from models.trading_decision import TradingDecision

# Hyperliquid SDK imports
try:
    from hyperliquid.exchange import Exchange
    from hyperliquid.info import Info
    from hyperliquid.exchange import Cloid
    from eth_account import Account
    import eth_utils
except ImportError as e:
    print(f"❌ Hyperliquid SDK 未安装: {e}")
    print("请运行: source venv/bin/activate && pip install -r requirements.txt")
    Exchange = None
    Info = None

logger = logging.getLogger(__name__)


@dataclass
class HyperliquidOrderInfo:
    """Hyperliquid订单信息"""
    order_id: str
    coin: str
    side: str  # 'buy' or 'sell'
    size: float
    price: float
    order_type: str  # 'limit', 'market', 'trigger'
    status: str  # 'pending', 'filled', 'cancelled'
    timestamp: datetime
    reduce_only: bool = False

    def to_order_info(self) -> OrderInfo:
        """转换为标准OrderInfo格式"""
        symbol = f"{self.coin}USDT"
        return OrderInfo(
            order_id=self.order_id,
            symbol=symbol,
            side=self.side,
            type=self.order_type,
            amount=self.size,
            price=self.price,
            status=self.status,
            timestamp=self.timestamp
        )


class HyperliquidTrader(TradingInterface):
    """
    Hyperliquid交易执行器

    支持：
    - Agent Wallet安全模式
    - Mainnet/Testnet环境
    - 市价单/限价单/触发单
    - 止损止盈
    - 持仓管理
    - 杠杆设置
    """

    def __init__(
        self,
        database_path: Optional[str] = None,
        use_testnet: bool = False,
        agent_private_key: Optional[str] = None,
        main_wallet_address: Optional[str] = None
    ):
        """
        初始化Hyperliquid交易执行器

        Args:
            database_path: 数据库路径
            use_testnet: 是否使用测试网
            agent_private_key: Agent钱包私钥（用于签名）
            main_wallet_address: 主钱包地址（持有资金）
        """
        if Exchange is None or Info is None:
            raise ImportError("Hyperliquid SDK 未安装，请运行: source venv/bin/activate && pip install -r requirements.txt")

        # Agent Wallet 安全配置
        self.agent_private_key = agent_private_key or os.getenv("HYPERLIQUID_PRIVATE_KEY")
        self.main_wallet_address = main_wallet_address or os.getenv("HYPERLIQUID_WALLET_ADDRESS")

        if not self.agent_private_key:
            raise ValueError("❌ 未配置Agent钱包私钥，请设置 HYPERLIQUID_PRIVATE_KEY 环境变量")

        if not self.main_wallet_address:
            raise ValueError("❌ 未配置主钱包地址，请设置 HYPERLIQUID_WALLET_ADDRESS 环境变量")

        # 验证地址格式
        if not self.main_wallet_address.startswith("0x") or len(self.main_wallet_address) != 42:
            raise ValueError(f"❌ 主钱包地址格式错误: {self.main_wallet_address}")

        # API端点配置
        self.use_testnet = use_testnet
        self.base_url = "https://api.hyperliquid-testnet.xyz/info" if use_testnet else "https://api.hyperliquid.xyz/info"

        # 初始化Exchange客户端
        try:
            # 去掉私钥的0x前缀（如果有）
            private_key = self.agent_private_key.replace("0x", "") if self.agent_private_key.startswith("0x") else self.agent_private_key

            # 创建Exchange实例
            self.exchange = Exchange(
                private_key,
                account_address=self.main_wallet_address
            )

            # 创建Info实例
            self.info = Info()

            # 获取Agent钱包地址（从私钥推导）
            agent_account = Account.from_key(private_key)
            self.agent_address = agent_account.address

            # 安全检查：验证Agent和主钱包地址不同
            if self.agent_address.lower() == self.main_wallet_address.lower():
                logger.warning("⚠️  Agent钱包地址与主钱包地址相同，这不是推荐的安全配置")
                logger.warning("   建议: 创建单独的Agent钱包，仅用于签名操作")
            else:
                logger.info("✅ Agent Wallet安全模式已启用")
                logger.info(f"   Agent地址: {self.agent_address} (签名)")
                logger.info(f"   主钱包地址: {self.main_wallet_address} (资金)")

        except Exception as e:
            logger.error(f"初始化Hyperliquid客户端失败: {e}")
            raise

        self.database_path = database_path or "hyperliquid_trading.db"
        self.positions: Dict[str, Dict] = {}
        self.orders: List[HyperliquidOrderInfo] = []
        self.meta_cache = None
        self.meta_lock = Lock()

        self._init_database()
        self._refresh_meta()

        mode_name = "Hyperliquid Testnet" if use_testnet else "Hyperliquid Mainnet"
        logger.info(f"Hyperliquid交易执行器已初始化 - 模式: {mode_name}")

    def _init_database(self):
        """初始化数据库"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()

            # 创建订单表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    order_id TEXT PRIMARY KEY,
                    coin TEXT,
                    side TEXT,
                    size REAL,
                    price REAL,
                    order_type TEXT,
                    status TEXT,
                    timestamp TEXT,
                    reduce_only BOOLEAN
                )
            ''')

            # 创建持仓表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS positions (
                    coin TEXT PRIMARY KEY,
                    side TEXT,
                    size REAL,
                    entry_price REAL,
                    mark_price REAL,
                    unrealized_pnl REAL,
                    leverage REAL
                )
            ''')

            conn.commit()
            conn.close()
            logger.info("Hyperliquid数据库初始化成功")
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise

    def _refresh_meta(self):
        """刷新meta信息（包含精度等）"""
        try:
            with self.meta_lock:
                self.meta_cache = self.info.meta()
                logger.info(f"Meta信息已刷新，包含 {len(self.meta_cache['universe'])} 个资产")
        except Exception as e:
            logger.error(f"刷新Meta信息失败: {e}")
            self.meta_cache = {'universe': []}

    def _get_sz_decimals(self, coin: str) -> int:
        """获取币种的数量精度"""
        try:
            with self.meta_lock:
                if not self.meta_cache:
                    self._refresh_meta()

                for asset in self.meta_cache.get('universe', []):
                    if asset['name'] == coin:
                        return asset.get('szDecimals', 4)

                logger.warning(f"未找到 {coin} 的精度信息，使用默认精度4")
                return 4
        except Exception as e:
            logger.error(f"获取 {coin} 精度失败: {e}")
            return 4

    def _round_to_sz_decimals(self, coin: str, value: float) -> float:
        """将数值四舍五入到正确的数量精度"""
        decimals = self._get_sz_decimals(coin)
        multiplier = 10 ** decimals
        return round(value * multiplier) / multiplier

    def _round_price_to_sigfigs(self, price: float, sigfigs: int = 5) -> float:
        """将价格四舍五入到指定有效数字"""
        if price == 0:
            return 0

        import math
        magnitude = math.floor(math.log10(abs(price)))
        factor = 10 ** (sigfigs - 1 - magnitude)
        return round(price * factor) / factor

    def _convert_symbol_to_hyperliquid(self, symbol: str) -> str:
        """将标准symbol转换为Hyperliquid格式"""
        # BTCUSDT -> BTC
        if symbol.endswith('USDT'):
            return symbol[:-4]
        return symbol

    def _convert_symbol_from_hyperliquid(self, coin: str) -> str:
        """将Hyperliquid格式转换为标准symbol"""
        # BTC -> BTCUSDT
        return f"{coin}USDT"

    @property
    def mode_name(self) -> str:
        """获取交易模式名称"""
        return "Hyperliquid Testnet" if self.use_testnet else "Hyperliquid Mainnet"

    def get_account_balance(self) -> Dict[str, float]:
        """
        获取账户余额

        Returns:
            余额字典 {asset: amount}
        """
        try:
            # 获取账户状态
            user_state = self.info.user_state(self.main_wallet_address)

            # 获取现货余额
            spot_state = self.info.spot_user_state(self.main_wallet_address)

            result = {}

            # 处理现货余额
            if spot_state and 'balances' in spot_state:
                for balance in spot_state['balances']:
                    coin = balance['coin']
                    total = float(balance['total'])
                    if total > 0:
                        result[coin] = total

            # 处理合约账户价值
            if 'crossMarginSummary' in user_state:
                account_value = float(user_state['crossMarginSummary']['accountValue'])
                withdrawable = float(user_state['withdrawable'])

                # USDC作为主要计价货币
                result['USDC'] = result.get('USDC', 0) + withdrawable
                result['total_account_value'] = account_value

            logger.info(f"获取Hyperliquid余额: {result}")
            self._save_balances(result)
            return result

        except Exception as e:
            logger.error(f"获取Hyperliquid余额失败: {e}")
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
            coin = self._convert_symbol_to_hyperliquid(symbol)

            # 获取所有市场价格
            all_mids = self.info.all_mids()

            if coin in all_mids:
                price = float(all_mids[coin])
                logger.debug(f"{symbol} 当前价格: {price}")
                return price
            else:
                raise ValueError(f"未找到 {coin} 的价格信息")

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
            coin = self._convert_symbol_to_hyperliquid(symbol)

            # 获取当前价格用于创建aggressive limit order
            current_price = self.get_symbol_price(symbol)

            # 市价单使用aggressive limit order实现
            if side.lower() == 'buy':
                # 买入时使用略高于市场价的价格
                price = self._round_price_to_sigfigs(current_price * 1.001)
                is_buy = True
            else:
                # 卖出时使用略低于市场价的价格
                price = self._round_price_to_sigfigs(current_price * 0.999)
                is_buy = False

            # 数量精度处理
            size = self._round_to_sz_decimals(coin, amount)

            # 创建订单
            order_result = self.exchange.order(
                coin=coin,
                is_buy=is_buy,
                size=size,
                price=price,
                order_type={"limit": {"tif": "ioc"}},  # Immediate or Cancel
                reduce_only=False
            )

            # 记录订单
            order_info = HyperliquidOrderInfo(
                order_id=str(order_result.get('oid', '')),
                coin=coin,
                side=side,
                size=size,
                price=price,
                order_type='market',
                status='filled',
                timestamp=datetime.now()
            )
            self.orders.append(order_info)
            self._save_order(order_info)

            logger.info(f"Hyperliquid市价单执行成功: {symbol} {side} {size} @ {price}")
            return {
                "status": "success",
                "order_id": order_info.order_id,
                "symbol": symbol,
                "side": side,
                "amount": size,
                "price": price,
                "message": reason
            }

        except Exception as e:
            logger.error(f"Hyperliquid下市价单失败: {e}")
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
            coin = self._convert_symbol_to_hyperliquid(symbol)

            # 价格和数量精度处理
            rounded_price = self._round_price_to_sigfigs(price)
            size = self._round_to_sz_decimals(coin, amount)

            # 创建订单
            order_result = self.exchange.order(
                coin=coin,
                is_buy=(side.lower() == 'buy'),
                size=size,
                price=rounded_price,
                order_type={"limit": {"tif": "gtc"}},  # Good Til Cancelled
                reduce_only=False
            )

            # 记录订单
            order_info = HyperliquidOrderInfo(
                order_id=str(order_result.get('oid', '')),
                coin=coin,
                side=side,
                size=size,
                price=rounded_price,
                order_type='limit',
                status='pending',
                timestamp=datetime.now()
            )
            self.orders.append(order_info)
            self._save_order(order_info)

            logger.info(f"Hyperliquid限价单提交成功: {symbol} {side} {size} @ {rounded_price}")
            return {
                "status": "success",
                "order_id": order_info.order_id,
                "symbol": symbol,
                "side": side,
                "amount": size,
                "price": rounded_price,
                "message": reason
            }

        except Exception as e:
            logger.error(f"Hyperliquid下限价单失败: {e}")
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
            coin = self._convert_symbol_to_hyperliquid(symbol)

            # 取消订单
            self.exchange.cancel_by_cloid(coin, Cloid(order_id))

            logger.info(f"Hyperliquid撤单成功: {symbol} {order_id}")
            return {"status": "success", "message": "撤单成功"}

        except Exception as e:
            logger.error(f"Hyperliquid撤单失败: {e}")
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
            coin = self._convert_symbol_to_hyperliquid(symbol)

            # 获取订单状态
            orders = self.info.open_orders(self.main_wallet_address)

            for order in orders:
                if str(order['oid']) == order_id:
                    return {
                        "status": "success",
                        "order": order
                    }

            return {"status": "error", "message": "未找到订单"}

        except Exception as e:
            logger.error(f"查询Hyperliquid订单失败: {e}")
            return {"status": "error", "message": str(e)}

    def get_open_positions(self) -> List[Dict[str, Any]]:
        """
        获取所有持仓

        Returns:
            持仓列表
        """
        try:
            # 获取账户状态
            user_state = self.info.user_state(self.main_wallet_address)

            positions = []

            # 处理持仓信息
            if 'assetPositions' in user_state:
                for asset_pos in user_state['assetPositions']:
                    position = asset_pos['position']

                    # 持仓数量
                    size = float(position['szi'])
                    if size == 0:
                        continue

                    coin = position['coin']
                    symbol = self._convert_symbol_from_hyperliquid(coin)

                    pos_data = {
                        'symbol': symbol,
                        'side': 'long' if size > 0 else 'short',
                        'positionAmt': abs(size),
                        'entryPrice': float(position['entryPx']) if position['entryPx'] else 0,
                        'markPrice': float(position['positionValue']) / abs(size) if size != 0 else 0,
                        'unRealizedProfit': float(position['unrealizedPnl']),
                        'leverage': float(position['leverage']['value']) if position['leverage'] else 1
                    }

                    positions.append(pos_data)

            return positions

        except Exception as e:
            logger.error(f"获取Hyperliquid持仓失败: {e}")
            return []

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
        try:
            coin = self._convert_symbol_to_hyperliquid(symbol)

            # 判断止损单的买卖方向
            # 空仓止损（回补）= 买入，多仓止损（平仓）= 卖出
            is_buy = side.lower() == 'short'

            # 数量和价格精度处理
            size = self._round_to_sz_decimals(coin, amount)
            rounded_stop_price = self._round_price_to_sigfigs(stop_price)

            # 创建触发止损单
            order_result = self.exchange.order(
                coin=coin,
                is_buy=is_buy,
                size=size,
                price=rounded_stop_price,
                order_type={"trigger": {"triggerPx": rounded_stop_price, "isMarket": True, "tpsl": "sl"}},
                reduce_only=True
            )

            # 记录订单
            order_info = HyperliquidOrderInfo(
                order_id=str(order_result.get('oid', '')),
                coin=coin,
                side=side,
                size=size,
                price=rounded_stop_price,
                order_type='stop_loss',
                status='pending',
                timestamp=datetime.now(),
                reduce_only=True
            )
            self.orders.append(order_info)
            self._save_order(order_info)

            logger.info(f"Hyperliquid止损单设置成功: {symbol} {side} {size} @ {rounded_stop_price}")
            return {
                "status": "success",
                "order_id": order_info.order_id,
                "symbol": symbol,
                "side": side,
                "amount": size,
                "stop_price": rounded_stop_price,
                "message": reason
            }

        except Exception as e:
            logger.error(f"Hyperliquid设置止损失败: {e}")
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
            current_price = price_override or self.get_symbol_price(decision.symbol)

            if decision.action == "BUY":
                # 按百分比计算数量（基于USDC余额）
                balance = self.get_account_balance()
                usdc_balance = balance.get('USDC', 0)

                if usdc_balance <= 0:
                    return {"status": "error", "message": "USDC余额不足"}

                # 计算交易金额
                usdt_amount = usdc_balance * (decision.position_size / 100)
                amount = usdt_amount / current_price

                # 下单
                order_result = self.place_market_order(
                    symbol=decision.symbol,
                    side='buy',
                    amount=amount,
                    reason=decision.reasoning
                )

                # 设置止损
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
                # 检查持仓
                positions = self.get_open_positions()
                position = None

                for pos in positions:
                    if pos['symbol'] == decision.symbol:
                        position = pos
                        break

                if not position:
                    return {
                        "status": "error",
                        "message": f"未找到 {decision.symbol} 的持仓"
                    }

                # 按百分比平仓
                amount = position['positionAmt'] * (decision.position_size / 100)

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
            logger.error(f"执行Hyperliquid交易决策失败: {e}")
            return {"status": "error", "message": str(e)}

    def get_trades(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取交易记录

        Args:
            limit: 返回条数限制

        Returns:
            交易记录列表
        """
        try:
            # 获取最近的订单
            recent_orders = self.orders[-limit:]

            # 转换为标准格式
            trades = []
            for order_info in recent_orders:
                trades.append(order_info.to_order_info().to_dict())

            return trades

        except Exception as e:
            logger.error(f"获取Hyperliquid交易记录失败: {e}")
            return []

    def _save_order(self, order: HyperliquidOrderInfo):
        """保存订单到数据库"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO orders
                (order_id, coin, side, size, price, order_type, status, timestamp, reduce_only)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                order.order_id, order.coin, order.side, order.size, order.price,
                order.order_type, order.status, order.timestamp.isoformat(), order.reduce_only
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"保存Hyperliquid订单失败: {e}")

    def _save_balances(self, balances: Dict[str, float]):
        """保存余额到数据库"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()

            # 创建余额表（如果不存在）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS balances (
                    asset TEXT PRIMARY KEY,
                    amount REAL,
                    timestamp TEXT
                )
            ''')

            timestamp = datetime.now().isoformat()
            for asset, amount in balances.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO balances
                    (asset, amount, timestamp)
                    VALUES (?, ?, ?)
                ''', (asset, amount, timestamp))

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"保存Hyperliquid余额失败: {e}")

    def close(self):
        """关闭连接/清理资源"""
        logger.info("Hyperliquid交易执行器已关闭")