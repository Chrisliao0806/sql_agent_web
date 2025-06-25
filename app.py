from flask import Flask, request, render_template, jsonify, redirect, url_for, flash
import sqlite3
import os
import pandas as pd
from werkzeug.utils import secure_filename
from services.sql_agent import SQLAgent

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "your-secret-key-here")
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size

# 確保上傳資料夾存在
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# 允許的文件類型
ALLOWED_EXTENSIONS = {"db", "sqlite", "sqlite3", "csv"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def convert_csv_to_sqlite(csv_path, db_path):
    """將CSV文件轉換為SQLite資料庫"""
    try:
        # 嘗試不同的編碼讀取CSV文件
        encodings = ["utf-8", "big5", "gbk", "latin1", "cp1252"]
        df = None
        
        # 先嘗試讀取少量行來檢查文件結構
        for encoding in encodings:
            try:
                # 先讀取前5行來檢查列數和結構
                sample_df = pd.read_csv(csv_path, encoding=encoding, nrows=5)
                if not sample_df.empty:
                    print(f"成功使用 {encoding} 編碼讀取CSV文件，檢測到 {len(sample_df.columns)} 個欄位")
                    
                    # 檢查列數是否過多（SQLite理論上支持最多32767列，但實際建議不超過2000列）
                    if len(sample_df.columns) > 1000:
                        print(f"警告: CSV文件有 {len(sample_df.columns)} 個欄位，可能會影響性能")
                    
                    # 讀取完整文件，使用分塊讀取避免記憶體問題
                    chunk_size = 10000  # 每次讀取10000行
                    chunks = []
                    
                    for chunk in pd.read_csv(csv_path, encoding=encoding, chunksize=chunk_size):
                        if not chunk.empty:
                            chunks.append(chunk)
                    
                    if chunks:
                        df = pd.concat(chunks, ignore_index=True)
                        print(f"成功讀取 {len(df)} 行數據")
                        break
                    
            except Exception as e:
                print(f"使用 {encoding} 編碼失敗: {e}")
                continue

        if df is None or df.empty:
            return False, "無法讀取CSV文件，請檢查文件格式和編碼"

        # 清理列名（移除特殊字符，確保符合SQL標準）
        original_columns = df.columns.tolist()
        cleaned_columns = []
        
        for i, col in enumerate(original_columns):
            # 清理列名
            cleaned_col = str(col).strip()
            # 移除或替換特殊字符
            cleaned_col = cleaned_col.replace(" ", "_").replace("-", "_").replace("(", "_").replace(")", "_")
            cleaned_col = cleaned_col.replace("[", "_").replace("]", "_").replace(".", "_")
            cleaned_col = cleaned_col.replace("/", "_").replace("\\", "_").replace("'", "").replace('"', "")
            cleaned_col = cleaned_col.replace("&", "and").replace("%", "percent").replace("#", "num")
            
            # 確保列名不是SQL關鍵字且以字母開頭
            if not cleaned_col or cleaned_col[0].isdigit():
                cleaned_col = f"col_{i}_{cleaned_col}"
            
            # 確保列名唯一
            base_col = cleaned_col
            counter = 1
            while cleaned_col in cleaned_columns:
                cleaned_col = f"{base_col}_{counter}"
                counter += 1
            
            cleaned_columns.append(cleaned_col)
        
        df.columns = cleaned_columns
        print(f"已清理 {len(cleaned_columns)} 個欄位名稱")

        # 創建SQLite連接
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 取得CSV檔案名稱作為表格名稱
        table_name = os.path.splitext(os.path.basename(csv_path))[0]
        # 清理表格名稱，確保符合SQL標準
        table_name = table_name.replace(" ", "_").replace("-", "_").replace("(", "_").replace(")", "_")
        
        try:
            # 將DataFrame寫入SQLite，使用檔案名稱作為表格名稱
            # 使用method='multi'提高插入性能，對大數據更友好
            df.to_sql(table_name, conn, if_exists="replace", index=False, method='multi')
            
            # 驗證數據是否成功插入
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            conn.close()
            print(f"CSV文件已成功轉換為SQLite，表格名稱: {table_name}，共 {row_count} 行數據")
            return True, table_name
            
        except Exception as sql_error:
            conn.close()
            print(f"SQLite寫入錯誤: {sql_error}")
            return False, f"數據庫寫入失敗: {str(sql_error)}"

    except Exception as e:
        print(f"CSV轉換錯誤: {e}")
        # 提供更詳細的錯誤信息
        error_msg = str(e)
        if "too many columns" in error_msg.lower():
            return False, f"CSV文件欄位數量過多，請考慮減少欄位數量或分割文件。錯誤詳情: {error_msg}"
        elif "memory" in error_msg.lower():
            return False, f"文件過大導致記憶體不足，請考慮使用較小的文件。錯誤詳情: {error_msg}"
        elif "encoding" in error_msg.lower():
            return False, f"文件編碼問題，請檢查文件編碼格式。錯誤詳情: {error_msg}"
        else:
            return False, f"CSV轉換失敗: {error_msg}"


def is_csv_file(filename):
    """檢查是否為CSV文件"""
    return filename.lower().endswith(".csv")


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

        # 檢查是否為CSV文件，如果是則轉換為SQLite
        if is_csv_file(filename):
            # 生成對應的SQLite文件名
            db_filename = os.path.splitext(filename)[0] + ".db"
            db_filepath = os.path.join(app.config["UPLOAD_FOLDER"], db_filename)

            # 轉換CSV為SQLite
            success, result = convert_csv_to_sqlite(filepath, db_filepath)

            if success:
                # 獲取資料庫資訊
                table_info = get_table_info(db_filepath)
                flash(f"CSV文件已成功轉換為SQLite資料庫，表格名稱: {result}")
                return render_template(
                    "database_info.html", filename=db_filename, table_info=table_info
                )
            else:
                flash(f"CSV轉換失敗: {result}")
                return redirect(request.url)
        else:
            # 原有的SQLite文件處理邏輯
            table_info = get_table_info(filepath)
            return render_template(
                "database_info.html", filename=filename, table_info=table_info
            )
    else:
        flash("請上傳有效的資料庫文件 (.db, .sqlite, .sqlite3) 或 CSV 文件 (.csv)")
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
            "sql_result": agent_result.get("result", ""),
        }

        # 如果有SQL查詢結果，添加表格資料
        if sql_query_result and sql_query_result.get("success"):
            result.update(
                {
                    "data": sql_query_result.get("data", []),
                    "columns": sql_query_result.get("columns", []),
                    "row_count": sql_query_result.get("row_count", 0),
                }
            )
        else:
            result.update({"data": [], "columns": [], "row_count": 0})

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
    app.run(debug=True, host="0.0.0.0", port=5000)
else:
    # 生產環境配置
    app.secret_key = os.environ.get(
        "SECRET_KEY", "your-secret-key-here-change-this-in-production"
    )
