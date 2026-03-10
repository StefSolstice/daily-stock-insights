#!/bin/bash
# 启动 Web UI

echo "🚀 启动 Daily Stock Insights Web UI..."

# 检查依赖
echo "📦 检查依赖..."
pip3 install -q Flask Flask-Login Flask-WTF bcrypt python-dotenv 2>/dev/null

# 初始化数据库并启动
echo "📊 初始化数据库..."
cd "$(dirname "$0")"
python3 app.py
