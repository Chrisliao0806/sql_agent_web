# SQL Agent Web 🚀

**An intelligent web-based assistant for your SQLite databases.**

SQL Agent Web allows you to interact with your SQLite databases through an intuitive web interface. You can upload your database, view its schema, and query it using either raw SQL or natural language.

![SQL Agent Web Demo](https://user-images.githubusercontent.com/1234567/123456789-abcdef.gif) 
*(Demo GIF placeholder)*

---

## ✨ Features

*   **📤 Easy Database Upload:** Quickly upload your SQLite files (`.db`, `.sqlite`, `.sqlite3`).
*   **📊 Schema Viewer:** Instantly view all your tables, their columns, and data types.
*   **📝 Sample Data Preview:** Get a quick peek at the first few rows of your tables.
*   **✏️ Direct SQL Execution:** Run any SQL query directly from your browser and see the results immediately.
*   **🤖 AI-Powered Queries (Simulated):** Ask questions in plain English! Our "SQL Agent" translates your natural language into SQL queries.
*   **↔️ Compare Mode:** Execute both a raw SQL query and a natural language query side-by-side to compare the results.
*   **🌐 Web-Based & User-Friendly:** Built with Flask and a clean, intuitive frontend.

## 🛠️ Getting Started

### Prerequisites

*   Python 3.10+
*   `pip` for package management

### Installation & Setup

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

1.  **Upload:** Drag and drop or select your SQLite database file on the main page.
2.  **Explore:** You'll be redirected to the Database Info page, where you can see all the tables and their structures.
3.  **Query:**
    *   Click on the "Compare Queries" button.
    *   On the left, write a standard SQL query.
    *   On the right, type a question in natural language (e.g., "Show me all users" or "How many products are there?").
    *   See the results and the AI-generated SQL appear instantly!

## 🔮 Future Roadmap

The current AI agent is a simple simulation. The next big step is to integrate a real Large Language Model (LLM) to provide much more accurate and flexible natural language-to-SQL translation.

*   [ ] Integrate a real LLM (e.g., GPT, Llama, or a fine-tuned model).
*   [ ] Support for more database systems (PostgreSQL, MySQL).
*   [ ] User authentication and database management.
*   [ ] Charting and data visualization features.

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.