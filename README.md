# SQL Agent Web 🚀

**An intelligent web-based assistant for your SQLite databases.**

SQL Agent Web allows you to interact with your SQLite databases through an intuitive web interface. You can upload your database, view its schema, and query it using either raw SQL or natural language.

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

## 🛠️ Getting Started

### Prerequisites

- **For AI Features:** OpenAI API key (required for natural language queries)
- **For Docker:** Docker installed on your system
- **For Local Setup:** Python 3.10+ and pip

### Environment Configuration

Create a `.env` file in the project root directory with your OpenAI API key:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

**Important:** Without the OpenAI API key, the AI-powered natural language queries will not work. You can still use the traditional SQL query functionality.

### Option 1: Docker Deployment (Recommended) 🐳

#### Quick Start with Docker

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Chrisliao0806/sql_agent_web.git
   cd sql_agent_web
   ```

2. **Set up environment variables:**
   Create a `.env` file with your OpenAI API key (see Environment Configuration above)

3. **Start with one command:**
   ```bash
   ./start.sh
   ```
   
   Or manually:
   ```bash
   docker-compose up -d --build
   ```

4. **Access the application:**
   - Direct access: `http://localhost:5000`
   - Through Nginx: `http://localhost:80`

#### Quick Management Commands

```bash
# Start the application
./start.sh

# Stop the application  
./stop.sh

# Check status
./status.sh

# View logs
docker-compose logs -f
```

### Option 2: Local Python Setup

1. **Clone and setup:**
   ```bash
   git clone https://github.com/Chrisliao0806/sql_agent_web.git
   cd sql_agent_web
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file with your OpenAI API key (see Environment Configuration above)

5. **Run the application:**
   ```bash
   python app.py
   ```

6. **Open your browser** and navigate to `http://127.0.0.1:5000`

## 🚀 How to Use

### 1. Upload Files
- **SQLite Database Files:** Upload `.db`, `.sqlite`, or `.sqlite3` files
- **CSV Files:** Upload CSV files for automatic conversion to SQLite format

### 2. Explore Your Data
- View database schema and table structures
- Preview sample data from each table
- Click table cards for detailed information

### 3. Query and Analyze
- **Compare Queries:** Access dual-query interface with:
  - **Left Panel:** Traditional SQL queries with syntax highlighting
  - **Right Panel:** AI-powered natural language queries
- View execution times and compare results
- See AI-generated SQL alongside natural language results

### Example Queries

**Traditional SQL:**
```sql
SELECT * FROM sales_data LIMIT 10;
SELECT 產品名稱, SUM(銷售數量) as 總銷量 FROM sales_data GROUP BY 產品名稱;
SELECT AVG(價格) as 平均價格 FROM sales_data;
```

**Natural Language:**
- "顯示所有銷售資料"
- "哪個產品銷量最高？"
- "計算平均銷售價格"
- "Show me the top 5 best selling products"

## 📦 Production Notes

### Docker Production Features
- Uses **Gunicorn** WSGI server for production performance
- Application runs on port **5000** inside container
- For persistent storage, mount uploads volume:
  ```bash
  docker run -d -p 5000:5000 -v $(pwd)/uploads:/app/uploads --name sql_agent_web sql_agent_web
  ```

### Environment Variables
- `OPENAI_API_KEY`: Required for AI functionality
- `FLASK_ENV`: Set to `production` for production deployment
- `FLASK_APP`: Application entry point (default: `app.py`)

## 🔮 Future Roadmap

*   [ ] Support for more database systems (PostgreSQL, MySQL)
*   [ ] User authentication and database management
*   [ ] Data visualization and charting features
*   [ ] Kubernetes deployment configurations
*   [ ] Multi-container setup with Redis for session management

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.