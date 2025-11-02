#!/usr/bin/env python3
"""
快速查询数据库

常用数据库查询命令
"""

import sys
import os
import sqlite3
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Database

def quick_query(query_type="all"):
    """快速查询"""
    db = Database()
    db_path = db.db_path

    queries = {
        "summary": "查看数据摘要",
        "latest": "查看最新记录",
        "symbols": "查看所有交易对",
        "klines": "查看 K 线数据",
        "indicators": "查看技术指标",
        "perp": "查看永续合约数据"
    }

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        if query_type == "all" or query_type == "summary":
            print("\n" + "=" * 70)
            print("📋 数据库摘要")
            print("=" * 70)
            print(f"数据库文件: {db_path}")

            for table in ['klines_3m', 'klines_4h', 'technical_indicators', 'perpetual_data']:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                cursor.execute(f"SELECT COUNT(DISTINCT symbol) FROM {table}")
                symbols = cursor.fetchone()[0]
                print(f"  {table:25s}: {count:,} 条记录，{symbols} 个交易对")

        if query_type == "all" or query_type == "symbols":
            print("\n" + "=" * 70)
            print("💰 交易对列表")
            print("=" * 70)
            cursor.execute("""
                SELECT DISTINCT symbol FROM klines_3m
                ORDER BY symbol
            """)
            for row in cursor.fetchall():
                print(f"  - {row[0]}")

        if query_type == "all" or query_type == "latest":
            print("\n" + "=" * 70)
            print("🕐 最新数据")
            print("=" * 70)

            for table in ['klines_3m', 'klines_4h', 'technical_indicators', 'perpetual_data']:
                cursor.execute(f"""
                    SELECT symbol, timestamp FROM {table}
                    ORDER BY timestamp DESC
                    LIMIT 1
                """)
                row = cursor.fetchone()
                if row:
                    dt = datetime.fromtimestamp(row[1] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                    print(f"  {table:25s}: {row[0]} @ {dt}")

        if query_type == "all" or query_type == "klines":
            print("\n" + "=" * 70)
            print("📈 K 线数据 (最新 5 条)")
            print("=" * 70)
            cursor.execute("""
                SELECT symbol, timestamp, open, high, low, close, volume
                FROM klines_3m
                ORDER BY timestamp DESC
                LIMIT 5
            """)
            print(f"{'交易对':12s} {'时间':20s} {'开盘':12s} {'最高':12s} {'最低':12s} {'收盘':12s} {'成交量':12s}")
            print("-" * 92)
            for row in cursor.fetchall():
                dt = datetime.fromtimestamp(row[1] / 1000).strftime('%m-%d %H:%M:%S')
                print(f"{row[0]:12s} {dt:20s} {row[2]:12.2f} {row[3]:12.2f} {row[4]:12.2f} {row[5]:12.2f} {row[6]:12.2f}")

        if query_type == "all" or query_type == "indicators":
            print("\n" + "=" * 70)
            print("📊 技术指标 (最新)")
            print("=" * 70)
            cursor.execute("""
                SELECT symbol, timeframe, ema_20, ema_50, rsi_14, atr_14
                FROM technical_indicators
                ORDER BY timestamp DESC
            """)
            print(f"{'交易对':12s} {'周期':6s} {'EMA20':12s} {'EMA50':12s} {'RSI14':8s} {'ATR14':12s}")
            print("-" * 70)
            for row in cursor.fetchall():
                print(f"{row[0]:12s} {row[1]:6s} {row[2]:12.2f} {row[3]:12.2f} {row[4]:8.2f} {row[5]:12.2f}")

        if query_type == "all" or query_type == "perp":
            print("\n" + "=" * 70)
            print("💹 永续合约数据")
            print("=" * 70)
            cursor.execute("""
                SELECT symbol, funding_rate, open_interest_latest
                FROM perpetual_data
                ORDER BY timestamp DESC
            """)
            print(f"{'交易对':12s} {'资金费率':12s} {'开放利息':15s}")
            print("-" * 40)
            for row in cursor.fetchall():
                print(f"{row[0]:12s} {row[1]:12.6f} {row[2]:15.2f}")

    db.close()

if __name__ == '__main__':
    query_type = "all"
    if len(sys.argv) > 1:
        query_type = sys.argv[1]
    quick_query(query_type)
