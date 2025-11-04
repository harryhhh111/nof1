"""
交易决策数据模型

使用dataclass实现，无需额外依赖
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class TradingDecision:
    """
    交易决策模型

    用于存储LLM生成的所有交易决策信息
    """

    # 基础决策
    action: str  # "BUY", "SELL", "HOLD"

    confidence: float  # 0-100

    # 价格信息
    entry_price: Optional[float] = None

    stop_loss: Optional[float] = None

    take_profit: Optional[float] = None

    # 仓位信息
    position_size: float = 0.0  # 0-100

    leverage: float = 1.0

    # 分析信息
    reasoning: str = ""

    timeframe: str = ""

    # 趋势和信号
    trend_analysis: Optional[str] = None

    timing_analysis: Optional[str] = None

    key_factors: Optional[List[str]] = None

    signals: Optional[List[str]] = None

    entry_trigger: Optional[str] = None

    # 风险信息
    risk_level: str = "MEDIUM"  # "LOW", "MEDIUM", "HIGH"

    risk_score: float = 50.0  # 0-100

    # 元数据
    model_source: str = ""

    timestamp: datetime = field(default_factory=datetime.now)

    symbol: Optional[str] = None

    # 决策融合相关
    fusion_summary: Optional[str] = None

    long_term_contribution: Optional[str] = None

    short_term_contribution: Optional[str] = None

    consensus_score: Optional[float] = None

    execution_timing: Optional[str] = None

    def __post_init__(self):
        """初始化后处理"""
        # 转换价格
        self.entry_price = self._convert_to_float(self.entry_price)
        self.stop_loss = self._convert_to_float(self.stop_loss)
        self.take_profit = self._convert_to_float(self.take_profit)

        # 转换百分比
        self.position_size = self._convert_to_float_or_none(self.position_size) or 0.0
        self.risk_score = self._convert_to_float_or_none(self.risk_score) or 50.0
        self.consensus_score = self._convert_to_float_or_none(self.consensus_score)

    @staticmethod
    def _convert_to_float(value) -> Optional[float]:
        """将值转换为浮点数"""
        if value is None or value == 'N/A' or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _convert_to_float_or_none(value):
        """将百分比转换为浮点数"""
        return TradingDecision._convert_to_float(value)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        import dataclasses
        return dataclasses.asdict(self)

    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TradingDecision':
        """从字典创建实例"""
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> 'TradingDecision':
        """从JSON创建实例"""
        data = json.loads(json_str)
        return cls(**data)

    def validate_decision(self) -> tuple[bool, str]:
        """
        验证决策的合理性

        Returns:
            tuple: (是否有效, 错误信息)
        """
        # 检查必要字段
        if not self.action:
            return False, "缺少交易动作"

        # 检查置信度
        if not 0 <= self.confidence <= 100:
            return False, f"置信度无效: {self.confidence}"

        # 检查价格逻辑
        if self.entry_price and self.stop_loss and self.take_profit:
            if self.action == "BUY":
                if not (self.stop_loss < self.entry_price < self.take_profit):
                    return False, "买入时止损应低于入场，入场应低于止盈"
            elif self.action == "SELL":
                if not (self.take_profit < self.entry_price < self.stop_loss):
                    return False, "卖出时止盈应低于入场，入场应低于止损"

        # 检查仓位大小
        if not 0 <= self.position_size <= 100:
            return False, f"仓位大小无效: {self.position_size}"

        # 检查风险等级
        if self.risk_level not in ["LOW", "MEDIUM", "HIGH"]:
            return False, f"风险等级无效: {self.risk_level}"

        return True, "决策有效"

    def get_risk_reward_ratio(self) -> Optional[float]:
        """计算风险回报比"""
        if not all([self.entry_price, self.stop_loss, self.take_profit]):
            return None

        if self.action == "BUY":
            risk = abs(self.entry_price - self.stop_loss)
            reward = abs(self.take_profit - self.entry_price)
        elif self.action == "SELL":
            risk = abs(self.entry_price - self.take_profit)
            reward = abs(self.stop_loss - self.entry_price)
        else:
            return None

        if risk == 0:
            return None

        return reward / risk

    def __str__(self) -> str:
        """字符串表示"""
        return (
            f"交易决策: {self.action} | "
            f"置信度: {self.confidence}% | "
            f"风险: {self.risk_level} | "
            f"仓位: {self.position_size}%"
        )


@dataclass
class DecisionMetadata:
    """决策元数据"""

    request_id: str
    model_name: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    processing_time: float
    cost: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        import dataclasses
        return dataclasses.asdict(self)

    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), default=str)


