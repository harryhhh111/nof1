#!/usr/bin/env python3
"""
数据库查看工具

演示如何查看 SQLite 数据库中的数据
"""

import sys
import os
import sqlite3
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Database

def print_separator(title=""):
    """打印分隔线"""
    print("\n" + "=" * 70)
    if title:
        print(f" {title}")
        print("=" * 70)

def view_database():
    """查看数据库内容"""
    db = Database()

    # 检查数据库文件
    print_separator("数据库信息")
    print(f"数据库路径: {db.db_path}")
    print(f"文件大小: {os.path.getsize(db.db_path) / 1024:.2f} KB")

    # 查看表
    print_separator("数据表列表")
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table'
            ORDER BY name
        """)
        tables = cursor.fetchall()
        for table in tables:
            print(f"  - {table[0]}")

    # 查看各表记录数
    print_separator("数据统计")
    table_names = ['klines_3m', 'klines_4h', 'technical_indicators', 'perpetual_data']
    for table in table_names:
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  {table:25s}: {count:,} 条记录")
            except Exception as e:
                print(f"  {table:25s}: 0 条记录 (表不存在或为空)")

    # 查看最近的数据
    print_separator("最新数据 (每表 5 条)")
    for table in table_names:
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(f"""
                    SELECT * FROM {table}
                    ORDER BY timestamp DESC
                    LIMIT 5
                """)
                rows = cursor.fetchall()

                if rows:
                    print(f"\n📊 {table}:")
                    # 获取列名
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = [col[1] for col in cursor.fetchall()]

                    # 显示前 3 条记录的详细信息
                    for i, row in enumerate(rows[:3]):
                        print(f"\n  [{i+1}] ", end="")
                        for j, value in enumerate(row):
                            if j == 0:  # ID 跳过
                                continue
                            if j < len(columns):
                                col_name = columns[j]
                                # 格式化输出
                                if 'timestamp' in col_name.lower():
                                    try:
                                        ts = int(value)
                                        dt = datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d %H:%M:%S')
                                        print(f"{col_name}: {dt}", end=" | ")
                                    except:
                                        print(f"{col_name}: {value}", end=" | ")
                                elif isinstance(value, float):
                                    print(f"{col_name}: {value:.2f}", end=" | ")
                                else:
                                    print(f"{col_name}: {value}", end=" | ")
                        print()

                    if len(rows) > 3:
                        print(f"  ... 还有 {len(rows) - 3} 条记录")
                else:
                    print(f"\n  {table}: 无数据")
            except Exception as e:
                print(f"\n  {table}: 查询失败 - {e}")

    # 查看具体交易对数据
    print_separator("查看特定交易对数据")
    symbol = input("请输入交易对符号 (如 BTCUSDT，直接回车跳过): ").strip().upper()

    if symbol:
        try:
            data = db.get_latest_data(symbol)
            if data:
                print(f"\n✅ 找到 {symbol} 的最新数据:")
                print(f"  时间戳: {data['timestamp']}")
                print(f"  当前价格: ${data['current_price']:,.2f}")
                print(f"\n  日内数据:")
                print(f"    价格数量: {len(data['intraday']['prices'])}")
                print(f"    EMA20 数量: {len(data['intraday']['ema20'])}")
                print(f"    MACD 数量: {len(data['intraday']['macd'])}")
                print(f"\n  长期数据:")
                print(f"    EMA20: {data['long_term']['ema_20']}")
                print(f"    EMA50: {data['long_term']['ema_50']}")
                print(f"    RSI14: {data['long_term']['rsi_14']}")
                print(f"\n  永续合约数据:")
                print(f"    资金费率: {data['perp_data']['funding_rate']}")
            else:
                print(f"\n❌ 未找到 {symbol} 的数据")
        except Exception as e:
            print(f"\n❌ 查询失败: {e}")

    db.close()

def execute_sql():
    """自定义 SQL 查询"""
    print_separator("自定义 SQL 查询")
    print("输入 SQL 查询语句 (输入 'quit' 退出)")
    print("示例: SELECT * FROM klines_3m LIMIT 10;")
    print("-" * 70)

    db_path = Database().db_path

    while True:
        sql = input("\nSQL> ").strip()
        if sql.lower() in ['quit', 'exit', 'q']:
            break

        if not sql:
            continue

        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(sql)

                # 判断是 SELECT 还是其他
                if sql.strip().upper().startswith('SELECT'):
                    rows = cursor.fetchall()
                    col_names = [desc[0] for desc in cursor.description] if cursor.description else []

                    if rows:
                        # 打印列名
                        print("\n" + " | ".join(col_names))
                        print("-" * 70)

                        # 打印前 10 行
                        for i, row in enumerate(rows[:10]):
                            formatted_row = []
                            for value in row:
                                if isinstance(value, float):
                                    formatted_row.append(f"{value:.2f}")
                                elif isinstance(value, int) and value > 1e12:  # timestamp
                                    try:
                                        dt = datetime.fromtimestamp(value / 1000).strftime('%Y-%m-%d %H:%M:%S')
                                        formatted_row.append(dt)
                                    except:
                                        formatted_row.append(str(value))
                                else:
                                    formatted_row.append(str(value))
                            print(" | ".join(formatted_row))

                        if len(rows) > 10:
                            print(f"... 还有 {len(rows) - 10} 行")
                        print(f"\n共返回 {len(rows)} 行")
                    else:
                        print("无结果")
                else:
                    conn.commit()
                    print(f"✅ 执行成功，影响行数: {cursor.rowcount}")

        except Exception as e:
            print(f"❌ 执行失败: {e}")

def main():
    """主函数"""
    print("\n" + "=" * 70)
    print(" 🗄️  Nof1 数据库查看工具")
    print("=" * 70)

    while True:
        print("\n请选择操作:")
        print("  1. 查看数据库概览")
        print("  2. 自定义 SQL 查询")
        print("  3. 退出")
        choice = input("\n请输入选择 (1-3): ").strip()

        if choice == '1':
            view_database()
        elif choice == '2':
            execute_sql()
        elif choice == '3':
            print("\n👋 再见！")
            break
        else:
            print("\n❌ 无效选择，请重试")

if __name__ == '__main__':
    main()
