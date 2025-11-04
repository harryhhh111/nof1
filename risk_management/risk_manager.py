"""
风险管理模块

实现交易决策的风险评估和控制
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from datetime import datetime, timedelta

from models.trading_decision import TradingDecision


@dataclass
class RiskMetrics:
    """风险指标"""

    symbol: str
    position_size_pct: float
    leverage: float
    var_1d: float  # 1天VaR
    var_5d: float  # 5天VaR
    sharpe_ratio: float
    max_drawdown: float
    volatility: float
    correlation_risk: float
    liquidity_risk: float
    risk_score: int  # 0-100
    risk_level: str  # LOW, MEDIUM, HIGH

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'symbol': self.symbol,
            'position_size_pct': self.position_size_pct,
            'leverage': self.leverage,
            'var_1d': self.var_1d,
            'var_5d': self.var_5d,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'volatility': self.volatility,
            'correlation_risk': self.correlation_risk,
            'liquidity_risk': self.liquidity_risk,
            'risk_score': self.risk_score,
            'risk_level': self.risk_level
        }


class RiskManager:
    """
    风险管理器

    功能：
    - 评估交易决策的风险
    - 计算风险指标
    - 建议合理的仓位大小
    - 检查风险限制
    """

    def __init__(
        self,
        account_balance: float,
        max_position_size: float = 0.1,  # 单个资产最大仓位10%
        max_leverage: float = 10.0,
        max_portfolio_risk: float = 0.02,  # 组合最大风险2%
        max_correlation: float = 0.7  # 最大相关性70%
    ):
        """
        初始化风险管理器

        Args:
            account_balance: 账户余额
            max_position_size: 单个资产最大仓位比例
            max_leverage: 最大杠杆
            max_portfolio_risk: 组合最大风险
            max_correlation: 最大相关性
        """
        self.account_balance = account_balance
        self.max_position_size = max_position_size
        self.max_leverage = max_leverage
        self.max_portfolio_risk = max_portfolio_risk
        self.max_correlation = max_correlation

        # 历史数据（简化版本）
        self.price_history: Dict[str, List[float]] = {}
        self.positions: Dict[str, Dict] = {}  # symbol -> position_info

    def evaluate_decision(
        self,
        decision: TradingDecision,
        current_positions: Dict[str, Dict],
        price_data: Dict[str, float]
    ) -> Tuple[bool, str, Optional[float]]:
        """
        评估交易决策

        Args:
            decision: 交易决策
            current_positions: 当前持仓
            price_data: 当前价格数据

        Returns:
            (是否通过评估, 错误信息, 建议仓位大小)
        """
        # 1. 检查决策有效性
        is_valid, msg = decision.validate_decision()
        if not is_valid:
            return False, f"决策无效: {msg}", None

        # 2. 检查仓位大小
        max_position_value = self.account_balance * self.max_position_size

        # 直接检查决策中的仓位比例是否超过限制
        if decision.position_size / 100.0 > self.max_position_size:
            return False, f"仓位过大: {decision.position_size}% > {self.max_position_size*100:.0f}%", None

        suggested_size = self._calculate_position_size(
            decision, price_data.get(decision.symbol, 0)
        )

        if suggested_size is None or suggested_size > max_position_value:
            return False, f"建议仓位过大: ${suggested_size:.2f} > ${max_position_value:.2f}", None

        # 3. 检查杠杆
        if decision.leverage > self.max_leverage:
            return False, f"杠杆过高: {decision.leverage}x > {self.max_leverage}x", None

        # 4. 检查组合风险
        portfolio_risk = self._calculate_portfolio_risk(current_positions, price_data)
        if portfolio_risk > self.max_portfolio_risk:
            return False, f"组合风险过高: {portfolio_risk*100:.2f}% > {self.max_portfolio_risk*100:.2f}%", None

        # 5. 检查相关性
        if decision.symbol in current_positions:
            correlation = self._calculate_correlation(decision.symbol, price_data)
            if correlation > self.max_correlation:
                return False, f"相关性过高: {correlation:.2f} > {self.max_correlation:.2f}", None

        return True, "通过风险评估", suggested_size

    def calculate_risk_metrics(
        self,
        symbol: str,
        position_size_pct: float,
        leverage: float,
        price_history: List[float]
    ) -> RiskMetrics:
        """
        计算风险指标

        Args:
            symbol: 交易对
            position_size_pct: 仓位比例
            leverage: 杠杆
            price_history: 价格历史

        Returns:
            风险指标
        """
        if len(price_history) < 30:
            # 数据不足，返回默认值
            return RiskMetrics(
                symbol=symbol,
                position_size_pct=position_size_pct,
                leverage=leverage,
                var_1d=0.0,
                var_5d=0.0,
                sharpe_ratio=0.0,
                max_drawdown=0.0,
                volatility=0.0,
                correlation_risk=0.0,
                liquidity_risk=0.0,
                risk_score=50,
                risk_level="MEDIUM"
            )

        # 计算收益率
        returns = np.diff(price_history) / price_history[:-1]

        # 计算VaR
        var_1d = self._calculate_var(returns, 0.05) * np.sqrt(1)  # 1天
        var_5d = self._calculate_var(returns, 0.05) * np.sqrt(5)  # 5天

        # 计算夏普比率
        sharpe_ratio = self._calculate_sharpe(returns)

        # 计算最大回撤
        max_drawdown = self._calculate_max_drawdown(price_history)

        # 计算波动率
        volatility = np.std(returns) * np.sqrt(365) * 100  # 年化波动率

        # 计算相关性风险（简化）
        correlation_risk = min(volatility / 100, 1.0)

        # 计算流动性风险（简化）
        liquidity_risk = 0.1  # 假设所有资产流动性风险为10%

        # 综合风险评分
        risk_score = self._calculate_risk_score(
            var_1d, volatility, max_drawdown, position_size_pct, leverage
        )

        # 确定风险等级
        if risk_score < 30:
            risk_level = "LOW"
        elif risk_score < 70:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"

        return RiskMetrics(
            symbol=symbol,
            position_size_pct=position_size_pct,
            leverage=leverage,
            var_1d=var_1d,
            var_5d=var_5d,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            volatility=volatility,
            correlation_risk=correlation_risk,
            liquidity_risk=liquidity_risk,
            risk_score=risk_score,
            risk_level=risk_level
        )

    def _calculate_var(self, returns: np.ndarray, confidence_level: float) -> float:
        """
        计算VaR (Value at Risk)

        Args:
            returns: 收益率序列
            confidence_level: 置信水平

        Returns:
            VaR值
        """
        return np.percentile(returns, confidence_level * 100)

    def _calculate_sharpe(self, returns: np.ndarray, risk_free_rate: float = 0.02) -> float:
        """
        计算夏普比率

        Args:
            returns: 收益率序列
            risk_free_rate: 无风险利率

        Returns:
            夏普比率
        """
        if len(returns) == 0 or np.std(returns) == 0:
            return 0.0

        excess_returns = np.mean(returns) * 365 - risk_free_rate  # 年化超额收益
        return excess_returns / (np.std(returns) * np.sqrt(365))

    def _calculate_max_drawdown(self, prices: List[float]) -> float:
        """
        计算最大回撤

        Args:
            prices: 价格序列

        Returns:
            最大回撤比例
        """
        if len(prices) < 2:
            return 0.0

        peak = prices[0]
        max_dd = 0.0

        for price in prices:
            if price > peak:
                peak = price
            dd = (peak - price) / peak
            max_dd = max(max_dd, dd)

        return max_dd

    def _calculate_risk_score(
        self,
        var_1d: float,
        volatility: float,
        max_drawdown: float,
        position_size_pct: float,
        leverage: float
    ) -> int:
        """
        计算综合风险评分 (0-100)

        Args:
            var_1d: 1天VaR
            volatility: 波动率
            max_drawdown: 最大回撤
            position_size_pct: 仓位比例
            leverage: 杠杆

        Returns:
            风险评分
        """
        # VaR风险 (0-30分)
        var_risk = min(abs(var_1d) * 1000, 30)

        # 波动率风险 (0-25分)
        vol_risk = min(volatility / 2, 25)

        # 回撤风险 (0-25分)
        dd_risk = min(max_drawdown * 100, 25)

        # 仓位风险 (0-10分)
        position_risk = min(position_size_pct, 10)

        # 杠杆风险 (0-10分)
        leverage_risk = min(leverage, 10)

        total_risk = int(var_risk + vol_risk + dd_risk + position_risk + leverage_risk)

        return min(total_risk, 100)

    def _calculate_position_size(
        self,
        decision: TradingDecision,
        current_price: float
    ) -> Optional[float]:
        """
        计算建议仓位大小

        Args:
            decision: 交易决策
            current_price: 当前价格

        Returns:
            仓位大小（美元）
        """
        # Kelly公式简化版本
        if decision.action == "HOLD" or decision.confidence < 50:
            return 0.0

        if not decision.entry_price:
            return None

        # 基于置信度计算仓位
        confidence_factor = decision.confidence / 100.0

        # 基于风险等级调整
        risk_factors = {
            "LOW": 1.0,
            "MEDIUM": 0.7,
            "HIGH": 0.4
        }
        risk_factor = risk_factors.get(decision.risk_level, 0.7)

        # 计算仓位比例
        position_pct = min(confidence_factor * risk_factor * self.max_position_size, self.max_position_size)

        # 转换为金额
        position_value = self.account_balance * position_pct

        return position_value

    def _calculate_portfolio_risk(
        self,
        positions: Dict[str, Dict],
        price_data: Dict[str, float]
    ) -> float:
        """
        计算组合风险

        Args:
            positions: 持仓信息
            price_data: 价格数据

        Returns:
            组合风险
        """
        if not positions:
            return 0.0

        # 简化计算：假设所有持仓独立
        total_risk = 0.0
        total_value = 0.0

        for symbol, position in positions.items():
            if symbol in price_data:
                position_value = position.get('size', 0) * price_data[symbol]
                total_value += position_value

                # 假设波动率为2%（简化）
                position_risk = position_value * 0.02
                total_risk += position_risk ** 2  # 平方和（独立假设）

        if total_value == 0:
            return 0.0

        # 组合标准差
        portfolio_volatility = np.sqrt(total_risk) / total_value

        return portfolio_volatility

    def _calculate_correlation(self, symbol: str, price_data: Dict[str, float]) -> float:
        """
        计算相关性（简化版本）

        Args:
            symbol: 交易对
            price_data: 价格数据

        Returns:
            相关性
        """
        # 简化实现：假设所有资产与BTC相关性为0.8
        if symbol == "BTCUSDT":
            return 1.0
        else:
            return 0.8

    def get_risk_summary(self, positions: Dict[str, Dict], price_data: Dict[str, float]) -> Dict:
        """
        获取风险摘要

        Args:
            positions: 持仓信息
            price_data: 价格数据

        Returns:
            风险摘要
        """
        portfolio_risk = self._calculate_portfolio_risk(positions, price_data)
        total_value = sum(
            pos.get('size', 0) * price_data.get(symbol, 0)
            for symbol, pos in positions.items()
            if symbol in price_data
        )

        utilization = total_value / self.account_balance if self.account_balance > 0 else 0

        return {
            'portfolio_risk': portfolio_risk,
            'total_value': total_value,
            'utilization': utilization,
            'max_position_size': self.max_position_size,
            'max_leverage': self.max_leverage,
            'risk_limit': self.max_portfolio_risk
        }


class PositionSizer:
    """
    仓位大小计算器

    基于风险和置信度计算最优仓位大小
    """

    def __init__(self, risk_manager: RiskManager):
        self.risk_manager = risk_manager

    def calculate_position_size(
        self,
        decision: TradingDecision,
        current_price: float,
        account_balance: float,
        price_history: Optional[List[float]] = None
    ) -> float:
        """
        计算最优仓位大小

        Args:
            decision: 交易决策
            current_price: 当前价格
            account_balance: 账户余额
            price_history: 价格历史（可选）

        Returns:
            建议仓位大小（美元）
        """
        # 方法1: 基于风险评分
        if price_history and len(price_history) > 30:
            metrics = self.risk_manager.calculate_risk_metrics(
                decision.symbol,
                decision.position_size,
                decision.leverage,
                price_history
            )
            risk_adjustment = 1.0 - (metrics.risk_score / 100.0)
        else:
            risk_adjustment = 1.0

        # 方法2: 基于置信度
        confidence_adjustment = decision.confidence / 100.0

        # 方法3: 基于风险等级
        risk_level_adjustments = {
            "LOW": 1.0,
            "MEDIUM": 0.7,
            "HIGH": 0.4
        }
        risk_level_adjustment = risk_level_adjustments.get(decision.risk_level, 0.7)

        # 综合调整
        total_adjustment = risk_adjustment * confidence_adjustment * risk_level_adjustment

        # 计算仓位大小
        position_size = account_balance * decision.position_size / 100.0 * total_adjustment

        return max(0.0, position_size)
