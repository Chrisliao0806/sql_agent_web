#!/bin/bash

# SQL Agent Web 一鍵啟動腳本
echo "🚀 正在啟動 SQL Agent Web..."

# 檢查 Docker 是否運行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未運行，請先啟動 Docker Desktop"
    exit 1
fi

# 啟動服務
docker-compose up -d --build

echo ""
echo "✅ SQL Agent Web 已成功啟動！"
echo ""
echo "📄 服務狀態："
docker-compose ps
echo ""
echo "🌐 訪問地址："
echo "   - 直接訪問: http://localhost:5000"
echo "   - 通過 Nginx: http://localhost:80"
echo ""
echo "📝 常用命令："
echo "   - 查看日誌: docker-compose logs -f"
echo "   - 停止服務: docker-compose down"
echo "   - 重啟服務: docker-compose restart"
echo ""
