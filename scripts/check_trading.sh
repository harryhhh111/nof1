#!/bin/bash
echo "═══════════════════════════════════════════════════════"
echo "  📈 Nof1 交易系统状态监控"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "🕐 当前时间: $(date)"
echo ""

echo "📊 系统进程:"
ps aux | grep -E "data_collector|run_full_system|run_api.py" | grep -v grep | awk '{print "  ✅", $2, $11, $12, "(" $9 ")"}'
echo ""

echo "🗄️ 数据库统计:"
python3 scripts/quick_query.py summary 2>/dev/null | grep -E "klines|指标|perpetual" | head -4
echo ""

echo "💰 Testnet余额:"
python3 -c "
from trading.testnet_trader import TestnetTrader
try:
    t = TestnetTrader()
    bal = t.get_account_balance()
    for k, v in list(bal.items())[:5]:
        print(f'  {k:10s}: {v:15.4f}')
except Exception as e:
    print('  ⚠️ 暂时无法获取余额:', str(e)[:50])
" 2>/dev/null
echo ""

echo "📈 最新数据时间:"
python3 -c "
import sqlite3
from datetime import datetime
try:
    conn = sqlite3.connect('market_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT MAX(timestamp) FROM klines_3m')
    ts = cursor.fetchone()[0]
    if ts:
        print('  3分钟K线:', datetime.fromtimestamp(ts/1000).strftime('%Y-%m-%d %H:%M:%S'))
    conn.close()
except:
    print('  ⚠️ 数据库查询失败')
"
echo ""

echo "📝 最新日志 (5行):"
tail -3 logs/trading_infinity.log 2>/dev/null | grep -E "完成|性能|交易" | head -3
echo ""

echo "═══════════════════════════════════════════════════════"
echo "  🌐 Web界面: http://localhost:8000/docs"
echo "  🌐 Testnet: https://testnet.binance.vision/"
echo "═══════════════════════════════════════════════════════"
