"""
纸交易执行器

实现模拟交易功能，用于在没有真实资金风险的情况下测试交易策略
"""

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
class Position:
    """持仓信息"""

    symbol: str
    side: str  # 'long' or 'short'
    size: float
    entry_price: float
    entry_time: datetime
    current_price: float
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

    def update_price(self, new_price: float):
        """更新当前价格"""
        self.current_price = new_price
        if self.side == 'long':
            self.unrealized_pnl = (new_price - self.entry_price) * self.size
        else:
            self.unrealized_pnl = (self.entry_price - new_price) * self.size

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['entry_time'] = self.entry_time.isoformat()
        return data


@dataclass
class Trade:
    """交易记录"""

    trade_id: str
    symbol: str
    side: str  # 'buy' or 'sell'
    size: float
    price: float
    timestamp: datetime
    pnl: float = 0.0
    fee: float = 0.0
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class PaperTrader:
    """
    纸交易执行器

    特点：
    - 使用虚拟资金进行模拟交易
    - 记录所有交易和持仓
    - 计算PnL和性能指标
    - 支持止损止盈自动平仓
    """

    def __init__(
        self,
        initial_balance: float = 100000.0,
        database_path: Optional[str] = None,
        fee_rate: float = 0.001  # 0.1% 手续费
    ):
        """
        初始化纸交易执行器

        Args:
            initial_balance: 初始资金
            database_path: 数据库路径
            fee_rate: 手续费率
        """
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.fee_rate = fee_rate
        self.positions: Dict[str, Position] = {}  # symbol -> Position
        self.trades: List[Trade] = []
        self.database_path = database_path or "paper_trading.db"
        self._init_database()

    def _init_database(self):
        """初始化数据库"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()

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

            # 创建交易记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    trade_id TEXT PRIMARY KEY,
                    symbol TEXT,
                    side TEXT,
                    size REAL,
                    price REAL,
                    timestamp TEXT,
                    pnl REAL,
                    fee REAL,
                    reason TEXT
                )
            ''')

            # 创建账户历史表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS account_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    balance REAL,
                    total_value REAL,
                    unrealized_pnl REAL,
                    realized_pnl REAL
                )
            ''')

            conn.commit()
            conn.close()
            logger.info("纸交易数据库初始化成功")
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")

    def execute_decision(
        self,
        decision: TradingDecision,
        current_price: float
    ) -> Dict[str, Any]:
        """
        执行交易决策

        Args:
            decision: 交易决策
            current_price: 当前价格

        Returns:
            执行结果
        """
        if not decision.symbol:
            return {"status": "error", "message": "缺少交易对符号"}

        try:
            # 验证决策
            is_valid, msg = decision.validate_decision()
            if not is_valid:
                return {"status": "error", "message": f"决策无效: {msg}"}

            # 执行交易
            if decision.action == "BUY":
                return self._buy(
                    symbol=decision.symbol,
                    position_size_pct=decision.position_size,
                    price=current_price,
                    stop_loss=decision.stop_loss,
                    take_profit=decision.take_profit,
                    reason=decision.reasoning
                )
            elif decision.action == "SELL":
                return self._sell(
                    symbol=decision.symbol,
                    position_size_pct=decision.position_size,
                    price=current_price,
                    reason=decision.reasoning
                )
            else:  # HOLD
                return {
                    "status": "hold",
                    "message": "HOLD决策，无操作",
                    "balance": self.balance,
                    "position": self.positions.get(decision.symbol).to_dict() if decision.symbol in self.positions else None
                }

        except Exception as e:
            logger.error(f"执行交易决策失败: {e}")
            return {"status": "error", "message": str(e)}

    def _buy(
        self,
        symbol: str,
        position_size_pct: float,
        price: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        reason: str = ""
    ) -> Dict[str, Any]:
        """买入操作"""
        # 将百分比转换为绝对大小
        if position_size_pct <= 0:
            return {"status": "error", "message": "仓位大小必须大于0"}

        # 计算买入数量（基于百分比）
        position_value = self.balance * (position_size_pct / 100.0)
        size = position_value / price

        # 计算所需资金（包含手续费）
        amount = price * size
        fee = amount * self.fee_rate
        total_cost = amount + fee

        if total_cost > self.balance:
            return {"status": "error", "message": "余额不足"}

        # 检查是否已持仓
        if symbol in self.positions:
            position = self.positions[symbol]
            if position.side == 'long':
                # 加仓
                new_size = position.size + size
                new_entry_price = (position.entry_price * position.size + price * size) / new_size
                position.size = new_size
                position.entry_price = new_entry_price
                position.stop_loss = stop_loss or position.stop_loss
                position.take_profit = take_profit or position.take_profit
            else:
                # 先平空头，再开多头
                self._close_position(symbol, price, "反向交易")
                return self._buy(symbol, position_size_pct, price, stop_loss, take_profit, reason)
        else:
            # 新建多头持仓
            self.positions[symbol] = Position(
                symbol=symbol,
                side='long',
                size=size,
                entry_price=price,
                entry_time=datetime.now(),
                current_price=price,
                stop_loss=stop_loss,
                take_profit=take_profit
            )

        # 扣减资金
        self.balance -= total_cost

        # 记录交易
        trade = Trade(
            trade_id=f"buy_{symbol}_{int(datetime.now().timestamp())}",
            symbol=symbol,
            side='buy',
            size=size,
            price=price,
            timestamp=datetime.now(),
            fee=fee,
            reason=reason
        )
        self.trades.append(trade)
        self._save_trade(trade)
        self._save_position(self.positions[symbol])
        self._save_account_history()

        return {
            "status": "success",
            "action": "buy",
            "symbol": symbol,
            "size": size,
            "price": price,
            "fee": fee,
            "balance": self.balance,
            "position": self.positions[symbol].to_dict()
        }

    def _sell(
        self,
        symbol: str,
        position_size_pct: float,
        price: float,
        reason: str = ""
    ) -> Dict[str, Any]:
        """卖出操作"""
        if position_size_pct <= 0:
            return {"status": "error", "message": "仓位大小必须大于0"}

        # 检查是否已持仓
        if symbol not in self.positions:
            return {"status": "error", "message": f"未持仓 {symbol}"}

        position = self.positions[symbol]

        if position.side == 'long':
            # 平多头
            if position_size_pct >= 100:
                # 全部平仓
                return self._close_position(symbol, price, reason)
            else:
                # 部分平仓
                size = position.size * (position_size_pct / 100.0)
                return self._close_position(symbol, price, reason, size)
        else:
            # 平空头
            if position_size_pct >= 100:
                # 全部平仓
                return self._close_position(symbol, price, reason)
            else:
                # 部分平仓
                size = position.size * (position_size_pct / 100.0)
                return self._close_position(symbol, price, reason, size)

    def _close_position(
        self,
        symbol: str,
        price: float,
        reason: str,
        size: Optional[float] = None
    ) -> Dict[str, Any]:
        """平仓操作"""
        position = self.positions[symbol]
        close_size = size or position.size

        # 计算PnL
        if position.side == 'long':
            pnl = (price - position.entry_price) * close_size
        else:
            pnl = (position.entry_price - price) * close_size

        # 计算手续费
        amount = price * close_size
        fee = amount * self.fee_rate
        net_pnl = pnl - fee

        # 更新资金
        self.balance += (amount - fee)
        self.balance += pnl

        # 更新持仓
        if size and size < position.size:
            # 部分平仓
            position.size -= size
            position.current_price = price
            self._save_position(position)
        else:
            # 完全平仓
            self.balance += net_pnl
            del self.positions[symbol]

        # 记录交易
        trade = Trade(
            trade_id=f"sell_{symbol}_{int(datetime.now().timestamp())}",
            symbol=symbol,
            side='sell',
            size=close_size,
            price=price,
            timestamp=datetime.now(),
            pnl=pnl,
            fee=fee,
            reason=reason
        )
        self.trades.append(trade)
        self._save_trade(trade)
        self._save_account_history()

        return {
            "status": "success",
            "action": "close",
            "symbol": symbol,
            "size": close_size,
            "price": price,
            "pnl": pnl,
            "fee": fee,
            "net_pnl": net_pnl,
            "balance": self.balance,
            "position": position.to_dict() if symbol in self.positions else None
        }

    def update_prices(self, price_data: Dict[str, float]):
        """
        更新所有持仓的当前价格

        Args:
            price_data: {symbol: price} 字典
        """
        for symbol, price in price_data.items():
            if symbol in self.positions:
                self.positions[symbol].update_price(price)

                # 检查止损止盈
                position = self.positions[symbol]
                should_close = False
                close_reason = ""

                if position.side == 'long':
                    if position.stop_loss and price <= position.stop_loss:
                        should_close = True
                        close_reason = "止损"
                    elif position.take_profit and price >= position.take_profit:
                        should_close = True
                        close_reason = "止盈"
                else:
                    if position.stop_loss and price >= position.stop_loss:
                        should_close = True
                        close_reason = "止损"
                    elif position.take_profit and price <= position.take_profit:
                        should_close = True
                        close_reason = "止盈"

                if should_close:
                    self._close_position(symbol, price, close_reason)

        self._save_account_history()

    def get_portfolio_value(self, price_data: Dict[str, float]) -> float:
        """
        计算投资组合总价值

        Args:
            price_data: 当前价格数据

        Returns:
            总价值
        """
        total = self.balance
        for symbol, position in self.positions.items():
            if symbol in price_data:
                price = price_data[symbol]
                if position.side == 'long':
                    total += position.size * price
                else:
                    total += position.size * (2 * position.entry_price - price)
        return total

    def get_pnl(self, price_data: Dict[str, float]) -> Dict[str, float]:
        """
        计算PnL

        Args:
            price_data: 当前价格数据

        Returns:
            PnL统计
        """
        # 未实现PnL
        unrealized_pnl = 0
        for symbol, position in self.positions.items():
            if symbol in price_data:
                price = price_data[symbol]
                if position.side == 'long':
                    unrealized_pnl += (price - position.entry_price) * position.size
                else:
                    unrealized_pnl += (position.entry_price - price) * position.size

        # 已实现PnL
        realized_pnl = sum(trade.pnl for trade in self.trades)

        # 总PnL
        total_pnl = realized_pnl + unrealized_pnl

        return {
            "unrealized_pnl": unrealized_pnl,
            "realized_pnl": realized_pnl,
            "total_pnl": total_pnl,
            "total_return_pct": (total_pnl / self.initial_balance) * 100
        }

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        计算性能指标

        Returns:
            性能指标
        """
        if not self.trades:
            return {
                "total_trades": 0,
                "win_rate": 0,
                "total_return": 0,
                "max_drawdown": 0
            }

        # 计算胜率
        profitable_trades = [t for t in self.trades if t.pnl > 0]
        win_rate = (len(profitable_trades)) / len(self.trades) * 100

        # 计算最大回撤
        running_max = 0
        max_drawdown = 0
        current_balance = self.balance

        # 这里简化处理，实际应该基于净值曲线计算
        for trade in self.trades:
            current_balance += trade.pnl
            running_max = max(running_max, current_balance)
            drawdown = (running_max - current_balance) / running_max * 100
            max_drawdown = max(max_drawdown, drawdown)

        return {
            "total_trades": len(self.trades),
            "win_rate": win_rate,
            "total_return": (self.balance - self.initial_balance) / self.initial_balance * 100,
            "max_drawdown": max_drawdown,
            "final_balance": self.balance
        }

    def get_positions(self) -> List[Dict[str, Any]]:
        """获取所有持仓"""
        return [pos.to_dict() for pos in self.positions.values()]

    def get_trades(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取交易记录"""
        trades = sorted(self.trades, key=lambda t: t.timestamp, reverse=True)
        return [t.to_dict() for t in trades[:limit]]

    def _save_position(self, position: Position):
        """保存持仓到数据库"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO positions
                (symbol, side, size, entry_price, entry_time, current_price,
                 unrealized_pnl, realized_pnl, stop_loss, take_profit)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                position.symbol, position.side, position.size, position.entry_price,
                position.entry_time.isoformat(), position.current_price,
                position.unrealized_pnl, position.realized_pnl,
                position.stop_loss, position.take_profit
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"保存持仓失败: {e}")

    def _save_trade(self, trade: Trade):
        """保存交易到数据库"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO trades
                (trade_id, symbol, side, size, price, timestamp, pnl, fee, reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade.trade_id, trade.symbol, trade.side, trade.size,
                trade.price, trade.timestamp.isoformat(), trade.pnl,
                trade.fee, trade.reason
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"保存交易失败: {e}")

    def _save_account_history(self):
        """保存账户历史"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO account_history
                (timestamp, balance, total_value, unrealized_pnl, realized_pnl)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                self.balance,
                self.balance,  # 简化处理
                0,  # 简化处理
                sum(t.pnl for t in self.trades)
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"保存账户历史失败: {e}")

    def export_trades(self, file_path: str):
        """导出交易记录"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.get_trades(), f, indent=2, ensure_ascii=False, default=str)

    def reset(self):
        """重置账户"""
        self.balance = self.initial_balance
        self.positions.clear()
        self.trades.clear()

        # 清空数据库
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM positions')
            cursor.execute('DELETE FROM trades')
            cursor.execute('DELETE FROM account_history')
            conn.commit()
            conn.close()
            logger.info("账户已重置")
        except Exception as e:
            logger.error(f"重置失败: {e}")

    def close(self):
        """关闭连接"""
        logger.info("纸交易执行器已关闭")
