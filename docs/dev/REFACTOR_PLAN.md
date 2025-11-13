# nof1 多账户重构计划

## 📋 项目概述

### 当前状态
- 现有项目为单账户架构，按交易对(symbol)分配LLM
- 需要重构为多账户架构，按账户(trader)分配LLM
- 参考 nofx 项目的成熟设计

### 重构目标
1. 实现多账户管理系统
2. 每个账户绑定一个LLM模型
3. 每个账户独立资金管理
4. 实时对比不同LLM的交易效果

## 📚 文档维护要求

### 文档结构
- 本文档记录完整重构计划
- 包含详细的实现步骤
- 标注每个阶段的目标和验收标准
- 遇到调整时立即更新文档

### 更新规则
- 实现前必须先更新文档
- 实现中遇到问题需要调整时，更新文档
- 每个里程碑完成后，更新文档状态
- 保持文档与代码同步

## 🎯 阶段一：核心类设计与实现

### 目标
设计并实现多账户系统的核心类：Trader、TraderManager

### 实现步骤

#### Step 1: 创建 Trader 类
**文件位置**: `models/trader.py`
**描述**: 交易员（账户）抽象类

**类设计**:
```python
class Trader:
    def __init__(self, trader_id, name, llm_model, initial_balance, llm_client)
    def get_decision(self, market_data) -> TradingDecision
    def execute_decision(self, decision, current_price) -> Dict
    def get_positions(self) -> List[Dict]
    def get_performance(self) -> Dict
```

**关键属性**:
- `trader_id`: 唯一标识
- `name`: 显示名称
- `llm_model`: 绑定的LLM模型
- `initial_balance`: 初始资金
- `current_balance`: 当前资金
- `positions`: 持仓字典
- `total_pnl`: 总盈亏
- `total_pnl_pct`: 收益率百分比
- `win_rate`: 胜率

**核心方法**:
- `get_decision()`: 调用绑定的LLM获取决策
- `execute_decision()`: 在独立账户中执行决策
- `update_positions()`: 更新持仓状态

**验收标准**:
- ✅ Trader类可以实例化
- ✅ 可以绑定LLM模型
- ✅ 可以执行决策并在独立账户中更新资金
- ✅ 可以计算并返回性能指标

#### Step 2: 创建 TraderManager 类
**文件位置**: `manager/trader_manager.py`
**描述**: 多账户管理器

**类设计**:
```python
class TraderManager:
    def __init__(self)
    def add_trader(self, trader: Trader)
    def remove_trader(self, trader_id)
    def get_trader(self, trader_id) -> Trader
    def list_traders(self) -> List[Trader]
    async def start_all(self)
    async def stop_all(self)
    async def run_once(self)
    def compare_performance(self) -> Dict
    def get_best_performer(self) -> Trader
```

**关键属性**:
- `traders`: Dict[str, Trader]，所有交易员
- `is_running`: bool，系统运行状态
- `market_data`: Dict，市场数据缓存

**核心方法**:
- `add_trader()`: 添加新的交易员
- `run_once()`: 执行一轮决策（所有交易员）
- `compare_performance()`: 对比所有交易员表现

**验收标准**:
- ✅ 可以添加多个Trader实例
- ✅ 可以并发运行所有Trader
- ✅ 可以对比性能并找出最佳表现者
- ✅ 系统稳定运行无崩溃

### 阶段一验收测试
运行测试文件：`tests/test_trader_manager.py`

**测试用例**:
1. 创建两个Trader实例（deepseek和qwen）
2. 为每个Trader添加相同的市场数据
3. 执行决策并验证资金独立
4. 对比性能指标

## 🎯 阶段二：配置系统重构

### 目标
重构配置系统，支持多账户配置

### 实现步骤

#### Step 1: 创建多账户配置文件
**文件位置**: `config/traders_config.py`
**描述**: 定义多账户初始配置

**配置格式**:
```python
TRADERS_CONFIG = [
    {
        'trader_id': 'trader_deepseek_001',
        'name': 'DeepSeek账户-01',
        'llm_model': 'deepseek',
        'initial_balance': 10000.0,
        'api_key': '${DEEPSEEK_API_KEY}',
        'symbols': ['BTCUSDT', 'ETHUSDT']
    },
    {
        'trader_id': 'trader_qwen_001',
        'name': 'Qwen账户-01',
        'llm_model': 'qwen',
        'initial_balance': 10000.0,
        'api_key': '${QWEN_API_KEY}',
        'symbols': ['BTCUSDT', 'ETHUSDT']
    }
]
```

#### Step 2: 实现配置加载器
**文件位置**: `manager/config_loader.py`
**描述**: 从配置文件创建Trader实例

**类设计**:
```python
class ConfigLoader:
    def __init__(self, config_path)
    def load_traders(self, llm_factory) -> List[Trader]
    def validate_config(self) -> bool
```

**验收标准**:
- ✅ 可以从配置文件加载多个Trader配置
- ✅ 可以验证配置的完整性
- ✅ 集成LLM工厂创建Trader实例

### 阶段二验收测试
运行测试文件：`tests/test_config_loader.py`

## 🎯 阶段三：调度器重构

### 目标
重写决策调度器，从单账户改为多账户

### 实现步骤

#### Step 1: 修改 HighFreqScheduler
**文件位置**: `scheduling/high_freq_scheduler.py`
**描述**: 重写为多账户调度器

**新架构要求**:
```python
class HighFreqScheduler:
    def __init__(self, trader_manager: TraderManager)
    async def start(self)
    async def _run_once(self)
    def _fetch_market_data(self) -> Dict
    async def _process_all_traders(self)
    def _log_performance_comparison(self)
```

**关键修改**:
- 删除 `symbol_to_llm` 映射逻辑
- 使用 `trader_manager` 管理所有账户
- 每个Trader独立决策和执行
- 实时对比和日志记录

**验收标准**:
- ✅ 可以启动多个Trader并发运行
- ✅ 每个Trader使用自己的LLM模型
- ✅ 性能对比日志输出清晰
- ✅ 系统稳定运行至少1小时

#### Step 2: 修改 DecisionScheduler
**文件位置**: `scheduling/decision_scheduler.py`
**描述**: 单Trader决策调度器（用于测试）

**类设计**:
```python
class DecisionScheduler:
    def __init__(self, trader: Trader)
    async def make_decision(self) -> TradingDecision
```

**验收标准**:
- ✅ 单Trader模式正常工作
- ✅ 可以独立测试任意Trader

### 阶段三验收测试
1. 集成测试：`tests/test_multi_account_integration.py`
2. 手动测试：运行 `python run_full_system.py`

## 🎯 阶段四：数据持久化

### 目标
修改数据库，支持多账户交易记录

### 实现步骤

#### Step 1: 扩展数据库表
**新增表**:
- `traders`: 交易员配置表
- `trader_trades`: 交易员交易记录表
- `trader_positions`: 交易员持仓表

#### Step 2: 修改数据访问层
**文件位置**: `database.py`
**新增方法**:
- `save_trader(trader)` 保存交易员
- `get_trader(trader_id)` 获取交易员
- `save_trade(trader_id, trade)` 保存交易
- `get_trader_performance(trader_id)` 获取性能

### 阶段四验收测试
运行测试文件：`tests/test_database_multi_account.py`

## 🎯 阶段五：集成测试

### 目标
全面测试多账户系统

### 测试场景

#### 场景1: 双账户对比
- Trader-1 使用 deepseek，初始10000U
- Trader-2 使用 qwen，初始10000U
- 运行30分钟
- 验证资金独立
- 对比PnL差异

#### 场景2: 故障恢复
- 模拟某个Trader的LLM调用失败
- 验证其他Trader继续运行
- 验证失败Trader的错误处理

#### 场景3: 扩展性测试
- 添加第三个Trader
- 验证系统正常运行
- 验证性能对比包含新Trader

### 验收标准
- ✅ 所有测试场景通过
- ✅ 系统稳定运行2小时以上
- ✅ 性能对比数据准确
- ✅ 日志输出清晰完整

## 🎯 阶段六：文档更新

### 目标
更新所有相关文档

### 文档列表

1. **用户文档**
   - `docs/user/MULTI_ACCOUNT_USAGE.md`: 多账户使用指南
   - `docs/user/QUICKSTART_TESTNET.md`: 更新快速开始指南

2. **开发者文档**
   - `docs/dev/ARCHITECTURE.md`: 新架构文档
   - `docs/dev/API_REFERENCE.md`: API参考文档

3. **维护文档**
   - `docs/project/DEPLOYMENT_GUIDE.md`: 部署指南
   - `docs/project/TROUBLESHOOTING.md`: 故障排除

### 更新要求
- 每个文档必须包含实际代码示例
- 所有配置说明必须准确
- 包含常见问题解答
- 提供故障排除指南

## 🔧 工具与脚本

### 开发工具

1. **验证脚本**:
   - `scripts/verify_multi_account.py`: 验证多账户架构
   - `scripts/benchmark_performance.py`: 性能对比脚本

2. **迁移脚本**:
   - `scripts/migrate_to_multi_account.py`: 从单账户迁移到多账户

3. **监控脚本**:
   - `scripts/monitor_traders.py`: 实时监控所有Trader状态

### 验收测试

1. **单元测试**:
   - 覆盖所有新增类和方法
   - 模拟各种异常情况

2. **集成测试**:
   - 端到端测试完整流程
   - 多账户并发测试

3. **性能测试**:
   - 验证系统在高负载下的表现
   - 内存和CPU使用情况

## 📦 交付物清单

### 代码交付物
- [ ] `models/trader.py`: Trader类实现
- [ ] `manager/trader_manager.py`: TraderManager类实现
- [ ] `manager/config_loader.py`: 配置加载器实现
- [ ] `scheduling/high_freq_scheduler.py`: 多账户调度器实现
- [ ] `config/traders_config.py`: 多账户配置示例
- [ ] `scripts/verify_multi_account.py`: 验证脚本

### 测试交付物
- [ ] `tests/test_trader.py`: Trader类单元测试
- [ ] `tests/test_trader_manager.py`: TraderManager测试
- [ ] `tests/test_config_loader.py`: 配置加载测试
- [ ] `tests/test_multi_account_integration.py`: 集成测试

### 文档交付物
- [ ] `docs/dev/MULTI_ACCOUNT_ARCHITECTURE.md`: 架构文档
- [ ] `docs/user/MULTI_ACCOUNT_USAGE.md`: 用户指南
- [ ] `docs/dev/API_REFERENCE.md`: API参考

### 验收标准
- [ ] 所有单元测试通过
- [ ] 集成测试通过
- [ ] 手动测试通过
- [ ] 文档完整准确
- [ ] 系统稳定运行2小时以上

## ⚠️ 风险与应对

### 风险1: LLM API限制
**问题**: 同时调用多个LLM可能触达API限制
**应对**:
- 实现请求队列和限流
- 添加失败重试机制
- 监控API调用频率

### 风险2: 数据竞争
**问题**: 多个Trader并发访问共享数据
**应对**:
- 使用线程锁保护关键数据
- 独立的market_data副本
- 异步处理减少竞争

### 风险3: 资金同步问题
**问题**: 持仓更新不同步
**应对**:
- 每个Trader独立的数据存储
- 定期同步持仓状态
- 实现事务性更新

## 📅 时间计划

| 阶段 | 预计时间 | 主要工作 |
|------|----------|----------|
| 阶段一 | 2天 | 核心类设计与实现 |
| 阶段二 | 1天 | 配置系统重构 |
| 阶段三 | 3天 | 调度器重构 |
| 阶段四 | 1天 | 数据持久化 |
| 阶段五 | 2天 | 集成测试 |
| 阶段六 | 1天 | 文档更新 |
| **总计** | **10天** | **完整重构** |

## 🎯 成功标准

1. **功能性**:
   - ✅ 支持至少2个Trader同时运行
   - ✅ 每个Trader绑定不同LLM
   - ✅ 账户资金完全独立
   - ✅ 实时性能对比

2. **稳定性**:
   - ✅ 系统稳定运行8小时以上
   - ✅ 无内存泄漏
   - ✅ 异常处理完善

3. **可维护性**:
   - ✅ 代码结构清晰
   - ✅ 文档完整准确
   - ✅ 测试覆盖率高

4. **性能**:
   - ✅ 决策延迟 < 5秒
   - ✅ 支持扩展到10个Trader
   - ✅ CPU使用率 < 50%

---

## 📝 实施记录

### 更新日志
- [2025-11-13] 创建初始重构计划
- [2025-11-13 10:40] ✅ 阶段一 Step 1: 创建 Trader 类完成 (models/trader.py)
- [2025-11-13 10:45] ✅ 阶段一 Step 2: 创建 TraderManager 类完成 (manager/trader_manager.py)
- [2025-11-13 10:50] ✅ 阶段二 Step 1: 创建多账户配置文件完成 (config/traders_config.py)
- [2025-11-13 10:52] ✅ 阶段二 Step 2: 实现配置加载器完成 (manager/config_loader.py)
- [2025-11-13 10:54] ✅ 阶段二 Step 3: 验证脚本测试完成 (scripts/verify_config_system.py)
- [2025-11-13 10:57] ✅ 阶段三 Step 1: 多账户系统演示完成 (simple_multi_account_demo.py)
- [待更新] 最终总结
- [待更新] ...

### 遇到的问题与解决方案
- [待记录]

### 架构调整记录
- [待记录]

---

**重要提醒**:
1. 严格按照文档执行，不得跳过任何步骤
2. 每个阶段完成后必须更新此文档
3. 遇到问题先更新文档，再解决
4. 所有代码必须包含完整注释
