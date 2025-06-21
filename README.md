# SQL Agent Web 🚀

**An intelligent web-based assistant for your SQLite databases.**

SQL Agent Web allows you to interact with your SQLite databases through an intuitive web interface. You can upload your database, view its schema, and query it using either raw SQL or natural language.

![SQL Agent Web Demo](https://user-images.githubusercontent.com/1234567/123456789-abcdef.gif) 
*(Demo GIF placeholder)*

---

## ✨ Features

*   **📤 Easy Database Upload:** Quickly upload your SQLite files (`.db`, `.sqlite`, `.sqlite3`) or CSV files.
*   **📂 CSV File Support:** Upload CSV files and have them automatically converted to SQLite format with multi-encoding support (UTF-8, Big5, GBK, Latin1, CP1252).
*   **📊 Schema Viewer:** Instantly view all your tables, their columns, and data types with interactive table information modals.
*   **📝 Sample Data Preview:** Get a quick peek at the first few rows of your tables.
*   **✏️ Direct SQL Execution:** Run any SQL query directly from your browser and see the results immediately.
*   **🤖 AI-Powered Queries:** Ask questions in plain English! Our SQL Agent translates your natural language into SQL queries using advanced AI.
*   **↔️ Compare Mode:** Execute both a raw SQL query and a natural language query side-by-side to compare the results with execution time analysis.
*   **🌐 Web-Based & User-Friendly:** Built with Flask and a modern, responsive Bootstrap 5 frontend.
*   **🐳 Docker Support:** Easy deployment with Docker for consistent environments.
*   **🚀 Real-time Results:** See query results and AI-generated SQL in real-time with loading indicators.

## 🛠️ Getting Started

You can run SQL Agent Web in two ways: **locally with Python** or **using Docker** (recommended for production).

### Option 1: Docker Deployment (Recommended) 🐳

#### Prerequisites
- Docker installed on your system
- Docker Compose (optional, for advanced setups)

#### Quick Start with Docker

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Chrisliao0806/sql_agent_web.git
   cd sql_agent_web
   ```

2. **Build the Docker image:**
   ```bash
   docker build -t sql_agent_web .
   ```

3. **Run the container:**
   ```bash
   docker run -d -p 5000:5000 --name sql_agent_web sql_agent_web
   ```

4. **Access the application:**
   Open your browser and navigate to `http://localhost:5000`

#### Docker Container Management

**Start the container:**
```bash
docker start sql_agent_web
```

**Stop the container:**
```bash
docker stop sql_agent_web
```

**View container logs:**
```bash
docker logs sql_agent_web
```

**Remove the container:**
```bash
docker stop sql_agent_web
docker rm sql_agent_web
```

**Rebuild after code changes:**
```bash
docker stop sql_agent_web
docker rm sql_agent_web
docker build -t sql_agent_web .
docker run -d -p 5000:5000 --name sql_agent_web sql_agent_web
```

#### Docker Compose (Alternative)

If you prefer using Docker Compose:

```bash
# Start the application
docker-compose up -d

# Stop the application
docker-compose down

# View logs
docker-compose logs -f

# Rebuild and restart
docker-compose up -d --build
```

### Option 2: Local Python Setup

#### Prerequisites
*   Python 3.10+
*   `pip` for package management

#### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Chrisliao0806/sql_agent_web.git
    cd sql_agent_web
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```bash
    python app.py
    ```

5.  **Open your browser** and navigate to `http://127.0.0.1:5000`.

## 🚀 How to Use

### Uploading Files
1. **SQLite Database Files:** Drag and drop or select your SQLite database file (`.db`, `.sqlite`, `.sqlite3`) on the main page.
2. **CSV Files:** Upload CSV files directly - they will be automatically converted to SQLite format with intelligent encoding detection.

### Exploring Your Data
3. **Database Overview:** You'll be redirected to the Database Info page where you can:
   - View all tables and their structures
   - See column information (names, types, constraints)
   - Preview sample data from each table
   - Click on any table card to get detailed information in a modal

### Querying and Analysis
4. **Compare Queries:** Click the "Compare Queries" button to access the dual-query interface:
   - **Left Panel (Traditional SQL):** Write standard SQL queries with syntax highlighting
   - **Right Panel (AI SQL Agent):** Ask questions in natural language
   - **Interactive Features:**
     - Click on table cards to get quick table information
     - Use the "Use this table" button to auto-generate SQL queries
     - View execution times and result comparisons
     - See AI-generated SQL alongside natural language results

### Example Queries

**Traditional SQL Examples:**
```sql
SELECT * FROM sales_data LIMIT 10;
SELECT 產品名稱, SUM(銷售數量) as 總銷量 FROM sales_data GROUP BY 產品名稱;
SELECT AVG(價格) as 平均價格 FROM sales_data;
```

**Natural Language Examples:**
- "顯示所有銷售資料"
- "哪個產品銷量最高？"
- "計算平均銷售價格"
- "Show me the top 5 best selling products"

## 📦 Deployment Notes

### Docker Production Tips

- The Docker image uses **Gunicorn** as the WSGI server for better production performance
- The application runs on port **5000** inside the container
- Database files are stored in the `/app/uploads` directory inside the container
- For persistent storage, consider mounting a volume:
  ```bash
  docker run -d -p 5000:5000 -v $(pwd)/uploads:/app/uploads --name sql_agent_web sql_agent_web
  ```

### Environment Variables

The following environment variables are available:

- `FLASK_ENV`: Set to `production` for production deployment (default in Docker)
- `FLASK_APP`: Application entry point (default: `app.py`)

## 🔧 Development

### Running Tests

```bash
# Local development
python -m pytest

# With Docker
docker run --rm sql_agent_web python -m pytest
```

### Development with Docker

For development with Docker and auto-reload:

```bash
# Mount source code as volume for development
docker run -d -p 5000:5000 -v $(pwd):/app --name sql_agent_web_dev sql_agent_web
```

## 🔮 Future Roadmap

The current AI agent is a simple simulation. The next big step is to integrate a real Large Language Model (LLM) to provide much more accurate and flexible natural language-to-SQL translation.

*   [ ] Integrate a real LLM (e.g., GPT, Llama, or a fine-tuned model).
*   [ ] Support for more database systems (PostgreSQL, MySQL).
*   [ ] User authentication and database management.
*   [ ] Charting and data visualization features.
*   [ ] Kubernetes deployment configurations.
*   [ ] Multi-container setup with Redis for session management.

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

---

# SQL Agent Web - 增強版

## 新增功能：CSV 文件支援

### 功能特色

1. **支援多種文件格式**：
   - SQLite 資料庫文件（.db, .sqlite, .sqlite3）
   - CSV 文件（.csv）- **新增功能**

2. **CSV 自動轉換**：
   - 自動將 CSV 文件轉換為 SQLite 格式
   - 支援多種編碼（UTF-8, Big5, GBK, Latin1）
   - 使用檔案名稱作為表格名稱

3. **智能查詢比較**：
   - 傳統 SQL 查詢
   - AI SQL Agent 自然語言查詢
   - 結果並排比較

### 使用步驟

1. **上傳文件**：
   - 選擇 SQLite 資料庫文件或 CSV 文件
   - 系統會自動識別文件類型

2. **CSV 處理**：
   - CSV 文件會自動轉換為 SQLite 格式
   - 轉換後的資料庫文件會保存在 uploads 目錄
   - 表格名稱為 CSV 檔案名稱（不含副檔名）

3. **查詢比較**：
   - 使用 SQL 語法進行精確查詢
   - 使用自然語言描述查詢需求
   - 比較兩種方式的結果和效能

### CSV 文件要求

- 第一行必須是欄位名稱（標題行）
- 支援常見的 CSV 格式
- 檔案大小限制：16MB
- 支援中文欄位名稱和內容

### 範例 CSV 格式

```csv
name,age,city,salary
張三,25,台北,50000
李四,30,高雄,60000
王五,28,台中,55000
```

### 技術實現

- **後端**：Flask + pandas + SQLite
- **前端**：Bootstrap 5 + JavaScript (Modern ES6+)
- **AI 功能**：LangChain + OpenAI GPT
- **CSV 處理**：pandas 自動編碼檢測和轉換 (支援UTF-8, Big5, GBK, Latin1, CP1252)
- **數據庫**：SQLite with PRAGMA optimizations
- **部署**：Docker + Gunicorn for production

## 🔧 Advanced Technical Features

### CSV Processing Pipeline
- **Multi-encoding Detection:** Automatically detects and handles various character encodings
- **Column Name Sanitization:** Cleans column names to be SQL-compatible
- **Data Type Inference:** Intelligent data type detection and conversion
- **Error Handling:** Comprehensive error handling with user-friendly messages

### AI SQL Agent
- **Natural Language Processing:** Uses advanced NLP to understand user queries
- **SQL Generation:** Automatically generates optimized SQL queries
- **Context Awareness:** Understands database schema and provides contextual responses
- **Multi-language Support:** Supports both English and Chinese queries

### Performance Optimizations
- **Lazy Loading:** Database connections are created on-demand
- **Query Caching:** Intelligent caching of frequently used queries
- **Asynchronous Operations:** Non-blocking file uploads and processing
- **Responsive Design:** Mobile-first responsive interface

### 安裝依賴

```bash
pip install -r requirements.txt
```

### 運行應用

```bash
python app.py
```

應用將在 http://localhost:5000 啟動

---

## 原有功能