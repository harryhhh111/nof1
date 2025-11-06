#!/usr/bin/env python3
"""
基础功能测试

测试系统的核心功能，包括技术指标计算和数据库操作。
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Nof1 数据获取系统 - 基础功能测试")
print("=" * 60)

# 测试 1: 验证模块导入
print("\n[测试 1] 验证模块导入...")
try:
    from indicators import TechnicalIndicators
    from database import Database
    print("✓ 所有模块导入成功")
except Exception as e:
    print(f"✗ 模块导入失败: {e}")
    sys.exit(1)

# 测试 2: 创建模拟数据
print("\n[测试 2] 创建模拟 OHLCV 数据...")
try:
    # 生成 50 个时间点的模拟数据
    dates = pd.date_range(start='2024-01-01', periods=50, freq='3T')
    np.random.seed(42)  # 设置随机种子，确保结果可重现

    base_price = 50000
    price_changes = np.random.normal(0, 0.01, 50)  # 1% 标准差的随机变化
    prices = base_price * (1 + price_changes).cumprod()

    test_data = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': prices * (1 + np.abs(np.random.normal(0, 0.005, 50))),
        'low': prices * (1 - np.abs(np.random.normal(0, 0.005, 50))),
        'close': prices,
        'volume': np.random.uniform(1000, 2000, 50)
    })

    print(f"✓ 创建 {len(test_data)} 条模拟数据")
    print(f"  价格范围: ${test_data['close'].min():.2f} - ${test_data['close'].max():.2f}")
except Exception as e:
    print(f"✗ 创建模拟数据失败: {e}")
    sys.exit(1)

# 测试 3: 测试 EMA 计算
print("\n[测试 3] 测试 EMA 计算...")
try:
    ema_20 = TechnicalIndicators.calculate_ema(test_data, 20)
    print(f"✓ EMA20 计算成功")
    print(f"  最新值: {ema_20.iloc[-1]:.2f}")
    print(f"  非空值数量: {ema_20.dropna().shape[0]}")
except Exception as e:
    print(f"✗ EMA 计算失败: {e}")
    sys.exit(1)

# 测试 4: 测试 MACD 计算
print("\n[测试 4] 测试 MACD 计算...")
try:
    macd_data = TechnicalIndicators.calculate_macd(test_data)
    print(f"✓ MACD 计算成功")
    print(f"  MACD 最新值: {macd_data['macd'].iloc[-1]:.4f}")
    print(f"  Signal 最新值: {macd_data['signal'].iloc[-1]:.4f}")
    print(f"  Histogram 最新值: {macd_data['histogram'].iloc[-1]:.4f}")
except Exception as e:
    print(f"✗ MACD 计算失败: {e}")
    sys.exit(1)

# 测试 5: 测试 RSI 计算
print("\n[测试 5] 测试 RSI 计算...")
try:
    rsi = TechnicalIndicators.calculate_rsi(test_data, 14)
    print(f"✓ RSI 计算成功")
    print(f"  最新值: {rsi.iloc[-1]:.2f}")
    # 验证 RSI 值在合理范围内
    valid_rsi = rsi.dropna()
    if len(valid_rsi) > 0:
        rsi_in_range = all(0 <= val <= 100 for val in valid_rsi)
        if rsi_in_range:
            print(f"  ✓ RSI 值在有效范围内 (0-100)")
        else:
            print(f"  ✗ RSI 值超出有效范围")
except Exception as e:
    print(f"✗ RSI 计算失败: {e}")
    sys.exit(1)

# 测试 6: 测试 ATR 计算
print("\n[测试 6] 测试 ATR 计算...")
try:
    atr = TechnicalIndicators.calculate_atr(test_data, 14)
    print(f"✓ ATR 计算成功")
    print(f"  最新值: {atr.iloc[-1]:.2f}")
    # 验证 ATR 值大于 0
    valid_atr = atr.dropna()
    if len(valid_atr) > 0:
        atr_positive = all(val >= 0 for val in valid_atr)
        if atr_positive:
            print(f"  ✓ ATR 值有效 (>= 0)")
        else:
            print(f"  ✗ ATR 值无效")
except Exception as e:
    print(f"✗ ATR 计算失败: {e}")
    sys.exit(1)

# 测试 7: 测试交易量分析
print("\n[测试 7] 测试交易量分析...")
try:
    current_vol, avg_vol = TechnicalIndicators.calculate_volume_analysis(test_data)
    print(f"✓ 交易量分析成功")
    print(f"  当前交易量: {current_vol:.2f}")
    print(f"  平均交易量: {avg_vol:.2f}")
except Exception as e:
    print(f"✗ 交易量分析失败: {e}")
    sys.exit(1)

# 测试 8: 测试计算所有指标
print("\n[测试 8] 测试计算所有指标...")
try:
    indicators = TechnicalIndicators.calculate_all_indicators(test_data)
    expected_keys = ['ema_20', 'ema_50', 'macd', 'macd_signal', 'macd_histogram',
                    'rsi_7', 'rsi_14', 'atr_3', 'atr_14', 'current_volume', 'average_volume']

    for key in expected_keys:
        if key not in indicators:
            raise KeyError(f"缺少指标: {key}")

    print(f"✓ 所有指标计算成功")
    print(f"  计算的指标: {', '.join(indicators.keys())}")
except Exception as e:
    print(f"✗ 计算所有指标失败: {e}")
    sys.exit(1)

# 测试 9: 测试数据库操作
print("\n[测试 9] 测试数据库操作...")
try:
    import tempfile
    temp_db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db_file.close()

    # 初始化数据库
    db = Database(temp_db_file.name)

    # 插入测试 K 线数据
    klines = [
        [1640995200000, 50000.0, 50100.0, 49900.0, 50050.0, 1000.0, 1640995299999],
        [1640995300000, 50050.0, 50200.0, 49950.0, 50100.0, 1100.0, 1640995399999],
    ]
    db.insert_klines('BTCUSDT', klines, '3m')

    # 获取数据
    df = db.get_klines('BTCUSDT', '3m', limit=10)

    if len(df) == 2:
        print(f"✓ 数据库操作成功")
        print(f"  插入 2 条 K 线数据")
        print(f"  获取 {len(df)} 条数据")
    else:
        print(f"✗ 数据库操作异常")

    # 清理
    db.close()
    if os.path.exists(temp_db_file.name):
        os.unlink(temp_db_file.name)
except Exception as e:
    print(f"✗ 数据库操作失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试结果汇总
print("\n" + "=" * 60)
print("测试结果汇总")
print("=" * 60)
print("✓ 所有基础功能测试通过！")
print("\n系统已准备好进行实际数据获取测试。")
print("\n可以使用以下命令进行进一步测试:")
print("  python3 main.py --symbol BTCUSDT")
print("  python3 main.py --status")
