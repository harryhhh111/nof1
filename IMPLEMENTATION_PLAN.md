# LLM 智能交易系统 - 详细实施计划

## 🎯 根据您的偏好调整的方案

**您的选择**:
- ✅ **LLM模型**: DeepSeek + Qwen3 (国产模型，性价比高)
- ✅ **数据频率**: 每 5 分钟调用一次 (高频决策)
- ✅ **执行模式**: 纸交易模式 (模拟账户执行)
- ✅ **时间框架**: 多时间框架融合 (4h定方向 + 3m定入场)

## 🏗️ 系统架构 (针对高频交易优化)

```
┌─────────────────────────────────────────────────────────┐
│                 高频决策调度器 (5分钟)                     │
│               (HighFreqScheduler)                        │
└────────────────────┬────────────────────────────────────┘
                     │
    ┌────────────────┴────────────────┐
    ▼                                 ▼
┌──────────────────┐         ┌──────────────────┐
│  4小时数据通道    │         │  3分钟数据通道    │
│ (长期趋势判断)    │         │ (短期入场时机)   │
└────────┬─────────┘         └────────┬─────────┘
         │                            │
    ┌────┴────┐                 ┌────┴────┐
    ▼         ▼                 ▼         ▼
┌─────────┐ ┌──────────┐   ┌─────────┐ ┌──────────┐
│趋势分析 │ │提示生成器│   │动量分析 │ │提示生成器│
└─────────┘ └──────────┘   └─────────┘ └──────────┘
         │                            │
         └────────┬───────────────────┘
                  ▼
          ┌─────────────────────┐
          │  决策融合引擎        │
          │ (DecisionFusion)    │
          └──────────┬──────────┘
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
    ┌──────────┐        ┌──────────┐
    │DeepSeek  │        │ Qwen3    │
    │   API    │        │   API    │
    └──────────┘        └──────────┘
          │                     │
          └──────────┬──────────┘
                     ▼
            ┌───────────────────┐
            │   决策融合器       │
            │ (Vote/Weight)     │
            └──────────┬─────────┘
                       │
                       ▼
            ┌───────────────────┐
            │  纸交易执行器      │
            │ (PaperTrader)     │
            └───────────────────┘
```

## 📋 实施阶段 (7 个阶段)

### 阶段 1: 多时间框架数据预处理 (3 天)

**目标**: 实现 4h 和 3m 数据的独立处理和特征提取

**核心模块**:
1. **multi_timeframe_preprocessor.py** - 多时间框架数据处理器
2. **trend_analyzer_4h.py** - 4 小时趋势分析器
3. **momentum_analyzer_3m.py** - 3 分钟动量分析器
4. **feature_extractor.py** - 特征提取器

**关键功能**:
```python
class MultiTimeframeProcessor:
    def process_4h_data(self, symbol: str) -> Dict:
        """
        处理4小时数据，提取长期趋势特征
        - 趋势方向 (上升/下降/横盘)
        - 趋势强度 (弱/中/强)
        - 支撑/阻力位
        - 长期动量
        """
        pass

    def process_3m_data(self, symbol: str) -> Dict:
        """
        处理3分钟数据，提取短期入场特征
        - 短期动量
        - 突破信号
        - 超买/超卖
        - 微趋势
        """
        pass
```

### 阶段 2: LLM 客户端实现 (3 天)

**目标**: 实现 DeepSeek 和 Qwen3 的 API 客户端

**核心模块**:
1. **llm_clients.py** - LLM 客户端工厂
2. **deepseek_client.py** - DeepSeek API 客户端
3. **qwen_client.py** - Qwen API 客户端

**关键功能**:
```python
class DeepSeekClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1"

    async def get_decision(self, prompt: str) -> TradingDecision:
        """
        调用DeepSeek API获取交易决策
        """
        response = await self.chat_completion(
            model="deepseek-chat",
            messages=[...],
            functions=[trading_decision_schema]
        )
        return parse_decision(response)

class QwenClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://dashscope.aliyuncs.com/api/v1"

    async def get_decision(self, prompt: str) -> TradingDecision:
        """
        调用Qwen API获取交易决策
        """
        pass
```

### 阶段 3: 决策融合引擎 (2 天)

**目标**: 实现多时间框架决策的融合逻辑

**核心模块**:
1. **decision_fusion.py** - 决策融合引擎
2. **decision_validator.py** - 决策验证器

**融合策略**:
```python
class DecisionFusion:
    def fuse_decisions(self,
                      long_term_decision: TradingDecision,
                      short_term_decision: TradingDecision) -> TradingDecision:
        """
        融合长期和短期决策
        规则:
        - 如果长期和短期方向一致 → 采用该方向
        - 如果方向相反 → HOLD (等待)
        - 权重: 长期(70%) + 短期(30%)
        """
        pass

    def vote_decisions(self,
                      decisions: List[TradingDecision],
                      weights: List[float]) -> TradingDecision:
        """
        多模型投票融合
        """
        pass
```

### 阶段 4: 纸交易执行器 (3 天)

**目标**: 实现纸交易模式 (模拟账户执行)

**核心模块**:
1. **paper_trader.py** - 纸交易执行器
2. **position_manager.py** - 仓位管理器
3. **portfolio.py** - 投资组合管理

**功能**:
```python
class PaperTrader:
    def __init__(self, initial_balance: float = 100000):
        self.balance = initial_balance
        self.positions = {}  # symbol -> position
        self.trades = []     # trade history
        self.portfolio_value = initial_balance

    async def execute_decision(self, decision: TradingDecision):
        """
        执行交易决策 (纸交易)
        - 检查余额
        - 计算仓位
        - 更新持仓
        - 记录交易
        """
        pass

    def calculate_pnl(self) -> Dict:
        """
        计算PnL
        - 已实现PnL
        - 未实现PnL
        - 总回报
        """
        pass
```

### 阶段 5: 高频决策调度器 (2 天)

**目标**: 实现每 5 分钟的定时决策

**核心模块**:
1. **high_freq_scheduler.py** - 高频调度器
2. **decision_cache.py** - 决策缓存 (防止重复决策)

**关键逻辑**:
```python
class HighFreqScheduler:
    def __init__(self):
        self.interval = 300  # 5分钟 = 300秒
        self.is_running = False
        self.decision_cache = DecisionCache(ttl=600)  # 10分钟缓存

    async def start(self):
        """
        启动高频决策调度
        每5分钟执行一次:
        1. 获取多时间框架数据
        2. 预处理特征
        3. 生成提示
        4. 调用LLM (并行)
        5. 融合决策
        6. 执行纸交易
        """
        while self.is_running:
            try:
                # 检查缓存
                if self.decision_cache.is_valid():
                    await asyncio.sleep(10)
                    continue

                # 并行获取决策
                tasks = [
                    self.get_long_term_decision(),
                    self.get_short_term_decision()
                ]
                decisions = await asyncio.gather(*tasks)

                # 融合决策
                final_decision = self.fuse_decisions(decisions)

                # 执行纸交易
                await self.paper_trader.execute_decision(final_decision)

                # 缓存决策
                self.decision_cache.set(final_decision)

            except Exception as e:
                logger.error(f"高频决策错误: {e}")

            await asyncio.sleep(self.interval)
```

### 阶段 6: 风险管理和回测 (2 天)

**目标**: 实现风险管理机制和回测框架

**核心模块**:
1. **risk_manager.py** - 风险管理
2. **backtest_engine.py** - 回测引擎

**风险控制**:
```python
class RiskManager:
    def validate_position(self, decision: TradingDecision,
                         current_positions: Dict) -> bool:
        """
        验证仓位风险
        - 单个资产最大仓位 (10%)
        - 总仓位限制 (80%)
        - 止损检查
        - 相关性检查
        """
        pass

    def calculate_position_size(self, decision: TradingDecision,
                               account_balance: float) -> float:
        """
        基于风险计算仓位大小
        - Kelly公式
        - 固定比例
        - ATR-based
        """
        pass
```

### 阶段 7: 监控和优化 (2 天)

**目标**: 实现系统监控和性能优化

**核心模块**:
1. **performance_monitor.py** - 性能监控
2. **cost_optimizer.py** - 成本优化 (LLM调用成本)

**监控指标**:
```python
class PerformanceMonitor:
    def track_decision(self, decision: TradingDecision, outcome: Dict):
        """
        跟踪决策效果
        - 命中率
        - 平均回报
        - 最大回撤
        - 夏普比率
        """
        pass

    def calculate_metrics(self) -> Dict:
        """
        计算性能指标
        - 总回报率
        - 年化回报
        - 最大回撤
        - 夏普比率
        - 卡玛比率
        - 胜率
        """
        pass

class CostOptimizer:
    def optimize_llm_calls(self):
        """
        优化LLM调用成本
        - 智能缓存 (避免重复调用)
        - 批处理 (合并多个决策)
        - 模型选择 (低成本模型处理简单情况)
        """
        pass
```

## 🛠️ 技术细节

### DeepSeek + Qwen3 API 客户端

```python
# 支持多个LLM模型的统一接口
LLM_MODELS = {
    'deepseek': {
        'client': DeepSeekClient,
        'cost_per_token': 0.0001,  # 更低
        'model_name': 'deepseek-chat'
    },
    'qwen': {
        'client': QwenClient,
        'cost_per_token': 0.0002,
        'model_name': 'qwen-turbo'
    }
}
```

### 决策架构

```python
class TradingDecision(BaseModel):
    # 基础决策
    action: Literal["BUY", "SELL", "HOLD"]
    confidence: float  # 0-100

    # 价格
    entry_price: Optional[float]
    stop_loss: Optional[float]
    take_profit: Optional[float]

    # 仓位
    position_size: float  # 百分比 0-100
    leverage: float = 1.0

    # 分析
    reasoning: str
    timeframes: Dict[str, str]  # {"4h": "BUY", "3m": "BUY"}

    # 风险
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    risk_score: float  # 0-100

    # 元数据
    model_sources: List[str]  # ["deepseek", "qwen"]
    timestamp: datetime
```

### 成本优化策略

```python
class CostOptimizer:
    def __init__(self):
        self.call_count = 0
        self.cost_per_call = {
            'deepseek': 0.01,  # 估算
            'qwen': 0.02
        }

    async def smart_call(self, prompt: str, urgency: str) -> str:
        """
        智能调用策略
        - 高 urgency: 使用高质量模型
        - 低 urgency: 使用低成本模型
        - 缓存命中: 直接返回
        """
        if urgency == 'HIGH':
            return await self.llm_clients['deepseek'].call(prompt)
        else:
            return await self.llm_clients['qwen'].call(prompt)

    def calculate_hourly_cost(self, calls_per_hour: int) -> float:
        """
        计算每小时成本
        """
        return calls_per_hour * sum(self.cost_per_call.values())
```

## 📊 预期性能

### 响应时间目标
- 单次决策: < 3 秒
- 并行LLM调用: < 5 秒
- 决策融合: < 1 秒

### 成本预算 (每月)
- DeepSeek: ~$100-200 (每5分钟调用)
- Qwen3: ~$100-200
- 总计: ~$200-400/月

### 性能指标目标
- 胜率: > 50%
- 夏普比率: > 1.0
- 最大回撤: < 15%
- 年化回报: > 20%

## 🚀 立即开始

**下一步**: 开始实现阶段 1 - 多时间框架数据预处理

**预计开始时间**: 明天

**准备事项**:
1. ✅ 获取 DeepSeek API Key
2. ✅ 获取 Qwen3 API Key
3. ✅ 准备测试环境

您准备好开始了吗？我们可以立即开始阶段 1 的实现！
