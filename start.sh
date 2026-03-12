#!/bin/bash

echo "🚀 正在启动 Daily Stock Insights..."

# 检查是否有.env文件
if [ ! -f .env ]; then
    echo "⚠️ 未找到.env文件，请先复制.env.example为.env并填写你的TuShare Token"
    exit 1
fi

# 加载环境变量
source .env

# 检查Token是否填写
if [ -z "$TUSHARE_TOKEN" ] || [ "$TUSHARE_TOKEN" = "your_tushare_token_here" ]; then
    echo "⚠️ 请在.env文件中填写你的TuShare Token"
    exit 1
fi

# 启动Web服务
echo "🌐 Web服务即将启动，请访问 http://localhost:5000"
python3 web/app.py
