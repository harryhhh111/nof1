#!/bin/bash
echo "测试不同的 Binance API URL..."
echo ""

echo "1. 测试 api.binance.com (真实交易):"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" https://api.binance.com/api/v3/time
echo ""

echo "2. 测试 testnet.binance.vision (测试环境):"
curl -s https://testnet.binance.vision/api/v3/time | head -c 100
echo ""
echo ""

echo "3. 测试 demo.binance.vision (不存在):"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" https://demo.binance.vision/api/v3/time
echo ""

echo "==================================="
echo "结论: 正确的 Base URL 是:"
echo "  - 真实交易: https://api.binance.com"
echo "  - 测试环境: https://testnet.binance.vision"
echo "  - demo.binance.vision 不存在"
echo "==================================="
