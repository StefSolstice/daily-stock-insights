"""
Daily Stock Insights - Web UI
股票分析 Web 界面
"""

import os
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import bcrypt

# 加载环境变量
load_dotenv()

# 创建 Flask 应用
app = Flask(__name__)
app.secret_key = os.urandom(24).hex()  # 生产环境应使用固定密钥

# 初始化扩展
# csrf = CSRFProtect(app)  # 暂时禁用 CSRF，修复登录问题
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "请先登录"


@login_manager.unauthorized_handler
def unauthorized():
    from flask import request, jsonify

    if request.path.startswith("/api/"):
        return jsonify({"error": "请先登录"}), 401
    from flask import redirect, url_for

    return redirect(url_for("login"))


# 数据库配置
DB_PATH = os.path.join(os.path.dirname(__file__), "stocks.db")

# ==================== 数据库模型 ====================

import sqlite3
from datetime import datetime


def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库表"""
    conn = get_db()
    cursor = conn.cursor()

    # 用户表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 股票分类表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            sort_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE (user_id, name)
        )
    """)

    # 自选股表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            ts_code TEXT NOT NULL,
            stock_name TEXT,
            category_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (category_id) REFERENCES categories (id),
            UNIQUE (user_id, ts_code)
        )
    """)

    # 分析结果缓存表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts_code TEXT NOT NULL,
            stock_name TEXT,
            analysis_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (ts_code)
        )
    """)

    # 用户设置表（存储最后分析的股票等）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            last_analysis_ts_code TEXT,
            last_analysis_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    conn.commit()
    conn.close()


# ==================== Flask-Login ====================


@login_manager.user_loader
def load_user(user_id):
    """加载用户"""
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if user:
        return User(user["id"], user["username"], user["password_hash"])
    return None


class User:
    """用户类"""

    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


# ==================== 路由 ====================

# 导入其他路由蓝图
from routes.stocks import stocks_bp
from routes.api import api_bp
from routes.selection import selection_bp

app.register_blueprint(stocks_bp)
app.register_blueprint(api_bp)
app.register_blueprint(selection_bp)


@app.route("/")
def index():
    """首页"""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """登录"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        conn.close()

        if user and bcrypt.checkpw(
            password.encode("utf-8"), user["password_hash"].encode("utf-8")
        ):
            login_user(User(user["id"], user["username"], user["password_hash"]))
            flash("登录成功！", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard"))
        else:
            flash("用户名或密码错误", "danger")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """注册"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:
            flash("两次密码不一致", "danger")
            return render_template("register.html")

        # 检查用户名是否已存在
        conn = get_db()
        exists = conn.execute(
            "SELECT id FROM users WHERE username = ?", (username,)
        ).fetchone()
        if exists:
            flash("用户名已存在", "danger")
            conn.close()
            return render_template("register.html")

        # 创建用户
        password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )
        conn.commit()
        conn.close()

        flash("注册成功！请登录", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    """登出"""
    logout_user()
    flash("已退出登录", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    """仪表盘"""
    conn = get_db()

    # 获取分类和自选股数量
    categories = conn.execute(
        """
        SELECT c.id, c.name, COUNT(w.id) as stock_count 
        FROM categories c 
        LEFT JOIN watchlist w ON c.id = w.category_id 
        WHERE c.user_id = ? 
        GROUP BY c.id
    """,
        (current_user.id,),
    ).fetchall()

    total_stocks = conn.execute(
        "SELECT COUNT(*) FROM watchlist WHERE user_id = ?", (current_user.id,)
    ).fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html", categories=categories, total_stocks=total_stocks
    )


@app.route("/analysis")
@login_required
def analysis():
    """股票分析页面"""
    ts_code = request.args.get("ts_code", "")
    return render_template("analysis.html", ts_code=ts_code)


@app.route("/settings")
@login_required
def settings():
    """设置页面"""
    return render_template("settings.html")


# ==================== 初始化 ====================

if __name__ == "__main__":
    init_db()
    print("🚀 启动 Web UI...")
    print("📊 访问地址：http://localhost:5001")
    app.run(debug=True, host="0.0.0.0", port=5001)
