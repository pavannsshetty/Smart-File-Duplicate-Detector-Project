import mysql.connector
from mysql.connector import errorcode

from config import Config


def get_connection():
    conn = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
    )
    return conn


def test_connection():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT COUNT(*) AS cnt FROM information_schema.tables "
            "WHERE table_schema = %s AND table_name = 'scan_history'",
            (Config.MYSQL_DB,),
        )
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result and result["cnt"] > 0:
            return (True, "Database connection OK.")
        else:
            return (
                False,
                "Table 'scan_history' not found in database "
                f"'{Config.MYSQL_DB}'. Please create it manually.",
            )

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            return (False, "Access denied. Check your MySQL username and password.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            return (
                False,
                f"Database '{Config.MYSQL_DB}' does not exist. "
                "Please create it in MySQL Workbench.",
            )
        elif err.errno == errorcode.ER_DBACCESS_DENIED_ERROR:
            return (
                False,
                f"User '{Config.MYSQL_USER}' does not have access "
                f"to database '{Config.MYSQL_DB}'.",
            )
        else:
            return (False, f"Database error: {err}")

    except Exception as e:
        return (False, f"Connection failed: {e}")


def get_dashboard_stats():
    stats = {
        "total_scans": 0,
        "total_files": 0,
        "duplicate_files": 0,
        "space_saved": 0,
        "error": None,
    }

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) AS count FROM scan_history")
        result = cursor.fetchone()
        stats["total_scans"] = result["count"] if result else 0

        cursor.execute(
            "SELECT COALESCE(SUM(total_files), 0) AS total FROM scan_history"
        )
        result = cursor.fetchone()
        stats["total_files"] = result["total"] if result else 0

        cursor.execute(
            "SELECT COALESCE(SUM(duplicate_files), 0) AS total FROM scan_history"
        )
        result = cursor.fetchone()
        stats["duplicate_files"] = result["total"] if result else 0

        cursor.execute(
            "SELECT COALESCE(SUM(space_saved), 0) AS total FROM scan_history"
        )
        result = cursor.fetchone()
        stats["space_saved"] = result["total"] if result else 0

        cursor.close()
        conn.close()

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_NO_SUCH_TABLE:
            stats["error"] = (
                "Table 'scan_history' is missing. "
                "Please create it manually using the schema reference file."
            )
        else:
            stats["error"] = f"Database error: {err}"

    except Exception as e:
        stats["error"] = f"Unexpected error: {e}"

    return stats


def get_recent_scan():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM scan_history ORDER BY scan_date DESC LIMIT 1"
        )
        recent = cursor.fetchone()
        cursor.close()
        conn.close()
        return recent

    except Exception:
        return None


def save_scan_history(folder_path, total_files, duplicate_files, space_saved):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO scan_history
                (folder_path, total_files, duplicate_files, space_saved)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (folder_path, total_files, duplicate_files, space_saved))
        conn.commit()

        cursor.close()
        conn.close()
        return {"success": True, "message": "Scan history saved."}

    except mysql.connector.Error as err:
        error_msg = f"Database error while saving scan history: {err}"
        print(error_msg)
        return {"success": False, "message": error_msg}

    except Exception as e:
        error_msg = f"Unexpected error while saving scan history: {e}"
        print(error_msg)
        return {"success": False, "message": error_msg}


def get_history_count(search_query=""):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        if search_query:
            cursor.execute(
                "SELECT COUNT(*) AS count FROM scan_history WHERE folder_path LIKE %s",
                (f"%{search_query}%",),
            )
        else:
            cursor.execute("SELECT COUNT(*) AS count FROM scan_history")

        result = cursor.fetchone()
        count = result["count"] if result else 0

        cursor.close()
        conn.close()
        return count

    except Exception:
        return 0


def get_history_page(search_query="", page=1, per_page=20):
    offset = (page - 1) * per_page

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        if search_query:
            query = """
                SELECT id, folder_path, total_files, duplicate_files,
                       space_saved, scan_date
                FROM scan_history
                WHERE folder_path LIKE %s
                ORDER BY scan_date DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, (f"%{search_query}%", per_page, offset))
        else:
            query = """
                SELECT id, folder_path, total_files, duplicate_files,
                       space_saved, scan_date
                FROM scan_history
                ORDER BY scan_date DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, (per_page, offset))

        records = cursor.fetchall()

        cursor.close()
        conn.close()
        return records

    except Exception:
        return []
