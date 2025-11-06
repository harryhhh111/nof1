#!/bin/bash
# 定期监控交易系统 - 每5分钟检查一次

echo "🔄 启动定期交易监控系统 (每5分钟)..."
echo "按 Ctrl+C 停止"
echo ""

while true; do
    clear
    echo "═══════════════════════════════════════════════════════"
    echo "  📊 Nof1 交易系统 - $(date '+%Y-%m-%d %H:%M:%S')"
    echo "═══════════════════════════════════════════════════════"
    echo ""
    
    # 1. 系统状态
    echo "📊 系统进程:"
    ps aux | grep -E "data_collector|run_full_system|run_api" | grep -v grep | awk '{print "  ✅", $2, $11, $12, "(" $9 ")"}' 2>/dev/null || echo "  ⚠️ 进程检查中..."
    echo ""
    
    # 2. Testnet余额
    echo "💰 Testnet余额:"
    python3 -c "
from trading.testnet_trader import TestnetTrader
try:
    t = TestnetTrader()
    bal = t.get_account_balance()
    for k, v in sorted(bal.items(), key=lambda x: x[1], reverse=True)[:6]:
        print(f'  {k:10s}: {v:15.4f}')
except Exception as e:
    print('  ⚠️ 暂时无法获取余额')
" 2>/dev/null
    echo ""
    
    # 3. 最新交易
    echo "📈 最新交易决策 (3条):"
    curl -s "http://localhost:8000/api/v1/decisions?limit=3" 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for item in data['data']:
        print(f'  {item[\"symbol\"]:10s} {item[\"action\"]:5s} 置信度: {item[\"confidence\"]:5.1f}% 时间: {item[\"timestamp\"][:19]}')
except:
    print('  ⚠️ 暂时无法获取决策记录')
" 2>/dev/null
    echo ""
    
    # 4. 数据库统计
    echo "🗄️ 数据收集:"
    python3 -c "
import sqlite3
try:
    conn = sqlite3.connect('market_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM klines_3m')
    count = cursor.fetchone()[0]
    cursor.execute('SELECT MAX(timestamp) FROM klines_3m')
    ts = cursor.fetchone()[0]
    from datetime import datetime
    print(f'  K线记录: {count:,} 条')
    if ts:
        print(f'  最新时间: {datetime.fromtimestamp(ts/1000).strftime(\"%H:%M:%S\")}')
    conn.close()
except:
    print('  ⚠️ 数据库查询失败')
" 2>/dev/null
    echo ""
    
    # 5. 性能统计
    echo "📊 性能统计:"
    curl -s "http://localhost:8000/api/v1/stats/summary" 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f'  总交易: {data.get(\"total_trades\", 0)} 次')
    print(f'  胜率: {data.get(\"win_rate\", 0):.1f}%')
    print(f'  总PnL: ${data.get(\"total_pnl\", 0):.2f}')
except:
    print('  ⚠️ 暂时无法获取统计')
" 2>/dev/null
    echo ""
    
    echo "═══════════════════════════════════════════════════════"
    echo "  🌐 Web界面: http://localhost:8000/docs"
    echo "  🌐 Testnet: https://testnet.binance.vision/"
    echo "═══════════════════════════════════════════════════════"
    echo ""
    echo "⏳ 5分钟后自动刷新... (按 Ctrl+C 退出)"
    
    sleep 300  # 5分钟
done
