"""
API使用示例

演示如何使用Nof1 Trading API
"""

import requests
import json
from datetime import datetime, timedelta


class Nof1APIClient:
    """Nof1 API客户端"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def get_decisions(
        self,
        page: int = 1,
        limit: int = 20,
        model: str = None,
        symbol: str = None,
        action: str = None,
        start_date: str = None,
        end_date: str = None
    ):
        """获取决策记录"""
        params = {
            "page": page,
            "limit": limit
        }

        if model:
            params["model"] = model
        if symbol:
            params["symbol"] = symbol
        if action:
            params["action"] = action
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        response = requests.get(f"{self.base_url}/api/v1/decisions", params=params)
        return response.json()

    def get_models_profit(
        self,
        start_date: str = None,
        end_date: str = None,
        interval: str = "hour"
    ):
        """获取模型盈利数据"""
        params = {"interval": interval}

        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        response = requests.get(f"{self.base_url}/api/v1/models/profit", params=params)
        return response.json()

    def get_models_performance(self):
        """获取模型性能摘要"""
        response = requests.get(f"{self.base_url}/api/v1/models/performance")
        return response.json()

    def get_stats_summary(self):
        """获取系统统计摘要"""
        response = requests.get(f"{self.base_url}/api/v1/stats/summary")
        return response.json()

    def health_check(self):
        """健康检查"""
        response = requests.get(f"{self.base_url}/api/v1/health")
        return response.json()


def main():
    """主函数 - 演示API使用"""
    print("=" * 80)
    print("📡 Nof1 Trading API 使用示例")
    print("=" * 80)

    # 初始化API客户端
    api = Nof1APIClient()

    print("\n1️⃣ 健康检查")
    print("-" * 80)
    health = api.health_check()
    print(json.dumps(health, indent=2, ensure_ascii=False))

    print("\n2️⃣ 获取系统统计摘要")
    print("-" * 80)
    stats = api.get_stats_summary()
    print(json.dumps(stats, indent=2, ensure_ascii=False))

    print("\n3️⃣ 获取模型性能摘要")
    print("-" * 80)
    performance = api.get_models_performance()
    print(json.dumps(performance, indent=2, ensure_ascii=False))

    print("\n4️⃣ 获取决策记录（分页）")
    print("-" * 80)
    decisions = api.get_decisions(page=1, limit=10)
    print(f"总记录数: {decisions['pagination']['total']}")
    print(f"当前页: {decisions['pagination']['page']}")
    print(f"每页数量: {decisions['pagination']['limit']}")
    print("\n前5条记录:")
    for decision in decisions['data'][:5]:
        print(f"  [{decision['timestamp']}] {decision['symbol']} - {decision['action']} - PnL: {decision['pnl']}")

    print("\n5️⃣ 获取模型盈利数据（最近7天）")
    print("-" * 80)
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    profit = api.get_models_profit(
        start_date=start_date,
        end_date=end_date,
        interval="day"
    )
    print(f"时间间隔: {profit['interval']}")
    print(f"数据点数: {len(profit['data'])}")
    print("\n每日累计盈利:")
    for point in profit['data']:
        print(f"  {point['timestamp']}: {point['cumulative_pnl']:.2f} (交易次数: {point['trade_count']})")

    print("\n6️⃣ 按模型筛选决策记录")
    print("-" * 80)
    deepseek_decisions = api.get_decisions(model="deepseek", limit=5)
    print(f"DeepSeek决策数: {deepseek_decisions['pagination']['total']}")
    for decision in deepseek_decisions['data']:
        print(f"  {decision['timestamp']} - {decision['action']} - 置信度: {decision['confidence']}")

    print("\n7️⃣ 按操作类型筛选")
    print("-" * 80)
    buy_decisions = api.get_decisions(action="BUY", limit=5)
    print(f"买入决策数: {buy_decisions['pagination']['total']}")
    sell_decisions = api.get_decisions(action="SELL", limit=5)
    print(f"卖出决策数: {sell_decisions['pagination']['total']}")
    hold_decisions = api.get_decisions(action="HOLD", limit=5)
    print(f"持有决策数: {hold_decisions['pagination']['total']}")

    print("\n8️⃣ 按交易对筛选")
    print("-" * 80)
    btc_decisions = api.get_decisions(symbol="BTCUSDT", limit=5)
    print(f"BTCUSDT决策数: {btc_decisions['pagination']['total']}")

    print("\n9️⃣ 时间范围查询")
    print("-" * 80)
    week_decisions = api.get_decisions(
        start_date=start_date,
        end_date=end_date,
        limit=10
    )
    print(f"最近7天决策数: {week_decisions['pagination']['total']}")

    print("\n" + "=" * 80)
    print("📝 API使用总结")
    print("=" * 80)
    print()
    print("✅ 支持的端点:")
    print("  - GET /api/v1/decisions - 获取决策记录（支持分页、筛选）")
    print("  - GET /api/v1/models/profit - 获取盈利数据（支持时间聚合）")
    print("  - GET /api/v1/models/performance - 获取性能摘要")
    print("  - GET /api/v1/stats/summary - 获取系统统计")
    print("  - GET /api/v1/health - 健康检查")
    print()
    print("✅ 筛选参数:")
    print("  - page: 页码 (默认: 1)")
    print("  - limit: 每页数量 (默认: 20, 最大: 100)")
    print("  - model: 模型筛选 (deepseek/qwen/fusion)")
    print("  - symbol: 交易对筛选 (BTCUSDT/ETHUSDT等)")
    print("  - action: 操作筛选 (BUY/SELL/HOLD)")
    print("  - start_date: 开始日期 (YYYY-MM-DD)")
    print("  - end_date: 结束日期 (YYYY-MM-DD)")
    print()
    print("✅ API文档:")
    print("  - Swagger UI: http://localhost:8000/docs")
    print("  - ReDoc: http://localhost:8000/redoc")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
