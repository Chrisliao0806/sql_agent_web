#!/bin/bash

# SQL Agent Web 狀態檢查腳本
echo "📊 SQL Agent Web 服務狀態"
echo "========================================"

# 檢查 Docker 狀態
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未運行"
    exit 1
fi

echo "✅ Docker 正在運行"
echo ""

# 檢查容器狀態
echo "🐳 容器狀態："
docker-compose ps

echo ""
echo "📋 日誌預覽 (最後 10 行)："
echo "----------------------------------------"
docker-compose logs --tail=10

echo ""
echo "🌐 訪問地址："
echo "   - 直接訪問: http://localhost:5000"
echo "   - 通過 Nginx: http://localhost:80"
echo ""
