#!/bin/bash

echo "🚀 開始部署 SQL Agent Web 應用..."

# 檢查 Docker 是否安裝
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安裝，請先安裝 Docker"
    exit 1
fi

# 檢查 Docker Compose 是否安裝
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安裝，請先安裝 Docker Compose"
    exit 1
fi

# 停止現有的容器（如果有的話）
echo "🛑 停止現有容器..."
docker-compose down

# 構建並啟動服務
echo "🔨 構建並啟動服務..."
docker-compose up --build -d

# 檢查服務狀態
echo "📊 檢查服務狀態..."
docker-compose ps

# 顯示日誌
echo "📝 顯示服務日誌..."
docker-compose logs --tail=50

echo "✅ 部署完成！"
echo "🌐 你的應用現在可以通過以下方式訪問："
echo "   - 本地訪問: http://localhost"
echo "   - 局域網訪問: http://[你的IP地址]"
echo ""
echo "💡 要查看即時日誌，請運行: docker-compose logs -f"
echo "💡 要停止服務，請運行: docker-compose down"