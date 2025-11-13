"""
交易员（账户）类

表示一个独立的交易账户，每个账户绑定一个LLM模型，
拥有独立的资金、持仓和交易记录。
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class PositionSide(Enum):
    """持仓方向"""
    LONG = "long"
    SHORT = "short"


@dataclass
class Position:
    """持仓信息"""

    symbol: str
    side: PositionSide
    size: float  # 持仓数量
    entry_price: float  # 入场价格
    current_price: float  # 当前价格
    unrealized_pnl: float = 0.0  # 未实现盈亏
    realized_pnl: float = 0.0  # 已实现盈亏
    stop_loss: Optional[float] = None  # 止损价
    take_profit: Optional[float] = None  # 止盈价
    entry_time: Optional[datetime] = None  # 入场时间

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        if self.entry_time:
            data['entry_time'] = self.entry_time.isoformat()
        data['side'] = self.side.value
        return data

    def update_price(self, new_price: float):
        """更新当前价格和未实现盈亏"""
        self.current_price = new_price
        pnl_per_unit = new_price - self.entry_price
        if self.side == PositionSide.SHORT:
            pnl_per_unit = -pnl_per_unit
        self.unrealized_pnl = pnl_per_unit * self.size


@dataclass
class Trade:
    """交易记录"""

    trade_id: str
    symbol: str
    side: PositionSide
    size: float
    price: float
    timestamp: datetime
    pnl: float = 0.0
    fee: float = 0.0
    decision_id: Optional[str] = None  # 关联的决策ID

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['side'] = self.side.value
        return data


class Trader:
    """
    交易员（账户）类

    表示一个独立的交易账户，具有以下特点：
    - 绑定一个LLM模型
    - 拥有独立的资金和持仓
    - 独立计算性能指标
    """

    def __init__(
        self,
        trader_id: str,
        name: str,
        llm_model: str,
        initial_balance: float,
        llm_client: Any,  # BaseLLMClient
        symbols: Optional[List[str]] = None
    ):
        """
        初始化交易员

        Args:
            trader_id: 唯一标识
            name: 显示名称
            llm_model: LLM模型名称
            initial_balance: 初始资金
            llm_client: LLM客户端实例
            symbols: 交易品种列表
        """
        self.trader_id = trader_id
        self.name = name
        self.llm_model = llm_model
        self.initial_balance = initial_balance
        self.llm_client = llm_client
        self.symbols = symbols or []

        # 资金管理
        self.current_balance = initial_balance
        self.available_balance = initial_balance

        # 持仓管理
        self.positions: Dict[str, Position] = {}

        # 交易记录
        self.trades: List[Trade] = []

        # 性能统计
        self.total_pnl = 0.0
        self.total_pnl_pct = 0.0
        self.win_rate = 0.0
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0

        # 时间统计
        self.start_time = datetime.now()
        self.last_update_time = datetime.now()

        logger.info(f"创建交易员: {self.name} (ID: {self.trader_id}, LLM: {self.llm_model}, 初始资金: ${self.initial_balance:.2f})")

    def get_decision(self, market_data: Dict, prompt_template: Optional[str] = None) -> Any:
        """
        获取交易决策

        Args:
            market_data: 市场数据
            prompt_template: 可选的提示模板

        Returns:
            TradingDecision: 交易决策对象
        """
        try:
            # 生成提示
            prompt = self._generate_prompt(market_data, prompt_template)

            # 调用绑定的LLM
            logger.info(f"{self.name} 正在获取决策 (LLM: {self.llm_model})...")
            decision = self.llm_client.get_decision(prompt)

            # 设置决策归属信息
            decision.trader_id = self.trader_id
            decision.llm_model = self.llm_model
            decision.timestamp = datetime.now().isoformat()

            logger.info(f"{self.name} 决策完成: {decision.action} "
                       f"(置信度: {decision.confidence}%, LLM: {self.llm_model})")

            return decision

        except Exception as e:
            logger.error(f"{self.name} 获取决策失败: {e}")
            # 返回默认HOLD决策
            return self._create_default_decision(str(e))

    def execute_decision(self, decision: Any, current_price: float) -> Dict[str, Any]:
        """
        执行交易决策（在独立账户中）

        Args:
            decision: 交易决策
            current_price: 当前价格（用于验证）

        Returns:
            Dict: 执行结果
        """
        try:
            if decision.action == "HOLD":
                return {
                    'status': 'hold',
                    'message': f"{self.name}: 维持现状",
                    'trader_id': self.trader_id
                }

            # 执行开仓或平仓
            if decision.action in ["BUY", "SELL"]:
                return self._open_position(decision, current_price)
            elif decision.action == "CLOSE":
                return self._close_position(decision.symbol, current_price)
            else:
                return {
                    'status': 'error',
                    'message': f"未知操作: {decision.action}",
                    'trader_id': self.trader_id
                }

        except Exception as e:
            logger.error(f"{self.name} 执行决策失败: {e}")
            return {
                'status': 'error',
                'message': f"执行失败: {str(e)}",
                'trader_id': self.trader_id
            }

    def _open_position(self, decision: Any, current_price: float) -> Dict[str, Any]:
        """
        开仓

        Args:
            decision: 交易决策
            current_price: 当前价格

        Returns:
            Dict: 执行结果
        """
        symbol = decision.symbol
        action = decision.action
        position_size = decision.position_size  # 百分比（0-100）
        stop_loss = decision.stop_loss
        take_profit = decision.take_profit

        # 计算仓位大小（基于可用资金）
        position_value = self.current_balance * (position_size / 100.0)
        quantity = position_value / current_price

        # 确定持仓方向
        side = PositionSide.LONG if action == "BUY" else PositionSide.SHORT

        # 检查是否已有持仓
        if symbol in self.positions:
            existing_pos = self.positions[symbol]
            # 如果方向相同，增加仓位
            if existing_pos.side == side:
                # 计算新的平均入场价
                total_size = existing_pos.size + quantity
                new_entry_price = (
                    existing_pos.entry_price * existing_pos.size +
                    current_price * quantity
                ) / total_size
                existing_pos.size = total_size
                existing_pos.entry_price = new_entry_price
                existing_pos.update_price(current_price)
            else:
                # 方向相反，先平旧仓，再开新仓
                self._close_position(symbol, current_price)
                return self._open_position(decision, current_price)

        else:
            # 创建新持仓
            self.positions[symbol] = Position(
                symbol=symbol,
                side=side,
                size=quantity,
                entry_price=current_price,
                current_price=current_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                entry_time=datetime.now()
            )

        # 更新资金
        self.available_balance -= position_value

        # 记录交易
        trade = Trade(
            trade_id=f"{self.trader_id}_{symbol}_{int(datetime.now().timestamp())}",
            symbol=symbol,
            side=side,
            size=quantity,
            price=current_price,
            timestamp=datetime.now(),
            decision_id=getattr(decision, 'id', None)
        )
        self.trades.append(trade)
        self.total_trades += 1

        # 更新性能统计
        self._update_performance()

        logger.info(f"{self.name} 开仓成功: {symbol} {side.value} "
                   f"{quantity:.6f} @ ${current_price:.2f}")

        return {
            'status': 'success',
            'action': 'open',
            'symbol': symbol,
            'side': side.value,
            'size': quantity,
            'price': current_price,
            'trader_id': self.trader_id
        }

    def _close_position(self, symbol: str, current_price: float) -> Dict[str, Any]:
        """
        平仓

        Args:
            symbol: 交易对
            current_price: 当前价格

        Returns:
            Dict: 执行结果
        """
        if symbol not in self.positions:
            return {
                'status': 'error',
                'message': f"无持仓: {symbol}",
                'trader_id': self.trader_id
            }

        position = self.positions[symbol]
        position.update_price(current_price)

        # 计算平仓价值
        close_value = position.size * current_price

        # 更新资金
        self.current_balance += close_value + position.unrealized_pnl
        self.available_balance += close_value

        # 记录交易
        trade = Trade(
            trade_id=f"{self.trader_id}_{symbol}_close_{int(datetime.now().timestamp())}",
            symbol=symbol,
            side=PositionSide.LONG if position.side == PositionSide.SHORT else PositionSide.SHORT,
            size=position.size,
            price=current_price,
            timestamp=datetime.now(),
            pnl=position.unrealized_pnl
        )
        self.trades.append(trade)

        # 更新胜负统计
        if position.unrealized_pnl > 0:
            self.winning_trades += 1
        else:
            self.losing_trades += 1

        # 移除持仓
        del self.positions[symbol]

        # 更新性能统计
        self.total_pnl += position.unrealized_pnl
        self._update_performance()

        logger.info(f"{self.name} 平仓成功: {symbol} "
                   f"PnL: ${position.unrealized_pnl:.2f}")

        return {
            'status': 'success',
            'action': 'close',
            'symbol': symbol,
            'pnl': position.unrealized_pnl,
            'trader_id': self.trader_id
        }

    def _generate_prompt(self, market_data: Dict, prompt_template: Optional[str] = None) -> str:
        """
        生成交易提示

        Args:
            market_data: 市场数据
            prompt_template: 可选的提示模板

        Returns:
            str: 提示字符串
        """
        if prompt_template:
            return prompt_template.format(
                trader_name=self.name,
                trader_id=self.trader_id,
                llm_model=self.llm_model,
                current_balance=self.current_balance,
                available_balance=self.available_balance,
                market_data=json.dumps(market_data, indent=2, ensure_ascii=False)
            )

        # 默认提示模板
        prompt = f"""
你是一个专业的加密货币量化交易员。

=== 交易员信息 ===
名称: {self.name}
ID: {self.trader_id}
使用模型: {self.llm_model}
当前资金: ${self.current_balance:.2f}
可用资金: ${self.available_balance:.2f}

=== 当前持仓 ===
{self._format_positions()}

=== 市场数据 ===
{json.dumps(market_data, indent=2, ensure_ascii=False)}

=== 交易任务 ===
请基于以上信息做出交易决策。

请以JSON格式返回决策：
{{
  "action": "BUY|SELL|HOLD|CLOSE",
  "symbol": "交易对",
  "position_size": 0-100,
  "confidence": 0-100,
  "reasoning": "详细分析",
  "entry_price": 价格,
  "stop_loss": 价格,
  "take_profit": 价格
}}
"""
        return prompt

    def _format_positions(self) -> str:
        """格式化持仓信息"""
        if not self.positions:
            return "无持仓"

        lines = []
        for symbol, pos in self.positions.items():
            lines.append(
                f"{symbol}: {pos.side.value} "
                f"{pos.size:.6f} @ ${pos.entry_price:.2f} "
                f"PnL: ${pos.unrealized_pnl:.2f}"
            )
        return "\n".join(lines)

    def _create_default_decision(self, reason: str) -> Any:
        """创建默认的HOLD决策"""
        class DefaultDecision:
            def __init__(self, reason):
                self.action = "HOLD"
                self.symbol = ""
                self.position_size = 0
                self.confidence = 0
                self.reasoning = f"决策失败: {reason}"
                self.entry_price = 0
                self.stop_loss = 0
                self.take_profit = 0
                self.trader_id = self.trader_id
                self.llm_model = self.llm_model
                self.timestamp = datetime.now().isoformat()

        return DefaultDecision(reason)

    def _update_performance(self):
        """更新性能统计"""
        # 计算总盈亏百分比
        self.total_pnl_pct = (self.total_pnl / self.initial_balance) * 100

        # 计算胜率
        if self.total_trades > 0:
            self.win_rate = (self.winning_trades / self.total_trades) * 100

        # 更新时间
        self.last_update_time = datetime.now()

    def get_positions(self) -> List[Dict[str, Any]]:
        """
        获取所有持仓

        Returns:
            List[Dict]: 持仓列表
        """
        return [pos.to_dict() for pos in self.positions.values()]

    def get_performance(self) -> Dict[str, Any]:
        """
        获取性能指标

        Returns:
            Dict: 性能指标
        """
        runtime_minutes = (datetime.now() - self.start_time).total_seconds() / 60

        return {
            'trader_id': self.trader_id,
            'name': self.name,
            'llm_model': self.llm_model,
            'initial_balance': self.initial_balance,
            'current_balance': self.current_balance,
            'total_pnl': self.total_pnl,
            'total_pnl_pct': self.total_pnl_pct,
            'win_rate': self.win_rate,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'runtime_minutes': runtime_minutes,
            'positions_count': len(self.positions),
            'last_update_time': self.last_update_time.isoformat()
        }

    def get_summary(self) -> str:
        """
        获取账户摘要

        Returns:
            str: 格式化的摘要信息
        """
        perf = self.get_performance()
        return f"""
{'='*60}
{self.name} ({self.trader_id})
{'='*60}
LLM模型: {self.llm_model}
初始资金: ${self.initial_balance:.2f}
当前资金: ${self.current_balance:.2f}
总盈亏: ${self.total_pnl:.2f} ({self.total_pnl_pct:+.2f}%)
胜率: {self.win_rate:.1f}%
交易次数: {self.total_trades}
持仓数: {len(self.positions)}
运行时间: {perf['runtime_minutes']:.0f} 分钟
{'='*60}
""".strip()

    def __repr__(self) -> str:
        return f"Trader(id={self.trader_id}, name={self.name}, llm={self.llm_model}, balance=${self.current_balance:.2f})"
