from flask import Flask, request, render_template, jsonify, redirect, url_for, flash
import sqlite3
import os
from werkzeug.utils import secure_filename
from services.sql_agent import SQLAgent

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size

# 確保上傳資料夾存在
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# 允許的文件類型
ALLOWED_EXTENSIONS = {"db", "sqlite", "sqlite3"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_table_info(db_path):
    """獲取資料庫中所有表格的資訊"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 獲取所有表格名稱
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    table_info = {}
    for table in tables:
        table_name = table[0]
        # 獲取表格結構
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()

        # 獲取前5行數據作為示例
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
        sample_data = cursor.fetchall()

        table_info[table_name] = {"columns": columns, "sample_data": sample_data}

    conn.close()
    return table_info


def execute_sql_query(db_path, query):
    """執行SQL查詢並返回結果"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query)

        # 獲取列名
        columns = (
            [description[0] for description in cursor.description]
            if cursor.description
            else []
        )

        # 獲取數據
        results = cursor.fetchall()
        conn.close()

        return {
            "success": True,
            "columns": columns,
            "data": results,
            "row_count": len(results),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        flash("沒有選擇文件")
        return redirect(request.url)

    file = request.files["file"]
    if file.filename == "":
        flash("沒有選擇文件")
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # 獲取資料庫資訊
        table_info = get_table_info(filepath)

        return render_template(
            "database_info.html", filename=filename, table_info=table_info
        )
    else:
        flash("請上傳有效的資料庫文件 (.db, .sqlite, .sqlite3)")
        return redirect(request.url)


@app.route("/compare/<filename>")
def compare_queries(filename):
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if not os.path.exists(filepath):
        flash("資料庫文件不存在")
        return redirect(url_for("index"))

    table_info = get_table_info(filepath)
    return render_template("compare.html", filename=filename, table_info=table_info)


@app.route("/api/sql_query", methods=["POST"])
def api_sql_query():
    data = request.json
    filename = data.get("filename")
    query = data.get("query")

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if not os.path.exists(filepath):
        return jsonify({"success": False, "error": "資料庫文件不存在"})

    result = execute_sql_query(filepath, query)
    return jsonify(result)


@app.route("/api/agent_query", methods=["POST"])
def api_agent_query():
    data = request.json
    filename = data.get("filename")
    natural_query = data.get("query")

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if not os.path.exists(filepath):
        return jsonify({"success": False, "error": "資料庫文件不存在"})

    try:
        # 建立 SQLAgent 實例，使用 sqlite:/// 格式的 URI
        db_uri = f"sqlite:///{filepath}"
        sql_agent = SQLAgent(db_uri)

        # 使用 SQLAgent 處理自然語言查詢
        agent_result = sql_agent.run(natural_query)
        print("Agent Result:", agent_result)
        
        # 如果有生成的SQL，執行它來獲取實際的查詢結果
        sql_query_result = None
        if agent_result.get("query") and agent_result.get("query") != "查無結果":
            sql_query_result = execute_sql_query(filepath, agent_result.get("query"))
        
        # 格式化回應
        result = {
            "success": True,
            "generated_sql": agent_result.get("query", ""),
            "natural_query": natural_query,
            "generation": agent_result.get("generation", ""),
            "sql_result": agent_result.get("result", "")
        }
        
        # 如果有SQL查詢結果，添加表格資料
        if sql_query_result and sql_query_result.get("success"):
            result.update({
                "data": sql_query_result.get("data", []),
                "columns": sql_query_result.get("columns", []),
                "row_count": sql_query_result.get("row_count", 0)
            })
        else:
            result.update({
                "data": [],
                "columns": [],
                "row_count": 0
            })

        return jsonify(result)

    except Exception as e:
        return jsonify(
            {
                "success": False,
                "error": f"SQL Agent 處理時發生錯誤: {str(e)}",
            }
        )


if __name__ == "__main__":
    # 開發環境
    app.run(debug=True, host='0.0.0.0', port=5000)
else:
    # 生產環境配置
    app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-this-in-production')
