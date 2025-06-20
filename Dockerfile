FROM python:3.12-slim

WORKDIR /app

# 安裝系統依賴和編譯工具
RUN apt-get update && apt-get install -y \
    sqlite3 \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 複製需求文件並安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 安裝生產級 WSGI 服務器
RUN pip install gunicorn

# 複製應用程式代碼
COPY . .

# 創建上傳目錄
RUN mkdir -p uploads

# 設置環境變數
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# 暴露端口
EXPOSE 5000

# 使用 gunicorn 運行應用
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]