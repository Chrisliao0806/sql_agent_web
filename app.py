from flask import Flask, request, render_template, jsonify, redirect, url_for, flash
import sqlite3
import os
from werkzeug.utils import secure_filename
import pandas as pd
import json

app = Flask(__name__)
app.secret_key = "your-secret-key-here"
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


def sql_agent_query(db_path, natural_language_query):
    """SQL Agent 查詢 (目前模擬，後續可以替換為真實的 AI 實現)"""
    # 這裡先模擬 SQL Agent 的行為，你可以後續替換為真實的 AI 模型

    # 簡單的關鍵字映射 (示例)
    query_mapping = {
        "所有": "SELECT * FROM",
        "全部": "SELECT * FROM",
        "多少": "SELECT COUNT(*) FROM",
        "總數": "SELECT COUNT(*) FROM",
        "平均": "SELECT AVG",
        "最大": "SELECT MAX",
        "最小": "SELECT MIN",
    }

    # 獲取表格資訊
    table_info = get_table_info(db_path)
    table_names = list(table_info.keys())

    # 簡單的自然語言轉SQL (示例實現)
    generated_sql = ""

    if table_names:
        first_table = table_names[0]
        if "所有" in natural_language_query or "全部" in natural_language_query:
            generated_sql = f"SELECT * FROM {first_table} LIMIT 10;"
        elif "多少" in natural_language_query or "總數" in natural_language_query:
            generated_sql = f"SELECT COUNT(*) as total_count FROM {first_table};"
        else:
            generated_sql = f"SELECT * FROM {first_table} LIMIT 5;"

    # 執行生成的SQL
    result = execute_sql_query(db_path, generated_sql)
    result["generated_sql"] = generated_sql
    result["natural_query"] = natural_language_query

    return result


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

    result = sql_agent_query(filepath, natural_query)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
