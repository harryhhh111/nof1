# nof1 多账户架构设计

## 🎯 当前问题

### 错误的架构（当前 nof1）
```
单账户系统：
- 一个交易系统管理所有交易对
- 每个交易对分配一个LLM（错误）
- 资金是统一的，不隔离

问题：
- BTCUSDT → deepseek
- ETHUSDT → qwen
- 这样没有意义，无法对比LLM效果
```

### 正确的架构（参考 nofx）
```
多账户系统：
- 每个账户(Trader)是一个独立的交易实体
- 每个账户绑定一个LLM
- 每个账户有独立的初始资金（如10000U）
- 所有账户看相同的市场数据
- 对比不同LLM的交易效果

设计：
Trader-001 (账户1) → deepseek → 10000U
Trader-002 (账户2) → qwen → 10000U
Trader-003 (账户3) → 自定义LLM → 10000U
```

## 🏗️ 新架构设计

### 1. Trader 类（账户抽象）

```python
class Trader:
    """交易员（账户）类"""

    def __init__(self,
                 trader_id: str,
                 name: str,
                 llm_model: str,
                 initial_balance: float,
                 llm_client: BaseLLMClient):
        """
        Args:
            trader_id: 唯一标识
            name: 显示名称
            llm_model: LLM模型名称
            initial_balance: 初始资金
            llm_client: LLM客户端实例
        """
        self.trader_id = trader_id
        self.name = name
        self.llm_model = llm_model
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.llm_client = llm_client

        # 持仓管理
        self.positions: Dict[str, Position] = {}

        # 交易记录
        self.trades: List[Trade] = []

        # 性能统计
        self.total_pnl = 0.0
        self.total_pnl_pct = 0.0
        self.win_rate = 0.0
        self.start_time = datetime.now()

    def get_decision(self, market_data: Dict) -> TradingDecision:
        """获取交易决策"""
        # 1. 生成提示（包含账户信息）
        prompt = self._generate_prompt(market_data)

        # 2. 调用绑定的LLM
        decision = self.llm_client.get_decision(prompt)

        # 3. 设置决策归属
        decision.trader_id = self.trader_id
        decision.llm_model = self.llm_model

        return decision

    def execute_decision(self, decision: TradingDecision, current_price: float):
        """执行交易决策（在独立账户中）"""
        if decision.action in ['BUY', 'SELL']:
            self._open_position(decision, current_price)
        elif decision.action == 'HOLD':
            self._update_existing_positions(decision)
```

### 2. MultiTraderManager 类（多账户管理器）

```python
class MultiTraderManager:
    """多账户管理器"""

    def __init__(self):
        self.traders: Dict[str, Trader] = {}
        self.market_data: Dict = {}
        self.is_running = False

    def add_trader(self, trader: Trader):
        """添加交易员"""
        self.traders[trader.trader_id] = trader
        logger.info(f"添加交易员: {trader.name} (LLM: {trader.llm_model})")

    def start_trading(self):
        """启动所有交易员"""
        self.is_running = True

        while self.is_running:
            # 1. 获取市场数据
            self.market_data = self._fetch_market_data()

            # 2. 所有交易员独立决策
            tasks = []
            for trader in self.traders.values():
                tasks.append(self._trader_make_decision(trader))

            # 3. 并发执行决策
            await asyncio.gather(*tasks)

            # 4. 性能对比
            self._compare_performance()

            # 5. 等待下一轮
            await asyncio.sleep(300)  # 5分钟

    async def _trader_make_decision(self, trader: Trader):
        """单个交易员决策流程"""
        try:
            # 获取决策
            decision = trader.get_decision(self.market_data)

            # 执行决策（在独立账户中）
            result = self._execute_in_isolated_account(trader, decision)

            # 记录结果
            logger.info(f"{trader.name}: {decision.action} "
                       f"(置信度: {decision.confidence}%, "
                       f"账户PnL: ${trader.total_pnl:.2f})")

        except Exception as e:
            logger.error(f"{trader.name} 决策失败: {e}")

    def _compare_performance(self):
        """对比所有交易员的性能"""
        logger.info("\n" + "="*60)
        logger.info("多账户性能对比")
        logger.info("="*60)

        for trader in self.traders.values():
            logger.info(
                f"{trader.name:20} | "
                f"LLM: {trader.llm_model:10} | "
                f"PnL: ${trader.total_pnl:8.2f} | "
                f"收益率: {trader.total_pnl_pct:6.2f}% | "
                f"胜率: {trader.win_rate:5.1f}%"
            )

        logger.info("="*60)

        # 找出最佳表现的LLM
        best_trader = max(self.traders.values(),
                         key=lambda t: t.total_pnl)
        logger.info(f"🏆 当前最佳: {best_trader.name} (LLM: {best_trader.llm_model})")
```

### 3. 配置示例

```python
# traders_config.py
TRADERS_CONFIG = [
    {
        'trader_id': 'trader_001',
        'name': 'DeepSeek账户',
        'llm_model': 'deepseek',
        'initial_balance': 10000.0,
        'api_key': 'deepseek_api_key_here'
    },
    {
        'trader_id': 'trader_002',
        'name': 'Qwen账户',
        'llm_model': 'qwen',
        'initial_balance': 10000.0,
        'api_key': 'qwen_api_key_here'
    },
    {
        'trader_id': 'trader_003',
        'name': '自定义LLM账户',
        'llm_model': 'custom',
        'initial_balance': 10000.0,
        'custom_config': {
            'api_url': 'https://custom-llm-api.com',
            'model_name': 'custom-gpt-4'
        }
    }
]
```

## 📊 数据流对比

### 当前架构（错误）
```
市场数据 → LLM工厂 → 多个LLM → 融合决策 → 统一执行
                            ↓
                        资金混合，无法对比
```

### 新架构（正确）
```
市场数据 →
    ├─→ Trader-001 (deepseek) → 决策 → 独立执行 (10000U账户)
    ├─→ Trader-002 (qwen) → 决策 → 独立执行 (10000U账户)
    └─→ Trader-003 (custom) → 决策 → 独立执行 (10000U账户)
                            ↓
                   对比各账户PnL效果
```

## 🔑 关键设计原则

1. **账户隔离**：每个Trader有独立的资金和持仓
2. **模型绑定**：每个Trader绑定一个LLM模型
3. **相同数据**：所有Trader看相同的市场数据
4. **独立决策**：每个Trader独立调用自己的LLM
5. **性能对比**：实时显示不同LLM的交易效果

## ✅ 实现优先级

1. **高优先级**：
   - Trader类设计
   - MultiTraderManager类设计
   - 独立账户资金管理

2. **中优先级**：
   - 性能对比面板
   - 实时数据同步
   - 风险控制

3. **低优先级**：
   - Web界面
   - 历史数据回测
   - 高级分析

## 🎯 成功指标

- ✅ 每个Trader有独立的初始资金（如10000U）
- ✅ 每个Trader使用不同的LLM
- ✅ 所有Trader看相同的市场数据
- ✅ 可以实时对比不同LLM的PnL效果
- ✅ 系统可以运行多个Trader实例
