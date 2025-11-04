"""
提示生成器

将多时间框架数据转换为 LLM 可理解的提示
"""

from typing import Dict
import json


class PromptGenerator:
    """提示生成器"""

    def __init__(self):
        """初始化提示生成器"""
        self.system_prompt = self._get_system_prompt()

    def generate_4h_prompt(self, data_4h: Dict, data_3m: Dict) -> str:
        """
        生成4小时趋势分析提示

        Args:
            data_4h: 4小时数据
            data_3m: 3分钟数据

        Returns:
            结构化提示字符串
        """
        prompt = f"""
你是一个专业的加密货币量化交易员，擅长基于多时间框架数据分析进行长期趋势判断。

当前分析交易对：{data_4h['symbol']}

=== 4小时长期趋势分析 ===
{data_4h.get('description', '无数据')}

=== 3分钟短期背景 ===
{data_3m.get('description', '无数据')}

=== 交易任务 ===
请基于以上数据进行长期趋势判断，给出交易建议。

请以JSON格式返回决策：
{{
  "action": "BUY|SELL|HOLD",
  "confidence": 0-100,
  "reasoning": "详细分析",
  "entry_price": 价格,
  "stop_loss": 价格,
  "take_profit": 价格,
  "position_size": 百分比,
  "risk_level": "LOW|MEDIUM|HIGH",
  "timeframe": "4h",
  "trend_analysis": "长期趋势分析",
  "key_factors": ["关键因素1", "关键因素2"]
}}
"""
        return prompt

    def generate_3m_prompt(self, data_3m: Dict) -> str:
        """
        生成3分钟短期入场提示

        Args:
            data_3m: 3分钟数据

        Returns:
            结构化提示字符串
        """
        prompt = f"""
你是一个专业的加密货币日内交易员，擅长基于短期数据进行精确入场时机判断。

当前分析交易对：{data_3m['symbol']}

=== 3分钟短期分析 ===
{data_3m.get('description', '无数据')}

=== 交易任务 ===
请基于以上短期数据进行入场时机判断，给出交易建议。

请以JSON格式返回决策：
{{
  "action": "BUY|SELL|HOLD",
  "confidence": 0-100,
  "reasoning": "详细分析",
  "entry_price": 价格,
  "stop_loss": 价格,
  "take_profit": 价格,
  "position_size": 百分比,
  "risk_level": "LOW|MEDIUM|HIGH",
  "timeframe": "3m",
  "timing_analysis": "入场时机分析",
  "signals": ["信号1", "信号2"],
  "entry_trigger": "触发条件"
}}
"""
        return prompt

    def generate_fusion_prompt(self, long_term: Dict, short_term: Dict) -> str:
        """
        生成决策融合提示

        Args:
            long_term: 长期决策
            short_term: 短期决策

        Returns:
            融合提示字符串
        """
        prompt = f"""
你是一个专业的交易决策融合专家，负责综合长期趋势和短期时机，给出最终交易决策。

=== 长期决策（4小时） ===
行动：{long_term.get('action')}
置信度：{long_term.get('confidence')}
分析：{long_term.get('reasoning')}

=== 短期决策（3分钟） ===
行动：{short_term.get('action')}
置信度：{short_term.get('confidence')}
分析：{short_term.get('reasoning')}

=== 融合任务 ===
请综合长期趋势和短期时机，给出最终决策。

融合规则：
- 如果长期和短期方向一致 → 采纳该方向
- 如果方向相反 → HOLD（观望）
- 权重分配：长期70%，短期30%
- 考虑置信度加权平均

请以JSON格式返回最终决策：
{{
  "action": "BUY|SELL|HOLD",
  "confidence": 0-100,
  "final_reasoning": "最终决策分析",
  "entry_price": 价格,
  "stop_loss": 价格,
  "take_profit": 价格,
  "position_size": 百分比,
  "risk_level": "LOW|MEDIUM|HIGH",
  "fusion_summary": "融合决策总结",
  "long_term_contribution": "长期决策贡献度",
  "short_term_contribution": "短期决策贡献度",
  "consensus_score": 0-100,
  "execution_timing": "执行时机建议"
}}
"""
        return prompt

    def _get_system_prompt(self) -> str:
        """获取系统提示"""
        return """
你是一个专业的加密货币量化交易员，具有以下能力：

1. 技术分析专家
   - 精通各类技术指标（RSI, MACD, EMA, ATR等）
   - 能够识别趋势、支撑阻力位、图形模式
   - 熟练进行多时间框架分析

2. 风险管理专家
   - 严格的风险控制
   - 合理的仓位管理
   - 科学的止损止盈设置

3. 决策制定专家
   - 基于数据的客观决策
   - 平衡收益和风险
   - 适应市场变化

你必须始终遵循以下原则：
- 严格的风险控制，单个交易风险不超过账户的2%
- 只在有明确信号时入场
- 始终设置止损位
- 保持客观，不受情绪影响
- 遵循交易计划，不随意改变

请基于提供的数据进行分析，给出专业的交易建议。
        """.strip()

    def format_decision_for_output(self, decision: Dict) -> str:
        """格式化决策为可读输出"""
        if not decision:
            return "无效决策"

        output = f"""
=== 交易决策 ===
交易对：{decision.get('symbol', 'N/A')}
行动：{decision.get('action', 'N/A')}
置信度：{decision.get('confidence', 0)}%
风险等级：{decision.get('risk_level', 'N/A')}

入场价格：${decision.get('entry_price', 'N/A')}
止损价格：${decision.get('stop_loss', 'N/A')}
止盈价格：${decision.get('take_profit', 'N/A')}
仓位大小：{decision.get('position_size', 0)}%

分析：{decision.get('reasoning', 'N/A')}

时间框架：{decision.get('timeframe', 'N/A')}
        """.strip()

        return output


if __name__ == '__main__':
    # 测试代码
    generator = PromptGenerator()

    # 模拟数据
    data_4h = {
        'symbol': 'BTCUSDT',
        'description': '测试4h数据',
        'trend': 'UP',
        'confidence': 80
    }

    data_3m = {
        'symbol': 'BTCUSDT',
        'description': '测试3m数据',
        'momentum': 'POSITIVE',
        'confidence': 75
    }

    long_term = {
        'action': 'BUY',
        'confidence': 80,
        'reasoning': '长期上升趋势'
    }

    short_term = {
        'action': 'BUY',
        'confidence': 75,
        'reasoning': '短期动量向上'
    }

    # 生成提示
    prompt_4h = generator.generate_4h_prompt(data_4h, data_3m)
    prompt_3m = generator.generate_3m_prompt(data_3m)
    prompt_fusion = generator.generate_fusion_prompt(long_term, short_term)

    print("4H提示:")
    print(prompt_4h)
    print("\n" + "="*50 + "\n")
    print("3M提示:")
    print(prompt_3m)
    print("\n" + "="*50 + "\n")
    print("融合提示:")
    print(prompt_fusion)
