"""
多账户配置文件

定义多个交易员的初始配置，每个交易员：
- 绑定一个LLM模型（deepseek或qwen）
- 有独立的初始资金
- 可以配置不同的交易品种
"""

import os
from typing import List, Dict, Any

# 多账户交易员配置
TRADERS_CONFIG = [
    {
        'trader_id': 'trader_deepseek_001',
        'name': 'DeepSeek账户-01',
        'llm_model': 'deepseek',
        'initial_balance': 10000.0,  # 初始资金10000U
        'api_key_env': 'DEEPSEEK_API_KEY',  # 从环境变量读取API密钥
        'symbols': ['BTCUSDT', 'ETHUSDT', 'SOLUSDT'],
        'description': '使用DeepSeek进行长期趋势分析'
    },
    {
        'trader_id': 'trader_qwen_001',
        'name': 'Qwen账户-01',
        'llm_model': 'qwen',
        'initial_balance': 10000.0,  # 初始资金10000U
        'api_key_env': 'QWEN_API_KEY',
        'symbols': ['BTCUSDT', 'ETHUSDT', 'SOLUSDT'],
        'description': '使用Qwen进行短期动量分析'
    },
    {
        'trader_id': 'trader_deepseek_002',
        'name': 'DeepSeek账户-02',
        'llm_model': 'deepseek',
        'initial_balance': 10000.0,
        'api_key_env': 'DEEPSEEK_API_KEY',
        'symbols': ['BNBUSDT', 'XRPUSDT', 'DOGEUSDT'],
        'description': 'DeepSeek山寨币专户'
    },
    {
        'trader_id': 'trader_qwen_002',
        'name': 'Qwen账户-02',
        'llm_model': 'qwen',
        'initial_balance': 10000.0,
        'api_key_env': 'QWEN_API_KEY',
        'symbols': ['BNBUSDT', 'XRPUSDT', 'DOGEUSDT'],
        'description': 'Qwen山寨币专户'
    }
]

# LLM模型配置
LLM_MODELS_CONFIG = {
    'deepseek': {
        'model_name': 'deepseek-chat',
        'temperature': 0.3,
        'max_tokens': 1500,
        'cost_per_token': 0.0002,
        'capabilities': ['trading', 'analysis', 'reasoning']
    },
    'qwen': {
        'model_name': 'qwen-turbo',
        'temperature': 0.3,
        'max_tokens': 1500,
        'cost_per_token': 0.0004,
        'capabilities': ['trading', 'analysis', 'creative']
    },
    'custom': {
        'model_name': os.getenv('CUSTOM_LLM_MODEL', 'custom-gpt-4'),
        'temperature': 0.3,
        'max_tokens': 1500,
        'cost_per_token': 0.001,
        'capabilities': ['trading', 'analysis']
    }
}

# 系统配置
SYSTEM_CONFIG = {
    'scan_interval_seconds': 300,  # 扫描间隔（5分钟）
    'max_traders': 10,  # 最大交易员数量
    'enable_paper_trading': True,  # 启用纸交易模式
    'enable_real_trading': False,  # 禁用实盘交易
    'default_leverage': 5,  # 默认杠杆
    'risk_management': {
        'max_position_size_pct': 20.0,  # 单个仓位最大占比
        'max_daily_loss_pct': 10.0,  # 最大日亏损百分比
        'max_drawdown_pct': 20.0  # 最大回撤百分比
    }
}

# 自定义交易策略模板
CUSTOM_PROMPTS = {
    'default': """
你是一个专业的加密货币量化交易员，擅长基于技术指标和市场数据做出客观决策。

=== 交易员信息 ===
名称: {trader_name}
ID: {trader_id}
使用模型: {llm_model}
当前资金: ${current_balance:.2f}
可用资金: ${available_balance:.2f}

=== 当前持仓 ===
{positions}

=== 市场数据 ===
{market_data}

=== 交易任务 ===
请基于以上信息做出交易决策。考虑以下因素：
1. 长期趋势（4小时图表）
2. 短期动量（3分钟图表）
3. 风险控制（设置止损止盈）
4. 仓位管理（不超过总资金20%）

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
""",
    'aggressive': """
你是一个激进的加密货币交易员，追求高收益，愿意承担高风险。

=== 交易员信息 ===
名称: {trader_name}
ID: {trader_id}
使用模型: {llm_model}
当前资金: ${current_balance:.2f}

=== 市场数据 ===
{market_data}

=== 交易策略 ===
- 寻找高波动性机会
- 使用较高杠杆（最高5倍）
- 仓位可达总资金30%
- 快速进出，短线为主

请返回JSON格式决策。
""",
    'conservative': """
你是一个保守的加密货币交易员，优先考虑风险控制，追求稳定收益。

=== 交易员信息 ===
名称: {trader_name}
ID: {trader_id}
使用模型: {llm_model}
当前资金: ${current_balance:.2f}

=== 交易策略 ===
- 严格风险控制
- 仓位不超过总资金10%
- 必须设置止损
- 只在明确信号时交易
- 偏好主流币种

请返回JSON格式决策。
"""
}


def get_traders_config() -> List[Dict[str, Any]]:
    """
    获取交易员配置列表

    Returns:
        List[Dict]: 交易员配置列表
    """
    return TRADERS_CONFIG


def get_llm_models_config() -> Dict[str, Dict[str, Any]]:
    """
    获取LLM模型配置

    Returns:
        Dict: LLM模型配置字典
    """
    return LLM_MODELS_CONFIG


def get_system_config() -> Dict[str, Any]:
    """
    获取系统配置

    Returns:
        Dict: 系统配置
    """
    return SYSTEM_CONFIG


def get_custom_prompts() -> Dict[str, str]:
    """
    获取自定义提示模板

    Returns:
        Dict: 提示模板字典
    """
    return CUSTOM_PROMPTS


def validate_config() -> tuple[bool, List[str]]:
    """
    验证配置的有效性

    Returns:
        tuple: (是否有效, 错误列表)
    """
    errors = []

    # 验证交易员配置
    trader_ids = set()
    for trader in TRADERS_CONFIG:
        # 检查trader_id唯一性
        if trader['trader_id'] in trader_ids:
            errors.append(f"重复的trader_id: {trader['trader_id']}")
        trader_ids.add(trader['trader_id'])

        # 检查必需字段
        required_fields = ['trader_id', 'name', 'llm_model', 'initial_balance', 'api_key_env']
        for field in required_fields:
            if field not in trader:
                errors.append(f"交易员 {trader.get('trader_id', 'unknown')} 缺少字段: {field}")

        # 检查初始资金
        if trader.get('initial_balance', 0) <= 0:
            errors.append(f"交易员 {trader['trader_id']} 初始资金必须大于0")

        # 检查LLM模型
        if trader.get('llm_model') not in LLM_MODELS_CONFIG:
            errors.append(f"交易员 {trader['trader_id']} 使用了未知的LLM模型: {trader.get('llm_model')}")

    # 验证环境变量
    for trader in TRADERS_CONFIG:
        api_key_env = trader.get('api_key_env')
        if api_key_env:
            api_key = os.getenv(api_key_env)
            if not api_key:
                errors.append(f"环境变量 {api_key_env} 未设置")

    return len(errors) == 0, errors


def print_config_summary():
    """打印配置摘要"""
    print("\n" + "="*60)
    print("多账户配置摘要")
    print("="*60)
    print(f"交易员数量: {len(TRADERS_CONFIG)}")
    print(f"LLM模型: {', '.join(LLM_MODELS_CONFIG.keys())}")
    print(f"总初始资金: ${sum(t['initial_balance'] for t in TRADERS_CONFIG):.2f}")
    print(f"扫描间隔: {SYSTEM_CONFIG['scan_interval_seconds']} 秒")
    print("="*60)

    # 显示每个交易员的信息
    print("\n交易员列表:")
    for i, trader in enumerate(TRADERS_CONFIG, 1):
        api_key_set = os.getenv(trader['api_key_env']) is not None
        print(f"{i}. {trader['name']}")
        print(f"   ID: {trader['trader_id']}")
        print(f"   LLM: {trader['llm_model']}")
        print(f"   资金: ${trader['initial_balance']:.2f}")
        print(f"   品种: {', '.join(trader['symbols'])}")
        print(f"   API Key: {'✅' if api_key_set else '❌'}")
        print()


if __name__ == '__main__':
    # 验证配置
    is_valid, errors = validate_config()

    if is_valid:
        print("✅ 配置验证通过")
        print_config_summary()
    else:
        print("❌ 配置验证失败:")
        for error in errors:
            print(f"  - {error}")
