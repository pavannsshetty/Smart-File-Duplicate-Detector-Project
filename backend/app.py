"""
app.py - Main Flask Application for Smart File Duplicate Detector

This is the entry point for the web application. It defines all
Flask routes and delegates database operations to the database/db.py
module. No SQL queries are written in this file.

Routes:
    /                   - Dashboard (home page)
    /scan               - Handle scan form submission (POST)
    /history            - View scan history with search
    /about              - About page
    /delete_duplicate   - Delete duplicate files (POST)
    /get_stats          - Get dashboard statistics (JSON)
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

from config import Config
from scanner.scanner import scan_folder
from database import db as database

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

app = Flask(__name__,
    template_folder=os.path.join(PROJECT_ROOT, 'frontend', 'templates'),
    static_folder=os.path.join(PROJECT_ROOT, 'frontend', 'static'),
    static_url_path='/static'
)
app.config.from_object(Config)


def format_size(size_in_bytes):
    if size_in_bytes == 0:
        return "0 B"

    size_units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    size = float(size_in_bytes)

    while size >= 1024 and unit_index < len(size_units) - 1:
        size /= 1024
        unit_index += 1

    return f"{size:.2f} {size_units[unit_index]}"


@app.template_filter("basename")
def basename_filter(file_path):
    return os.path.basename(file_path)


@app.template_filter("dirname")
def dirname_filter(file_path):
    return os.path.dirname(file_path)


def check_database():
    return database.test_connection()


@app.route("/")
def index():
    stats = database.get_dashboard_stats()
    db_error = stats.get("error")

    recent = database.get_recent_scan()
    if recent:
        stats["recent_scan"] = {
            "folder_path": recent["folder_path"],
            "total_files": recent["total_files"],
            "duplicate_files": recent["duplicate_files"],
            "space_saved": format_size(recent["space_saved"]),
            "scan_date": recent["scan_date"].strftime("%Y-%m-%d %H:%M:%S")
            if hasattr(recent["scan_date"], "strftime")
            else str(recent["scan_date"]),
        }
    else:
        stats["recent_scan"] = None

    stats["total_space_saved"] = format_size(stats["space_saved"])

    return render_template(
        "index.html",
        stats=stats,
        format_size=format_size,
        db_error=db_error,
    )


@app.route("/scan", methods=["POST"])
def scan():
    folder_path = request.form.get("folder_path", "").strip()

    if not folder_path:
        flash("Please enter a folder path.", "danger")
        return redirect(url_for("index"))

    result = scan_folder(folder_path)

    if result.get("error"):
        flash(result["error"], "danger")
        return redirect(url_for("index"))

    db_result = database.save_scan_history(
        folder_path=result["folder_path"],
        total_files=result["total_files"],
        duplicate_files=result["duplicate_files"],
        space_saved=result["space_saved"],
    )

    if not db_result["success"]:
        flash("Scan completed, but could not save to history: " + db_result["message"], "warning")

    for file_info in result["all_files"]:
        file_info["size_display"] = format_size(file_info["size"])

    for group in result.get("duplicate_groups", []):
        group["size_display"] = format_size(group["size"])
        group["space_saved_display"] = format_size(
            group["size"] * (len(group["files"]) - 1)
        )

    result["space_saved_display"] = format_size(result["space_saved"])

    return render_template("index.html", scan_result=result, stats=None, format_size=format_size)


@app.route("/history")
def history():
    search_query = request.args.get("search", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = 20

    total_records = database.get_history_count(search_query)
    total_pages = max(1, (total_records + per_page - 1) // per_page)

    records_raw = database.get_history_page(search_query, page, per_page)

    formatted_records = []
    for record in records_raw:
        formatted_records.append({
            "id": record["id"],
            "folder_path": record["folder_path"],
            "total_files": record["total_files"],
            "duplicate_files": record["duplicate_files"],
            "space_saved": format_size(record["space_saved"]),
            "scan_date": record["scan_date"].strftime("%Y-%m-%d %H:%M:%S")
            if hasattr(record["scan_date"], "strftime")
            else str(record["scan_date"]),
        })

    return render_template(
        "history.html",
        records=formatted_records,
        search_query=search_query,
        current_page=page,
        total_pages=total_pages,
    )


@app.route("/about")
def about():
    return render_template("index.html", active_page="about", stats=None)


@app.route("/delete_duplicate", methods=["POST"])
def delete_duplicate():
    data = request.get_json()

    if not data or "file_path" not in data:
        return jsonify({"success": False, "message": "No file path provided."}), 400

    file_path = data["file_path"]

    try:
        if not os.path.exists(file_path):
            return jsonify({"success": False, "message": "File not found."}), 404

        if not os.path.isfile(file_path):
            return jsonify({"success": False, "message": "Path is not a file."}), 400

        os.remove(file_path)

        return jsonify({
            "success": True,
            "message": f"Successfully deleted: {os.path.basename(file_path)}",
        })

    except PermissionError:
        return jsonify({
            "success": False,
            "message": "Permission denied. Cannot delete the file.",
        }), 403
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error deleting file: {str(e)}",
        }), 500


@app.route("/get_stats")
def get_stats():
    stats = database.get_dashboard_stats()

    if stats.get("error"):
        return jsonify({"success": False, "message": stats["error"]}), 500

    return jsonify({
        "success": True,
        "data": {
            "total_scans": stats["total_scans"],
            "total_files": stats["total_files"],
            "duplicate_files": stats["duplicate_files"],
            "space_saved": stats["space_saved"],
            "space_saved_display": format_size(stats["space_saved"]),
        },
    })


@app.errorhandler(404)
def page_not_found(error):
    return render_template("index.html", error="Page not found.", stats=None), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template(
        "index.html", error="Internal server error. Please try again.", stats=None
    ), 500


if __name__ == "__main__":
    db_ok, db_message = check_database()
    if not db_ok:
        print(f"[WARNING] {db_message}")
        print("[INFO] The application will start, but database features may not work.")
    else:
        print("[INFO] Database connection verified successfully.")

    app.run(debug=True, host="0.0.0.0", port=5000)
