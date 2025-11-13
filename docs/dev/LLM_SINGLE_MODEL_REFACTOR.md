# LLM决策逻辑重构：单一模型原则

## 📋 修改概述

本次重构解决了LLM决策过程中的一个重要问题：**一个账户应该只使用一个LLM进行决策**。

### ❌ 旧问题
在之前的实现中，系统在单个决策过程中调用了多个LLM（DeepSeek和Qwen），然后融合它们的输出。这不符合逻辑，因为：
- 一个账户的决策应该是单一的、连贯的
- 多个LLM应该用于多账户对比测试，而非单个决策融合
- 融合多个LLM的决策增加了复杂性和不确定性

### ✅ 新方案
现在实施以下原则：
1. **一个账户 → 一个LLM**：每个账户（交易对）分配一个特定的LLM模型
2. **多账户对比**：多个LLM用于对比测试（相同prompt，不同LLM）
3. **单一决策**：每个决策只使用一个LLM，避免不必要的融合

## 🔧 修改详情

### 1. 配置文件更新 (`config.py`)

新增账户-LLM映射配置：

```python
# 账户配置（每个账户使用一个LLM）
ACCOUNT_CONFIGS = {
    'account_deepseek': {
        'llm_model': 'deepseek',
        'symbols': ['BTCUSDT', 'ETHUSDT'],
        'description': '使用 DeepSeek 进行长期趋势分析'
    },
    'account_qwen': {
        'llm_model': 'qwen',
        'symbols': ['SOLUSDT', 'BNBUSDT'],
        'description': '使用 Qwen 进行短期动量分析'
    }
}

# LLM模型优先级
LLM_MODEL_PRIORITY = ['deepseek', 'qwen']

# 多账户对比模式配置
MULTI_ACCOUNT_COMPARISON = {
    'enabled': True,
    'symbols': ['BTCUSDT'],
    'accounts': ['account_deepseek', 'account_qwen']
}
```

### 2. 调度器重构 (`scheduling/high_freq_scheduler.py`)

#### 主要变更：

**a) 新增辅助方法：**
- `_build_symbol_llm_mapping()`：构建交易对到LLM的映射
- `_validate_symbol_llm_mapping()`：验证映射合理性
- `_get_prompt_for_symbol()`：生成综合提示（长期+短期）

**b) 修改核心方法：**
- `_process_symbol()`：简化为调用单一LLM
- `_parallel_llm_call()` → `_single_llm_call()`：重写为单一LLM调用
- `_fuse_decisions()`：保留但标记为仅用于多账户对比场景

**c) 更新 DecisionScheduler 类：**
- 添加LLM模型选择逻辑
- 支持用户指定模型
- 生成综合提示而非分离提示

### 3. 决策流程对比

#### 旧流程（问题）：
```
交易对 → 数据获取 → 生成2个提示(4h+3m) → 调用2个LLM → 融合决策 → 执行
```

#### 新流程（正确）：
```
交易对 → 数据获取 → 生成1个综合提示 → 调用1个LLM → 执行
```

### 4. 多账户对比测试

多账户对比测试场景：
```python
# 配置多账户对比
MULTI_ACCOUNT_COMPARISON = {
    'enabled': True,
    'symbols': ['BTCUSDT'],  # 对比测试交易对
    'accounts': ['account_deepseek', 'account_qwen']
}

# 系统行为：
# 1. 对BTCUSDT生成一个prompt
# 2. 分别用DeepSeek和Qwen处理相同prompt
# 3. 对比两个模型的效果（用于评估）
```

## 📊 关键改进

### 1. 逻辑清晰性
- ✅ 每个决策只涉及一个LLM
- ✅ 账户和LLM的映射明确
- ✅ 避免了不必要的决策融合

### 2. 成本控制
- ⚡ 减少LLM调用次数（从2次减至1次）
- 💰 降低API调用成本
- 📈 提高系统效率

### 3. 可扩展性
- 🔧 易于添加新LLM模型
- 📝 灵活的账户配置
- 🎯 支持多账户对比测试

### 4. 可维护性
- 📌 代码逻辑更简单
- 🐛 减少潜在bug
- 📖 文档更清晰

## 🔍 验证方法

### 1. 检查日志输出
```bash
# 应该看到：
# "使用 deepseek 分析 BTCUSDT..."
# 或
# "使用 qwen 分析 SOLUSDT..."

# 不应该看到：
# "调用 DeepSeek 分析..."
# "调用 Qwen 分析..."
# "融合X个决策..."
```

### 2. 验证映射配置
```python
from config import ACCOUNT_CONFIGS, symbol_to_llm

# 检查每个交易对是否映射到单一LLM
for symbol in symbols:
    llm = symbol_to_llm[symbol]
    print(f"{symbol} → {llm}")
```

### 3. 决策统计
```python
# 检查决策的模型来源
decision.model_source  # 应该是单一模型名，如 'deepseek' 或 'qwen'
# 不应该是 'fused' 或 'multi_account_fusion'
```

## 📚 使用指南

### 1. 配置账户
编辑 `config.py` 中的 `ACCOUNT_CONFIGS`：
```python
ACCOUNT_CONFIGS = {
    'my_account': {
        'llm_model': 'deepseek',  # 指定LLM
        'symbols': ['BTCUSDT'],   # 分配交易对
        'description': '我的账户'
    }
}
```

### 2. 启动调度器
```python
from llm_clients.llm_factory import create_llm_factory_from_env
from trading.paper_trader import PaperTrader
from scheduling.high_freq_scheduler import HighFreqScheduler

llm_factory = create_llm_factory_from_env()
paper_trader = PaperTrader()
scheduler = HighFreqScheduler(
    symbols=['BTCUSDT', 'ETHUSDT'],
    llm_factory=llm_factory,
    paper_trader=paper_trader
)

# 启动调度器
await scheduler.start()
```

### 3. 单次决策
```python
from scheduling.high_freq_scheduler import DecisionScheduler

scheduler = DecisionScheduler(
    symbol='BTCUSDT',
    llm_factory=llm_factory,
    paper_trader=paper_trader,
    llm_model='deepseek'  # 可选：指定模型
)

decision = await scheduler.make_decision()
print(f"决策: {decision.action}, 模型: {decision.model_source}")
```

## 🚀 后续建议

### 1. 测试覆盖
- [ ] 单元测试：单一LLM决策
- [ ] 集成测试：多账户配置
- [ ] 性能测试：成本对比

### 2. 监控指标
- [ ] LLM调用次数
- [ ] 决策成功率
- [ ] 成本统计

### 3. 文档完善
- [ ] 更新API文档
- [ ] 添加最佳实践指南
- [ ] 补充故障排除手册

## ⚠️ 注意事项

1. **向后兼容性**：决策融合逻辑已保留但标记为过时，仅在多账户对比时使用
2. **缓存更新**：缓存键包含LLM信息，避免不同LLM的决策混淆
3. **错误处理**：当指定LLM不可用时，自动回退到优先级列表中的可用模型
4. **成本监控**：统计已更新，反映单一LLM调用的真实成本

## 📞 支持

如有问题，请参考：
- 代码注释：详细说明了每个方法的作用
- 日志输出：包含详细的决策过程信息
- 测试用例：参考 `tests/` 目录中的相关测试

---

**版本**: v2.0
**日期**: 2025-11-13
**作者**: Claude Code
