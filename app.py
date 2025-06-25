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
                    print(
                        f"成功使用 {encoding} 編碼讀取CSV文件，檢測到 {len(sample_df.columns)} 個欄位"
                    )

                    # 檢查列數是否過多，如果超過1500列，則採用分片存儲策略
                    if len(sample_df.columns) > 1500:
                        print(
                            f"警告: CSV文件有 {len(sample_df.columns)} 個欄位，超過SQLite建議限制，將採用分片存儲策略"
                        )
                        return convert_csv_to_sqlite_chunked(
                            csv_path, db_path, encoding
                        )
                    elif len(sample_df.columns) > 1000:
                        print(
                            f"警告: CSV文件有 {len(sample_df.columns)} 個欄位，將進行分批處理"
                        )

                    # 讀取完整文件，使用分塊讀取避免記憶體問題
                    chunk_size = 5000 if len(sample_df.columns) > 1000 else 10000
                    chunks = []

                    for chunk in pd.read_csv(
                        csv_path, encoding=encoding, chunksize=chunk_size
                    ):
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
            cleaned_col = (
                cleaned_col.replace(" ", "_")
                .replace("-", "_")
                .replace("(", "_")
                .replace(")", "_")
            )
            cleaned_col = (
                cleaned_col.replace("[", "_").replace("]", "_").replace(".", "_")
            )
            cleaned_col = (
                cleaned_col.replace("/", "_")
                .replace("\\", "_")
                .replace("'", "")
                .replace('"', "")
            )
            cleaned_col = (
                cleaned_col.replace("&", "and")
                .replace("%", "percent")
                .replace("#", "num")
            )
            cleaned_col = (
                cleaned_col.replace("@", "at").replace("!", "").replace("?", "")
            )

            # 確保列名不是SQL關鍵字且以字母開頭
            if not cleaned_col or cleaned_col[0].isdigit():
                cleaned_col = f"col_{i}_{cleaned_col}"

            # 限制列名長度
            if len(cleaned_col) > 64:
                cleaned_col = cleaned_col[:60] + f"_{i}"

            # 確保列名唯一
            base_col = cleaned_col
            counter = 1
            while cleaned_col in cleaned_columns:
                cleaned_col = f"{base_col}_{counter}"
                counter += 1
                # 如果計數器讓列名過長，截短基礎名稱
                if len(cleaned_col) > 64:
                    base_col = base_col[:50]
                    cleaned_col = f"{base_col}_{counter}"

            cleaned_columns.append(cleaned_col)

        df.columns = cleaned_columns
        print(f"已清理 {len(cleaned_columns)} 個欄位名稱")

        # 創建SQLite連接，並設置優化參數
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 設置SQLite優化參數以處理大量列數
        cursor.execute("PRAGMA journal_mode = MEMORY")
        cursor.execute("PRAGMA synchronous = OFF")
        cursor.execute("PRAGMA cache_size = 1000000")
        cursor.execute("PRAGMA locking_mode = EXCLUSIVE")
        cursor.execute("PRAGMA temp_store = MEMORY")

        # 取得CSV檔案名稱作為表格名稱
        table_name = os.path.splitext(os.path.basename(csv_path))[0]
        # 清理表格名稱，確保符合SQL標準
        table_name = (
            table_name.replace(" ", "_")
            .replace("-", "_")
            .replace("(", "_")
            .replace(")", "_")
        )
        table_name = table_name.replace("[", "_").replace("]", "_").replace(".", "_")

        try:
            # 對於正常列數，使用pandas的to_sql方法
            df.to_sql(
                table_name,
                conn,
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=1000,
            )

            # 驗證數據是否成功插入
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]

            # 驗證列數
            cursor.execute(f"PRAGMA table_info({table_name})")
            actual_columns = cursor.fetchall()

            conn.close()
            print(
                f"CSV文件已成功轉換為SQLite，表格名稱: {table_name}，共 {row_count} 行數據，{len(actual_columns)} 列"
            )
            return True, table_name

        except Exception as sql_error:
            conn.close()
            print(f"SQLite寫入錯誤: {sql_error}")
            error_msg = str(sql_error)

            if "too many columns" in error_msg.lower():
                print("嘗試使用分片存儲策略...")
                return convert_csv_to_sqlite_chunked(csv_path, db_path, encoding)
            elif "database is locked" in error_msg.lower():
                return False, f"數據庫被鎖定，請稍後重試。錯誤詳情: {error_msg}"
            else:
                return False, f"數據庫寫入失敗: {error_msg}"

    except Exception as e:
        print(f"CSV轉換錯誤: {e}")
        # 提供更詳細的錯誤信息
        error_msg = str(e)
        if "too many columns" in error_msg.lower():
            return (
                False,
                f"CSV文件欄位數量過多。SQLite 在處理大量欄位時有限制，建議：1) 減少欄位數量 2) 將數據分割為多個文件。錯誤詳情: {error_msg}",
            )
        elif "memory" in error_msg.lower():
            return (
                False,
                f"文件過大導致記憶體不足，請考慮使用較小的文件。錯誤詳情: {error_msg}",
            )
        elif "encoding" in error_msg.lower():
            return False, f"文件編碼問題，請檢查文件編碼格式。錯誤詳情: {error_msg}"
        else:
            return False, f"CSV轉換失敗: {error_msg}"


def convert_csv_to_sqlite_chunked(csv_path, db_path, encoding):
    """
    使用分片策略處理超大列數的CSV文件
    將大量列分割成多個較小的表格
    """
    try:
        print("開始使用分片存儲策略處理超大列數CSV文件...")

        # 讀取CSV文件頭部信息
        df_sample = pd.read_csv(csv_path, encoding=encoding, nrows=1)
        total_columns = len(df_sample.columns)

        # 設定每個分片的最大列數（保守設定為1000列）
        max_columns_per_chunk = 1000
        num_chunks = (
            total_columns + max_columns_per_chunk - 1
        ) // max_columns_per_chunk

        print(
            f"將 {total_columns} 列分成 {num_chunks} 個分片，每片最多 {max_columns_per_chunk} 列"
        )

        # 創建SQLite連接
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 設置SQLite優化參數
        cursor.execute("PRAGMA journal_mode = MEMORY")
        cursor.execute("PRAGMA synchronous = OFF")
        cursor.execute("PRAGMA cache_size = 1000000")
        cursor.execute("PRAGMA locking_mode = EXCLUSIVE")
        cursor.execute("PRAGMA temp_store = MEMORY")

        # 基礎表格名稱
        base_table_name = os.path.splitext(os.path.basename(csv_path))[0]
        base_table_name = (
            base_table_name.replace(" ", "_")
            .replace("-", "_")
            .replace("(", "_")
            .replace(")", "_")
        )
        base_table_name = (
            base_table_name.replace("[", "_").replace("]", "_").replace(".", "_")
        )

        successful_tables = []

        # 分片處理
        for chunk_idx in range(num_chunks):
            start_col = chunk_idx * max_columns_per_chunk
            end_col = min((chunk_idx + 1) * max_columns_per_chunk, total_columns)

            print(
                f"處理分片 {chunk_idx + 1}/{num_chunks}: 列 {start_col} 到 {end_col - 1}"
            )

            try:
                # 確定要讀取的列
                if chunk_idx == 0:
                    # 第一個分片包含日期列
                    cols_to_read = list(range(start_col, end_col))
                else:
                    # 其他分片包含第一列（日期）和當前分片的列
                    cols_to_read = [0] + list(range(start_col, end_col))

                # 分塊讀取數據
                chunk_dfs = []
                for chunk in pd.read_csv(
                    csv_path, encoding=encoding, chunksize=5000, usecols=cols_to_read
                ):
                    if not chunk.empty:
                        chunk_dfs.append(chunk)

                if not chunk_dfs:
                    continue

                df_chunk = pd.concat(chunk_dfs, ignore_index=True)

                # 清理列名
                cleaned_columns = []
                for i, col in enumerate(df_chunk.columns):
                    cleaned_col = str(col).strip()
                    cleaned_col = (
                        cleaned_col.replace(" ", "_")
                        .replace("-", "_")
                        .replace("(", "_")
                        .replace(")", "_")
                    )
                    cleaned_col = (
                        cleaned_col.replace("[", "_")
                        .replace("]", "_")
                        .replace(".", "_")
                    )
                    cleaned_col = (
                        cleaned_col.replace("/", "_")
                        .replace("\\", "_")
                        .replace("'", "")
                        .replace('"', "")
                    )
                    cleaned_col = (
                        cleaned_col.replace("&", "and")
                        .replace("%", "percent")
                        .replace("#", "num")
                    )
                    cleaned_col = (
                        cleaned_col.replace("@", "at").replace("!", "").replace("?", "")
                    )

                    if not cleaned_col or cleaned_col[0].isdigit():
                        cleaned_col = f"col_{i}_{cleaned_col}"

                    if len(cleaned_col) > 64:
                        cleaned_col = cleaned_col[:60] + f"_{i}"

                    # 確保列名唯一
                    base_col = cleaned_col
                    counter = 1
                    while cleaned_col in cleaned_columns:
                        cleaned_col = f"{base_col}_{counter}"
                        counter += 1
                        if len(cleaned_col) > 64:
                            base_col = base_col[:50]
                            cleaned_col = f"{base_col}_{counter}"

                    cleaned_columns.append(cleaned_col)

                df_chunk.columns = cleaned_columns

                # 生成表格名稱
                if chunk_idx == 0:
                    table_name = base_table_name
                else:
                    table_name = f"{base_table_name}_part_{chunk_idx + 1}"

                # 寫入SQLite
                df_chunk.to_sql(
                    table_name,
                    conn,
                    if_exists="replace",
                    index=False,
                    method="multi",
                    chunksize=500,
                )

                # 驗證數據
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]

                cursor.execute(f"PRAGMA table_info({table_name})")
                actual_columns = cursor.fetchall()

                successful_tables.append(table_name)
                print(
                    f"成功創建表格 {table_name}: {row_count} 行, {len(actual_columns)} 列"
                )

            except Exception as chunk_error:
                print(f"分片 {chunk_idx + 1} 處理失敗: {chunk_error}")
                continue

        conn.close()

        if successful_tables:
            # 創建一個主表的視圖或者返回第一個表作為主表
            main_table = successful_tables[0]
            result_message = f"CSV文件已成功轉換為SQLite，創建了 {len(successful_tables)} 個表格。主表格: {main_table}"
            if len(successful_tables) > 1:
                result_message += f"，其他表格: {', '.join(successful_tables[1:])}"

            print(result_message)
            return True, main_table
        else:
            return False, "所有分片處理都失敗了"

    except Exception as e:
        print(f"分片處理錯誤: {e}")
        return False, f"分片處理失敗: {str(e)}"


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
