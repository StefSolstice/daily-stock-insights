"""
自选股管理路由
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
import sqlite3
from datetime import datetime

stocks_bp = Blueprint("stocks", __name__)

import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "stocks.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@stocks_bp.route("/watchlist")
@login_required
def watchlist():
    """自选股列表"""
    category_id = request.args.get("category_id", type=int)
    conn = get_db()

    if category_id:
        stocks = conn.execute(
            """
            SELECT w.*, c.name as category_name 
            FROM watchlist w 
            LEFT JOIN categories c ON w.category_id = c.id 
            WHERE w.user_id = ? AND w.category_id = ?
            ORDER BY w.created_at DESC
        """,
            (current_user.id, category_id),
        ).fetchall()
    else:
        stocks = conn.execute(
            """
            SELECT w.*, c.name as category_name 
            FROM watchlist w 
            LEFT JOIN categories c ON w.category_id = c.id 
            WHERE w.user_id = ?
            ORDER BY w.created_at DESC
        """,
            (current_user.id,),
        ).fetchall()

    categories = conn.execute(
        "SELECT * FROM categories WHERE user_id = ?", (current_user.id,)
    ).fetchall()
    conn.close()

    return render_template(
        "watchlist.html",
        stocks=stocks,
        categories=categories,
        current_category_id=category_id,
    )


@stocks_bp.route("/api/stock/add", methods=["POST"])
@login_required
def add_stock():
    """添加自选股"""
    data = request.get_json()
    ts_code = data.get("ts_code")
    stock_name = data.get("name", "")
    category_id = data.get("category_id")
    if category_id is not None:
        category_id = int(category_id)

    if not ts_code:
        return jsonify({"error": "股票代码不能为空"}), 400

    conn = get_db()
    try:
        conn.execute(
            """
            INSERT INTO watchlist (user_id, ts_code, stock_name, category_id)
            VALUES (?, ?, ?, ?)
        """,
            (current_user.id, ts_code, stock_name, category_id),
        )
        conn.commit()
        return jsonify({"success": True})
    except sqlite3.IntegrityError:
        return jsonify({"error": "该股票已在自选列表中"}), 400
    finally:
        conn.close()


@stocks_bp.route("/api/stock/delete/<int:stock_id>", methods=["POST"])
@login_required
def delete_stock(stock_id):
    """删除自选股"""
    conn = get_db()
    conn.execute(
        "DELETE FROM watchlist WHERE id = ? AND user_id = ?",
        (stock_id, current_user.id),
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True})


@stocks_bp.route("/api/category/add", methods=["POST"])
@login_required
def add_category():
    """添加分类"""
    data = request.get_json()
    name = data.get("name")

    if not name:
        return jsonify({"error": "分类名称不能为空"}), 400

    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO categories (user_id, name) VALUES (?, ?)",
            (current_user.id, name),
        )
        conn.commit()
        return jsonify({"success": True})
    except sqlite3.IntegrityError:
        return jsonify({"error": "分类名称已存在"}), 400
    finally:
        conn.close()


@stocks_bp.route("/api/category/delete/<int:category_id>", methods=["POST"])
@login_required
def delete_category(category_id):
    """删除分类"""
    conn = get_db()
    conn.execute(
        "DELETE FROM categories WHERE id = ? AND user_id = ?",
        (category_id, current_user.id),
    )
    # 同时清空该分类下的股票分类
    conn.execute(
        "UPDATE watchlist SET category_id = NULL WHERE category_id = ? AND user_id = ?",
        (category_id, current_user.id),
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True})


@stocks_bp.route("/api/category/update/<int:category_id>", methods=["POST"])
@login_required
def update_category(category_id):
    data = request.get_json()
    name = data.get("name")
    if not name:
        return jsonify({"error": "分类名称不能为空"}), 400

    conn = get_db()
    try:
        conn.execute(
            "UPDATE categories SET name = ? WHERE id = ? AND user_id = ?",
            (name, category_id, current_user.id),
        )
        conn.commit()
        return jsonify({"success": True})
    except sqlite3.IntegrityError:
        return jsonify({"error": "分类名称已存在"}), 400
    finally:
        conn.close()


@stocks_bp.route("/api/stock/update/<int:stock_id>", methods=["POST"])
@login_required
def update_stock(stock_id):
    data = request.get_json()
    category_id = data.get("category_id")
    stock_name = data.get("stock_name")

    conn = get_db()
    if category_id is not None:
        category_id = int(category_id)
        conn.execute(
            "UPDATE watchlist SET category_id = ?, stock_name = ? WHERE id = ? AND user_id = ?",
            (category_id, stock_name, stock_id, current_user.id),
        )
    else:
        conn.execute(
            "UPDATE watchlist SET category_id = NULL, stock_name = ? WHERE id = ? AND user_id = ?",
            (stock_name, stock_id, current_user.id),
        )
    conn.commit()
    conn.close()
    return jsonify({"success": True})


@stocks_bp.route("/api/stock/search")
@login_required
def search_stock():
    """搜索股票（调用 TuShare API）"""
    import tushare as ts
    import os

    keyword = request.args.get("q", "")
    if not keyword:
        return jsonify([])

    token = os.getenv("TUSHARE_TOKEN")
    if not token:
        return jsonify([])

    try:
        ts.set_token(token)
        pro = ts.pro_api()
        # 搜索股票（支持名称和代码搜索）
        result = pro.stock_basic(
            exchange="", list_status="L", fields="ts_code,symbol,name,area,industry"
        )
        name_match = result["name"].str.contains(keyword, case=False, na=False)
        symbol_match = result["symbol"].str.contains(keyword, case=False, na=False)
        ts_code_match = result["ts_code"].str.contains(keyword, case=False, na=False)
        stocks = result[name_match | symbol_match | ts_code_match]

        result_list = []
        for _, row in stocks.head(20).iterrows():
            result_list.append(
                {
                    "ts_code": row["ts_code"],
                    "symbol": row["symbol"],
                    "name": row["name"],
                    "area": row.get("area", ""),
                    "industry": row.get("industry", ""),
                }
            )

        return jsonify(result_list)
    except Exception as e:
        return jsonify([])
