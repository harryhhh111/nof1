#!/usr/bin/env python3
"""
数据库演示脚本

插入示例数据并展示如何查看
"""

import sys
import os
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database


def create_sample_data():
    """创建示例数据"""
    print("=" * 70)
    print("📊 创建示例数据...")
    print("=" * 70)

    db = Database()

    # 生成示例 K 线数据
    base_timestamp = int(datetime.now().timestamp() * 1000)
    symbols = ['BTCUSDT', 'ETHUSDT']

    for symbol in symbols:
        print(f"\n为 {symbol} 生成数据...")

        # 3分钟 K 线数据
        klines_3m = []
        base_price = 50000 if symbol == 'BTCUSDT' else 3000
        for i in range(50):
            timestamp = base_timestamp - (50 - i) * 180000  # 3分钟间隔
            price = base_price + np.random.randn() * 100
            kline = [
                timestamp,
                price,
                price + np.random.rand() * 50,
                price - np.random.rand() * 50,
                price + np.random.randn() * 30,
                np.random.uniform(1000, 5000),
                timestamp + 179999
            ]
            klines_3m.append(kline)

        # 4小时 K 线数据
        klines_4h = []
        for i in range(30):
            timestamp = base_timestamp - (30 - i) * 14400000  # 4小时间隔
            price = base_price + np.random.randn() * 500
            kline = [
                timestamp,
                price,
                price + np.random.rand() * 200,
                price - np.random.rand() * 200,
                price + np.random.randn() * 150,
                np.random.uniform(5000, 20000),
                timestamp + 14399999
            ]
            klines_4h.append(kline)

        # 插入 K 线数据
        db.insert_klines(symbol, klines_3m, '3m')
        db.insert_klines(symbol, klines_4h, '4h')

        # 创建技术指标数据
        df_3m = pd.DataFrame(klines_3m, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time'])
        df_4h = pd.DataFrame(klines_4h, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time'])

        # 计算指标
        from indicators import TechnicalIndicators
        ti = TechnicalIndicators()

        # 3分钟指标
        indicators_3m = ti.calculate_all_indicators(df_3m)
        latest_ts_3m = klines_3m[-1][0]
        db.insert_indicators(symbol, latest_ts_3m, '3m', indicators_3m)

        # 4小时指标
        indicators_4h = ti.calculate_all_indicators(df_4h)
        latest_ts_4h = klines_4h[-1][0]
        db.insert_indicators(symbol, latest_ts_4h, '4h', indicators_4h)

        # 永续合约数据
        perp_data = {
            'open_interest_latest': np.random.uniform(40000, 60000),
            'open_interest_average': np.random.uniform(45000, 55000),
            'funding_rate': np.random.uniform(-0.001, 0.001)
        }
        db.insert_perp_data(symbol, latest_ts_3m, perp_data)

        print(f"  ✅ {symbol} 数据插入完成")

    db.close()
    print("\n✅ 所有示例数据创建完成！")

def view_database_summary():
    """查看数据库摘要"""
    print("\n" + "=" * 70)
    print("📋 数据库摘要")
    print("=" * 70)

    db = Database()
    db_path = db.db_path

    print(f"\n📁 数据库文件: {db_path}")
    print(f"📏 文件大小: {os.path.getsize(db_path) / 1024:.2f} KB")

    # 统计各表记录数
    print("\n📊 数据统计:")
    tables = ['klines_3m', 'klines_4h', 'technical_indicators', 'perpetual_data']

    with sqlite3.connect(db_path) as conn:
        for table in tables:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            cursor.execute(f"SELECT COUNT(DISTINCT symbol) FROM {table}")
            symbols = cursor.fetchone()[0]
            print(f"  {table:25s}: {count:,} 条记录，{symbols} 个交易对")

    # 显示最新记录
    print("\n🕐 最新记录:")
    for table in tables:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT symbol, timestamp FROM {table}
                ORDER BY timestamp DESC
                LIMIT 3
            """)
            rows = cursor.fetchall()

            if rows:
                print(f"\n  📌 {table}:")
                for symbol, timestamp in rows:
                    dt = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
                    print(f"    - {symbol} @ {dt}")

    db.close()

def query_examples():
    """常用查询示例"""
    print("\n" + "=" * 70)
    print("🔍 常用查询示例")
    print("=" * 70)

    db_path = Database().db_path

    queries = {
        "1. 查看所有表": """
            SELECT name FROM sqlite_master WHERE type='table';
        """,

        "2. 查看 K 线数据 (前10条)": """
            SELECT symbol, timestamp, open, high, low, close, volume
            FROM klines_3m
            ORDER BY timestamp DESC
            LIMIT 10;
        """,

        "3. 查看技术指标 (最新5条)": """
            SELECT symbol, timeframe, ema_20, ema_50, rsi_14, atr_14
            FROM technical_indicators
            ORDER BY timestamp DESC
            LIMIT 5;
        """,

        "4. 查看永续合约数据": """
            SELECT symbol, funding_rate, open_interest_latest
            FROM perpetual_data
            ORDER BY timestamp DESC;
        """,

        "5. 统计每个交易对的记录数": """
            SELECT symbol, COUNT(*) as record_count
            FROM klines_3m
            GROUP BY symbol
            ORDER BY record_count DESC;
        """,

        "6. 查看 BTCUSDT 最新数据": """
            SELECT *
            FROM klines_3m
            WHERE symbol = 'BTCUSDT'
            ORDER BY timestamp DESC
            LIMIT 1;
        """,

        "7. 查看最新指标计算时间": """
            SELECT symbol, timeframe, MAX(timestamp) as latest_timestamp
            FROM technical_indicators
            GROUP BY symbol, timeframe
            ORDER BY latest_timestamp DESC;
        """
    }

    for title, query in queries.items():
        print(f"\n{title}")
        print("-" * 70)

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query)
                rows = cursor.fetchall()

                if query.strip().upper().startswith('SELECT'):
                    col_names = [desc[0] for desc in cursor.description] if cursor.description else []

                    if rows:
                        # 打印列名
                        header = " | ".join(col_names)
                        print(f"\n{header}")
                        print("-" * len(header))

                        # 打印数据
                        for row in rows[:5]:  # 限制显示5行
                            formatted_row = []
                            for i, value in enumerate(row):
                                col_name = col_names[i].lower() if i < len(col_names) else ''
                                if 'timestamp' in col_name:
                                    try:
                                        ts = int(value)
                                        dt = datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d %H:%M:%S')
                                        formatted_row.append(dt)
                                    except:
                                        formatted_row.append(str(value))
                                elif isinstance(value, float):
                                    formatted_row.append(f"{value:.4f}")
                                else:
                                    formatted_row.append(str(value))
                            print(" | ".join(formatted_row))

                        if len(rows) > 5:
                            print(f"... 还有 {len(rows) - 5} 行")
                        print(f"\n共 {len(rows)} 行")
                    else:
                        print("无数据")
                else:
                    print(f"✅ 执行成功，影响行数: {cursor.rowcount}")

            except Exception as e:
                print(f"❌ 查询失败: {e}")

def show_schema(table_name):
    """显示表结构"""
    print("\n" + "=" * 70)
    print(f"📋 {table_name} 表结构")
    print("=" * 70)

    db_path = Database().db_path

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

        if columns:
            print(f"\n字段列表:")
            for col in columns:
                cid, name, type_, notnull, default, pk = col
                pk_str = " (主键)" if pk else ""
                notnull_str = " NOT NULL" if notnull else ""
                default_str = f" DEFAULT {default}" if default else ""
                print(f"  {name:25s} {type_:15s}{notnull_str}{default_str}{pk_str}")
        else:
            print(f"表 {table_name} 不存在")

def main():
    """主函数"""
    print("\n" + "=" * 70)
    print(" 🗄️  Nof1 数据库演示")
    print("=" * 70)

    while True:
        print("\n请选择操作:")
        print("  1. 创建示例数据")
        print("  2. 查看数据库摘要")
        print("  3. 常用查询示例")
        print("  4. 查看表结构")
        print("  5. 退出")

        choice = input("\n请输入选择 (1-5): ").strip()

        if choice == '1':
            create_sample_data()
        elif choice == '2':
            view_database_summary()
        elif choice == '3':
            query_examples()
        elif choice == '4':
            tables = ['klines_3m', 'klines_4h', 'technical_indicators', 'perpetual_data']
            for table in tables:
                show_schema(table)
        elif choice == '5':
            print("\n👋 再见！")
            break
        else:
            print("\n❌ 无效选择，请重试")

if __name__ == '__main__':
    main()
