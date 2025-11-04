"""
API服务

提供REST API接口，参考nof1.ai的设计风格
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
import sqlite3
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trading.paper_trader import PaperTrader
from monitoring.performance_monitor import PerformanceMonitor
from models.trading_decision import TradingDecision


# FastAPI应用初始化
app = FastAPI(
    title="Nof1 Trading API",
    description="LLM驱动的量化交易系统API",
    version="1.0.0"
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== 数据模型 =====

class DecisionRecord(BaseModel):
    """决策记录模型"""
    id: int
    timestamp: str
    symbol: str
    action: str
    confidence: float
    model_source: str
    pnl: float
    execution_time: float
    llm_cost: float
    total_cost: float
    reasoning: Optional[str] = None
    position_size: Optional[float] = None
    risk_level: Optional[str] = None


class ProfitDataPoint(BaseModel):
    """盈利数据点模型"""
    timestamp: str
    model: str
    total_pnl: float
    cumulative_pnl: float
    trade_count: int


class PerformanceSummary(BaseModel):
    """性能摘要模型"""
    model: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    avg_pnl_per_trade: float
    max_drawdown: float
    sharpe_ratio: float
    total_cost: float
    roi: float


# ===== API端点 =====

@app.get("/api/v1/decisions")
async def get_decisions(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    model: Optional[str] = Query(None, description="模型筛选 (deepseek/qwen/fusion)"),
    symbol: Optional[str] = Query(None, description="交易对筛选"),
    action: Optional[str] = Query(None, description="操作筛选 (BUY/SELL/HOLD)"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)")
):
    """
    获取决策记录
    支持分页、模型筛选、时间范围筛选
    """
    try:
        db_path = "performance_monitor.db"
        if not os.path.exists(db_path):
            return {
                "success": True,
                "data": [],
                "pagination": {"page": 1, "limit": limit, "total": 0, "total_pages": 0},
                "message": "数据库文件不存在"
            }

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 构建查询条件
        where_conditions = []
        params = []

        if model:
            where_conditions.append("action LIKE ?")
            params.append(f"%{model}%")

        if symbol:
            where_conditions.append("symbol = ?")
            params.append(symbol)

        if action:
            where_conditions.append("action = ?")
            params.append(action)

        if start_date:
            where_conditions.append("timestamp >= ?")
            params.append(start_date)

        if end_date:
            where_conditions.append("timestamp <= ?")
            params.append(end_date)

        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""

        # 查询总数
        count_query = f"SELECT COUNT(*) FROM trading_metrics {where_clause}"
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]

        # 查询数据 (分页)
        offset = (page - 1) * limit
        data_query = f"""
            SELECT id, timestamp, symbol, action, confidence, pnl,
                   execution_time, llm_cost, total_cost
            FROM trading_metrics
            {where_clause}
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
        """

        cursor.execute(data_query, params + [limit, offset])
        rows = cursor.fetchall()

        conn.close()

        # 转换为模型
        decisions = []
        for row in rows:
            decisions.append({
                "id": row[0],
                "timestamp": row[1],
                "symbol": row[2],
                "action": row[3],
                "confidence": row[4],
                "pnl": row[5],
                "execution_time": row[6],
                "llm_cost": row[7],
                "total_cost": row[8]
            })

        return {
            "success": True,
            "data": decisions,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/models/profit")
async def get_models_profit(
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    interval: str = Query("hour", description="时间间隔 (hour/day/week)")
):
    """
    获取每个模型的盈利数据
    用于绘制盈利曲线
    """
    try:
        db_path = "performance_monitor.db"
        if not os.path.exists(db_path):
            return {
                "success": True,
                "data": [],
                "message": "数据库文件不存在"
            }

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 构建查询条件
        where_conditions = ["pnl IS NOT NULL"]
        params = []

        if start_date:
            where_conditions.append("timestamp >= ?")
            params.append(start_date)

        if end_date:
            where_conditions.append("timestamp <= ?")
            params.append(end_date)

        where_clause = "WHERE " + " AND ".join(where_conditions)

        # 根据间隔确定时间格式化
        time_format = {
            "hour": "%Y-%m-%d %H:00:00",
            "day": "%Y-%m-%d",
            "week": "%Y-%W"
        }.get(interval, "%Y-%m-%d")

        # 查询每个时间段的累计盈利
        profit_query = f"""
            SELECT
                strftime('{time_format}', timestamp) as time_period,
                COUNT(*) as trade_count,
                SUM(pnl) as period_pnl
            FROM trading_metrics
            {where_clause}
            GROUP BY time_period
            ORDER BY time_period
        """

        cursor.execute(profit_query, params)
        rows = cursor.fetchall()

        conn.close()

        # 计算累计盈利
        profit_data = []
        cumulative = 0
        for row in rows:
            cumulative += row[2] if row[2] else 0
            profit_data.append({
                "timestamp": row[0],
                "period_pnl": row[2] if row[2] else 0,
                "cumulative_pnl": cumulative,
                "trade_count": row[1]
            })

        return {
            "success": True,
            "data": profit_data,
            "interval": interval
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/models/performance")
async def get_models_performance():
    """
    获取所有模型的性能摘要
    """
    try:
        db_path = "performance_monitor.db"
        if not os.path.exists(db_path):
            return {
                "success": True,
                "data": {
                    "model": "ALL",
                    "total_trades": 0,
                    "winning_trades": 0,
                    "losing_trades": 0,
                    "win_rate": 0,
                    "total_pnl": 0,
                    "avg_pnl_per_trade": 0,
                    "total_cost": 0
                },
                "message": "数据库文件不存在"
            }

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 按模型分组统计
        performance_query = """
            SELECT
                'ALL' as model,
                COUNT(*) as total_trades,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losing_trades,
                AVG(CASE WHEN pnl > 0 THEN 1.0 ELSE 0.0 END) * 100 as win_rate,
                SUM(pnl) as total_pnl,
                AVG(pnl) as avg_pnl_per_trade,
                SUM(total_cost) as total_cost
            FROM trading_metrics
            WHERE pnl IS NOT NULL
        """

        cursor.execute(performance_query)
        row = cursor.fetchone()

        conn.close()

        performance_summary = {
            "model": row[0] if row else "ALL",
            "total_trades": row[1] if row else 0,
            "winning_trades": row[2] if row else 0,
            "losing_trades": row[3] if row else 0,
            "win_rate": round(row[4], 2) if row else 0,
            "total_pnl": round(row[5], 2) if row else 0,
            "avg_pnl_per_trade": round(row[6], 2) if row else 0,
            "total_cost": round(row[7], 4) if row else 0
        }

        return {
            "success": True,
            "data": performance_summary
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/stats/summary")
async def get_stats_summary():
    """
    获取系统统计摘要
    """
    try:
        db_path = "performance_monitor.db"
        if not os.path.exists(db_path):
            return {
                "success": True,
                "data": {
                    "total_decisions": 0,
                    "total_trades": 0,
                    "total_pnl": 0,
                    "total_cost": 0,
                    "avg_confidence": 0,
                    "cost_per_trade": 0
                },
                "message": "数据库文件不存在"
            }

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 获取基本统计
        stats_queries = {
            "total_decisions": "SELECT COUNT(*) FROM trading_metrics",
            "total_trades": "SELECT COUNT(*) FROM trading_metrics WHERE pnl IS NOT NULL",
            "total_pnl": "SELECT SUM(pnl) FROM trading_metrics WHERE pnl IS NOT NULL",
            "total_cost": "SELECT SUM(total_cost) FROM trading_metrics",
            "avg_confidence": "SELECT AVG(confidence) FROM trading_metrics"
        }

        results = {}
        for key, query in stats_queries.items():
            cursor.execute(query)
            result = cursor.fetchone()[0]
            results[key] = result if result else 0

        conn.close()

        return {
            "success": True,
            "data": {
                "total_decisions": results["total_decisions"],
                "total_trades": results["total_trades"],
                "total_pnl": round(results["total_pnl"], 2),
                "total_cost": round(results["total_cost"], 4),
                "avg_confidence": round(results["avg_confidence"], 2) if results["avg_confidence"] else 0,
                "cost_per_trade": round(results["total_cost"] / max(results["total_trades"], 1), 4)
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/health")
async def health_check():
    """
    健康检查
    """
    return {
        "success": True,
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


# ===== 启动应用 =====

if __name__ == "__main__":
    import uvicorn
    print("🚀 启动Nof1 Trading API服务...")
    print("📖 API文档: http://localhost:8000/docs")
    print("🔍 ReDoc文档: http://localhost:8000/redoc")
    uvicorn.run(app, host="0.0.0.0", port=8000)
