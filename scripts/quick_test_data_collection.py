#!/usr/bin/env python3
"""
快速数据收集测试脚本

测试数据收集系统是否正常工作，仅获取一次数据进行验证。
"""

import sys
import os
import logging
from datetime import datetime

# 添加项目根目录
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database

from data_fetcher import DataFetcher

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_data_collection():
    """测试数据收集功能"""
    print("=" * 80)
    print("  🔍 Nof1 数据收集系统快速测试")
    print("=" * 80)

    try:
        # 1. 测试数据获取器
        print("\n📡 测试数据获取器...")
        fetcher = DataFetcher()
        print("  ✅ 数据获取器初始化成功")

        # 2. 获取BTC数据
        print("\n📊 获取 BTCUSDT 市场数据...")
        data = fetcher.get_market_data('BTCUSDT')

        if data:
            print(f"  ✅ 数据获取成功！")
            print(f"    - 当前价格: ${data['current_price']:,.2f}")
            print(f"    - 时间戳: {data['timestamp']}")
            print(f"    - 数据表结构:")
            print(f"      • 日内数据 (3m): {len(data.get('intraday', {}).get('prices', []))} 个数据点")
            print(f"      • 长期数据 (4h): EMA20={data.get('long_term', {}).get('ema_20', 'N/A')}")
            print(f"      • 永续合约: 资金费率={data.get('perp_data', {}).get('funding_rate', 'N/A')}")
        else:
            print("  ❌ 数据获取失败")
            return False

        fetcher.close()
        print("  🔌 数据获取器已关闭")

        # 3. 测试数据库
        print("\n💾 测试数据库操作...")
        db = Database()

        # 获取最新数据
        latest = db.get_latest_data('BTCUSDT')
        if latest:
            print("  ✅ 数据库读取成功")
            print(f"    - 最新记录时间: {latest.get('timestamp', 'N/A')}")
        else:
            print("  ⚠️  数据库暂无数据（正常现象，这是第一次运行）")

        db.close()
        print("  💾 数据库连接已关闭")

        print("\n" + "=" * 80)
        print("  ✅ 所有测试通过！数据收集系统工作正常")
        print("=" * 80)
        print("\n💡 接下来您可以:")
        print("   1. 运行: python3 data_collector_only.py")
        print("   2. 或运行: python3 main.py --schedule")
        print("   3. 查看数据: python3 quick_query.py latest")

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        logger.error(f"测试失败: {e}", exc_info=True)
        return False


if __name__ == '__main__':
    success = test_data_collection()
    sys.exit(0 if success else 1)
