# LLM 智能交易系统 - 实施规划

## 🎯 项目目标

基于第一步的数据获取系统，构建一个能够接收市场数据、通过 LLM 进行分析决策、并输出交易建议的智能交易系统。

## 📋 总体架构

```
┌─────────────────┐
│   数据获取层     │  ← 已完成 (第一步)
│  (DataFetcher)  │
└────────┬────────┘
         │
┌────────┴────────┐
│   数据预处理层   │  ← 新增
│  (DataPreproc)  │
└────────┬────────┘
         │
┌────────┴────────┐
│   LLM 决策层     │  ← 新增
│  (LLMTrader)    │
└────────┬────────┘
         │
┌────────┴────────┐
│   交易执行层     │  ← 新增
│ (TradeExecutor) │
└─────────────────┘
```

## 📊 模块设计

### 1. 数据预处理模块 (DataPreprocessor)

**功能**: 将原始市场数据转换为 LLM 可理解的结构化提示

**输入**:
- 来自数据库的 K 线数据
- 技术指标数据
- 永续合约数据

**处理流程**:
```python
def preprocess_data(symbol: str, timeframe: str = '3m') -> Dict:
    """
    预处理数据，生成结构化提示
    """
    # 1. 获取数据
    klines = db.get_klines(symbol, timeframe, limit=50)
    indicators = db.get_latest_indicators(symbol, timeframe)
    perp_data = db.get_latest_perp_data(symbol)

    # 2. 计算趋势和模式
    trend = analyze_trend(klines)
    patterns = detect_patterns(klines)
    momentum = calculate_momentum(indicators)

    # 3. 生成文本提示
    prompt = generate_prompt({
        'symbol': symbol,
        'current_price': klines.iloc[-1]['close'],
        'trend': trend,
        'patterns': patterns,
        'momentum': momentum,
        'technical_indicators': indicators,
        'perp_data': perp_data
    })

    return {
        'symbol': symbol,
        'prompt': prompt,
        'metadata': {...}
    }
```

**核心组件**:
- **趋势分析器** (`TrendAnalyzer`): 识别上升/下降/横盘趋势
- **模式检测器** (`PatternDetector`): 检测技术图形模式
- **动量计算器** (`MomentumCalculator`): 计算价格动量
- **提示生成器** (`PromptGenerator`): 生成结构化文本

### 2. LLM 决策引擎 (LLMTrader)

**功能**: 调用 LLM API，获取交易决策

**支持模型**:
- OpenAI GPT-4
- Anthropic Claude
- 任何兼容 OpenAI API 的模型

**决策框架**:
```python
class TradingDecision(BaseModel):
    action: Literal["BUY", "SELL", "HOLD"]
    confidence: float  # 0-100
    entry_price: Optional[float]
    stop_loss: Optional[float]
    take_profit: Optional[float]
    position_size: float  # 百分比
    reasoning: str
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    timeframe: str
```

**API 调用流程**:
```python
def get_trading_decision(prompt: str, model: str = "gpt-4") -> TradingDecision:
    """
    调用 LLM 获取交易决策
    """
    # 1. 构建系统提示
    system_prompt = build_system_prompt()

    # 2. 调用 LLM API
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        functions=[...],  # JSON Schema
        temperature=0.3
    )

    # 3. 解析响应
    decision = parse_response(response)

    # 4. 验证决策
    if not validate_decision(decision):
        raise ValueError("Invalid decision from LLM")

    return decision
```

### 3. 交易执行模块 (TradeExecutor)

**功能**: 格式化决策、执行交易（模拟或实盘）

**执行模式**:
- **模拟模式**: 仅记录决策，不实际交易
- **纸交易**: 使用模拟账户执行
- **实盘模式**: 连接交易所 API 执行真实交易

**核心逻辑**:
```python
def execute_decision(decision: TradingDecision, mode: str = "SIMULATION"):
    """
    执行交易决策
    """
    if mode == "SIMULATION":
        return simulate_trade(decision)
    elif mode == "PAPER":
        return paper_trade(decision)
    elif mode == "LIVE":
        return live_trade(decision)
```

## 🔄 实施计划 (分步进行)

### Phase 1: 数据预处理模块
**时间估算**: 2-3 天

**任务**:
1. 创建 `data_preprocessor.py`
2. 实现趋势分析器
3. 实现模式检测器
4. 实现提示生成器
5. 添加单元测试

**输出文件**:
- `data_preprocessor.py` - 主模块
- `trend_analyzer.py` - 趋势分析
- `pattern_detector.py` - 模式检测
- `prompt_generator.py` - 提示生成
- `tests/test_data_preprocessor.py` - 测试

### Phase 2: LLM 决策引擎
**时间估算**: 3-4 天

**任务**:
1. 创建 `llm_trader.py`
2. 实现 LLM API 客户端
3. 设计交易决策 JSON Schema
4. 实现决策验证逻辑
5. 添加模拟功能
6. 添加单元测试

**配置需求**:
```python
# config.py 新增
LLM_CONFIG = {
    'api_key': os.getenv('OPENAI_API_KEY'),
    'model': 'gpt-4',
    'temperature': 0.3,
    'max_tokens': 1000,
    'timeout': 30
}

TRADING_CONFIG = {
    'mode': 'SIMULATION',  # SIMULATION, PAPER, LIVE
    'max_position_size': 0.1,  # 10%
    'risk_free_rate': 0.02,
    'stop_loss_pct': 0.05,  # 5%
    'take_profit_pct': 0.10,  # 10%
}
```

**输出文件**:
- `llm_trader.py` - 主模块
- `models/trading_decision.py` - 决策模型
- `prompts/system_prompts.py` - 系统提示
- `tests/test_llm_trader.py` - 测试

### Phase 3: 交易执行模块
**时间估算**: 2-3 天

**任务**:
1. 创建 `trade_executor.py`
2. 实现模拟交易器
3. 实现纸交易器（可选）
4. 实现实盘交易器（可选）
5. 添加交易记录器
6. 添加单元测试

**输出文件**:
- `trade_executor.py` - 主模块
- `exchange_client.py` - 交易所客户端
- `trade_logger.py` - 交易记录
- `tests/test_trade_executor.py` - 测试

### Phase 4: 风险管理和回测
**时间估算**: 3-4 天

**任务**:
1. 创建 `risk_manager.py`
2. 实现仓位计算器
3. 实现止损止盈
4. 实现回测框架
5. 添加性能指标计算
6. 添加可视化报告

**输出文件**:
- `risk_manager.py` - 风险管理
- `backtest.py` - 回测框架
- `performance_metrics.py` - 性能指标
- `visualization.py` - 可视化
- `tests/test_risk_manager.py` - 测试

### Phase 5: 集成和优化
**时间估算**: 2-3 天

**任务**:
1. 集成所有模块
2. 创建统一入口 (`llm_trading_main.py`)
3. 添加配置管理
4. 性能优化
5. 添加日志系统
6. 端到端测试

**输出文件**:
- `llm_trading_main.py` - 主入口
- `config_manager.py` - 配置管理
- `logger.py` - 日志系统
- `integration_tests/` - 集成测试

## 💡 关键技术细节

### 1. 提示工程 (Prompt Engineering)

**系统提示结构**:
```
你是一个专业的量化交易员，具有丰富的加密货币交易经验。

任务：根据提供的市场数据和技术指标，给出交易决策。

数据格式：
- 当前价格: $X,XXX.XX
- 趋势: [上升/下降/横盘]
- 动量: [强/弱/中性]
- 技术指标: RSI=XX, MACD=XX, ATR=XX
- 资金费率: X.XXXX%

输出格式（JSON）:
{
  "action": "BUY|SELL|HOLD",
  "confidence": 0-100,
  "reasoning": "详细分析...",
  "entry_price": 价格,
  "stop_loss": 价格,
  "take_profit": 价格,
  "position_size": 百分比,
  "risk_level": "LOW|MEDIUM|HIGH"
}
```

### 2. 决策验证

```python
def validate_decision(decision: TradingDecision) -> bool:
    """
    验证决策合理性
    """
    # 检查必要字段
    if not decision.action:
        return False

    # 检查置信度
    if not 0 <= decision.confidence <= 100:
        return False

    # 检查价格逻辑
    if decision.stop_loss and decision.take_profit:
        if decision.stop_loss >= decision.take_profit:
            return False

    # 检查仓位大小
    if not 0 < decision.position_size <= 100:
        return False

    return True
```

### 3. 风险控制

```python
def calculate_position_size(account_balance: float, risk_pct: float,
                          entry_price: float, stop_loss: float) -> float:
    """
    基于风险计算仓位大小
    """
    risk_amount = account_balance * risk_pct
    price_risk = abs(entry_price - stop_loss)
    position_size = risk_amount / price_risk
    return position_size
```

### 4. 回测框架

```python
class Backtest:
    def __init__(self, initial_balance: float = 10000):
        self.balance = initial_balance
        self.positions = []
        self.trades = []

    def run(self, decisions: List[TradingDecision],
            market_data: pd.DataFrame) -> Dict:
        """
        运行回测
        """
        for decision in decisions:
            # 应用决策
            # 更新仓位
            # 计算PnL
            pass

        # 计算性能指标
        return {
            'total_return': ...,
            'sharpe_ratio': ...,
            'max_drawdown': ...,
            'win_rate': ...
        }
```

## 🔧 技术栈

**新增依赖**:
```python
# requirements.txt 新增
openai>=0.28.0          # OpenAI API
anthropic>=0.7.0        # Anthropic Claude API (可选)
pydantic>=2.0.0         # 数据验证
matplotlib>=3.7.0       # 可视化 (可选)
seaborn>=0.12.0         # 可视化 (可选)
```

## 📝 待讨论的问题

### 1. LLM 模型选择
- **选项 A**: OpenAI GPT-4 (最成熟，但需要付费)
- **选项 B**: Anthropic Claude (性能好，但需要付费)
- **选项 C**: 开源模型 (如 Llama 2，本地运行，免费但需要 GPU)
- **选项 D**: 多个模型集成 (提高鲁棒性)

**建议**: 先用 GPT-4 实现原型，后续可切换到开源模型

### 2. 数据频率
- **实时模式**: 每分钟调用一次 LLM
- **定期模式**: 每小时或每天调用一次
- **事件触发**: 当市场发生重大变化时调用

**建议**: 先实现定期模式 (每小时)，降低 API 成本

### 3. 执行模式
- **模拟模式**: 仅记录决策，不实际交易
- **纸交易**: 使用模拟账户执行
- **实盘**: 使用真实资金交易

**建议**: 初期只实现模拟模式，确认有效后再添加纸交易

### 4. 多时间框架融合
- **问题**: 应该基于 3 分钟数据还是 4 小时数据决策？
- **方案 A**: 单一时间框架
- **方案 B**: 多时间框架融合 (如：4h 决策方向 + 3m 决策入场)

**建议**: 初期使用单一时间框架 (4h)，后期再融合多时间框架

### 5. 记忆和上下文
- **问题**: LLM 是否需要记住历史决策？
- **方案 A**: 仅基于当前数据决策
- **方案 B**: 包含最近 N 次决策历史
- **方案 C**: 包含完整交易记录

**建议**: 初期不记录历史决策，保持简单

## 🚀 第一阶段实施 (下周开始)

**目标**: 完成数据预处理模块 + LLM 决策引擎原型

**具体任务**:
1. 创建 `data_preprocessor.py` (预计 1 天)
2. 实现 `llm_trader.py` (预计 2 天)
3. 集成测试 (预计 1 天)
4. 文档和示例 (预计 1 天)

**成功标准**:
- 能够接收市场数据
- 能够生成结构化提示
- 能够调用 LLM API
- 能够解析和验证决策
- 单元测试覆盖 > 80%

## ❓ 需要您确认的问题

1. **LLM 模型**: 您希望使用哪个 LLM 模型？建议先用 GPT-4
2. **数据频率**: 您希望多久调用一次 LLM？建议每小时一次
3. **执行模式**: 您希望先实现哪种模式？建议先做模拟模式
4. **预算**: 您是否有 LLM API 的预算？GPT-4 约 $0.03/1K tokens
5. **时间表**: 您希望何时完成第一阶段？建议一周时间

请回复您的偏好，我将根据您的选择调整实施计划！
