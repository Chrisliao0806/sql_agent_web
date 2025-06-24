#!/bin/bash

# SQL Agent Web 一鍵關閉腳本
echo "🛑 正在關閉 SQL Agent Web..."

# 關閉服務
docker-compose down

echo ""
echo "✅ SQL Agent Web 已成功關閉！"
echo ""
echo "📊 清理狀態："
echo "   - 容器已停止並移除"
echo "   - 網絡已移除"
echo "   - 數據卷已保留 (uploads 目錄)"
echo ""
echo "🔄 重新啟動:"
echo "   - 運行 './start.sh' 或 'docker-compose up -d'"
echo ""
