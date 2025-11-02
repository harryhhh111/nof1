"""
Nof1 数据获取系统主程序

主程序入口，提供数据获取、定时更新和查询功能。
"""

import argparse
import json
import sys
import logging
from typing import List, Optional
from datetime import datetime

from data_fetcher import DataFetcher
from scheduler import DataScheduler
from database import Database
from config import SYMBOLS, UPDATE_INTERVAL, LOG_LEVEL, LOG_FORMAT

# 配置日志
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('nof1.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)


def fetch_single_symbol(symbol: str, output_format: str = 'json'):
    """
    获取单个交易对数据

    Args:
        symbol: 交易对符号
        output_format: 输出格式 ('json', 'print')
    """
    try:
        fetcher = DataFetcher()
        data = fetcher.get_market_data(symbol)
        fetcher.close()

        if output_format == 'json':
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"\n=== {symbol} 市场数据 ===")
            print(f"当前价格: ${data['current_price']:,.2f}")
            print(f"时间戳: {data['timestamp']}")
            print(f"\n=== 日内数据 (3分钟) ===")
            print(f"价格范围: ${min(data['intraday']['prices']):,.2f} - ${max(data['intraday']['prices']):,.2f}")
            print(f"最新 EMA20: {data['intraday']['ema20'][-1]:.2f if data['intraday']['ema20'] else 'N/A'}")
            print(f"最新 MACD: {data['intraday']['macd'][-1]:.2f if data['intraday']['macd'] else 'N/A'}")
            print(f"最新 RSI7: {data['intraday']['rsi_7'][-1]:.2f if data['intraday']['rsi_7'] else 'N/A'}")
            print(f"最新 RSI14: {data['intraday']['rsi_14'][-1]:.2f if data['intraday']['rsi_14'] else 'N/A'}")
            print(f"\n=== 长期数据 (4小时) ===")
            print(f"EMA20: {data['long_term']['ema_20']:.2f if data['long_term']['ema_20'] else 'N/A'}")
            print(f"EMA50: {data['long_term']['ema_50']:.2f if data['long_term']['ema_50'] else 'N/A'}")
            print(f"ATR3: {data['long_term']['atr_3']:.2f if data['long_term']['atr_3'] else 'N/A'}")
            print(f"ATR14: {data['long_term']['atr_14']:.2f if data['long_term']['atr_14'] else 'N/A'}")
            print(f"当前交易量: {data['long_term']['volume_current']:.2f if data['long_term']['volume_current'] else 'N/A'}")
            print(f"平均交易量: {data['long_term']['volume_average']:.2f if data['long_term']['volume_average'] else 'N/A'}")
            print(f"\n=== 永续合约数据 ===")
            print(f"资金费率: {data['perp_data']['funding_rate']:.6f}" if data['perp_data']['funding_rate'] else "资金费率: N/A")
            print(f"开放利息: {data['perp_data']['open_interest_latest']:.2f}" if data['perp_data']['open_interest_latest'] else "开放利息: N/A")

        return data

    except Exception as e:
        logger.error(f"获取 {symbol} 数据失败: {e}")
        return None


def fetch_multiple_symbols(symbols: List[str], output_format: str = 'json'):
    """
    获取多个交易对数据

    Args:
        symbols: 交易对符号列表
        output_format: 输出格式 ('json', 'print')
    """
    try:
        fetcher = DataFetcher()
        data = fetcher.get_multiple_symbols_data(symbols)
        fetcher.close()

        if output_format == 'json':
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            for symbol, market_data in data.items():
                print(f"\n{'='*50}")
                print(f"  {symbol}")
                print(f"{'='*50}")
                print(f"当前价格: ${market_data['current_price']:,.2f}")
                print(f"时间戳: {market_data['timestamp']}")
                print(f"资金费率: {market_data['perp_data']['funding_rate']:.6f}" if market_data['perp_data']['funding_rate'] else "资金费率: N/A")

        return data

    except Exception as e:
        logger.error(f"获取多个交易对数据失败: {e}")
        return None


def start_scheduler(symbols: Optional[List[str]] = None,
                    update_interval: Optional[int] = None):
    """
    启动数据更新调度器

    Args:
        symbols: 交易对符号列表
        update_interval: 更新间隔（秒）
    """
    logger.info("启动 Nof1 数据获取系统调度器...")
    scheduler = DataScheduler(symbols, update_interval)
    scheduler.start()


def query_latest_data(symbols: List[str], output_format: str = 'json'):
    """
    查询数据库中的最新数据

    Args:
        symbols: 交易对符号列表
        output_format: 输出格式 ('json', 'print')
    """
    try:
        db = Database()

        if output_format == 'json':
            result = {}
            for symbol in symbols:
                data = db.get_latest_data(symbol)
                if data:
                    result[symbol] = data
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            for symbol in symbols:
                data = db.get_latest_data(symbol)
                if data:
                    print(f"\n{'='*50}")
                    print(f"  {symbol} (来自数据库)")
                    print(f"{'='*50}")
                    print(f"当前价格: ${data['current_price']:,.2f}")
                    print(f"时间戳: {data['timestamp']}")
                    print(f"EMA20: {data['long_term']['ema_20']:.2f}" if data['long_term']['ema_20'] else "EMA20: N/A")
                    print(f"EMA50: {data['long_term']['ema_50']:.2f}" if data['long_term']['ema_50'] else "EMA50: N/A")
                    print(f"RSI14: {data['long_term']['rsi_14']:.2f}" if data['long_term']['rsi_14'] else "RSI14: N/A")
                    print(f"资金费率: {data['perp_data']['funding_rate']:.6f}" if data['perp_data']['funding_rate'] else "资金费率: N/A")
                else:
                    print(f"\n{symbol}: 暂无数据")

        db.close()

    except Exception as e:
        logger.error(f"查询最新数据失败: {e}")


def show_status():
    """显示系统状态"""
    try:
        db = Database()
        print("\n=== Nof1 数据获取系统状态 ===")
        print(f"数据库路径: {db.db_path}")
        print(f"监控交易对: {', '.join(SYMBOLS)}")
        print(f"更新间隔: {UPDATE_INTERVAL} 秒")
        print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 显示数据库中的记录数
        import sqlite3
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM klines_3m")
            klines_3m_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM klines_4h")
            klines_4h_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM technical_indicators")
            indicators_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM perpetual_data")
            perp_count = cursor.fetchone()[0]

            print(f"\n数据库记录数:")
            print(f"  3分钟 K 线: {klines_3m_count:,} 条")
            print(f"  4小时 K 线: {klines_4h_count:,} 条")
            print(f"  技术指标: {indicators_count:,} 条")
            print(f"  永续合约数据: {perp_count:,} 条")

        db.close()

    except Exception as e:
        logger.error(f"显示系统状态失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Nof1 数据获取系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 获取单个交易对数据
  python main.py --symbol BTCUSDT

  # 获取多个交易对数据
  python main.py --symbols BTCUSDT ETHUSDT SOLUSDT

  # 启动定时调度器
  python main.py --schedule

  # 启动调度器并指定交易对
  python main.py --schedule --symbols BTCUSDT ETHUSDT --interval 60

  # 查询数据库中的最新数据
  python main.py --query --symbols BTCUSDT

  # 显示系统状态
  python main.py --status
        """
    )

    parser.add_argument('--symbol', type=str, help='单个交易对符号 (如 BTCUSDT)')
    parser.add_argument('--symbols', nargs='+', help='多个交易对符号')
    parser.add_argument('--schedule', action='store_true', help='启动定时调度器')
    parser.add_argument('--query', action='store_true', help='查询数据库中的最新数据')
    parser.add_argument('--status', action='store_true', help='显示系统状态')
    parser.add_argument('--interval', type=int, help='更新间隔 (秒)')
    parser.add_argument('--output', type=str, choices=['json', 'print'],
                       default='json', help='输出格式 (默认: json)')

    args = parser.parse_args()

    # 如果没有指定任何参数，显示帮助
    if not any(vars(args).values()):
        parser.print_help()
        return

    try:
        # 显示系统状态
        if args.status:
            show_status()

        # 获取单个交易对数据
        elif args.symbol:
            fetch_single_symbol(args.symbol, args.output)

        # 获取多个交易对数据
        elif args.symbols:
            fetch_multiple_symbols(args.symbols, args.output)

        # 查询最新数据
        elif args.query:
            symbols = args.symbols if args.symbols else SYMBOLS
            query_latest_data(symbols, args.output)

        # 启动定时调度器
        elif args.schedule:
            symbols = args.symbols if args.symbols else SYMBOLS
            interval = args.interval if args.interval else UPDATE_INTERVAL
            start_scheduler(symbols, interval)

    except KeyboardInterrupt:
        logger.info("程序已中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
