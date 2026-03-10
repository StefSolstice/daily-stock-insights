# Web UI 使用指南

## 🚀 快速启动

### 方式 1：一键启动（推荐）
```bash
cd web
./start.sh
```

### 方式 2：手动启动
```bash
cd web
pip3 install -r ../requirements.txt
python3 app.py
```

启动后访问：http://localhost:5000

---

## 📋 功能特性

### ✅ 已实现
- [x] 用户注册/登录
- [x] 自选股管理（支持分类）
- [x] 股票搜索（TuShare API）
- [x] 股票技术分析
- [x] 批量分析（开发中）
- [x] 数据导出（开发中）

### 📅 计划中
- [ ] 定时任务（每日自动更新）
- [ ] 价格提醒推送
- [ ] 股票对比功能
- [ ] 数据看板
- [ ] 选股策略

---

## 🗄️ 数据库

使用 SQLite 存储：
- `stocks.db` - 用户数据、自选股、分类

数据库自动初始化，无需手动创建。

---

## 🔐 安全说明

- 密码使用 bcrypt 加密存储
- 启用 CSRF 保护
- 会话管理使用 Flask-Login
- TuShare token 存储在 `.env` 文件，不提交到 Git

---

## 📁 目录结构

```
web/
├── app.py              # Flask 应用入口
├── stocks.db           # SQLite 数据库（自动生成）
├── start.sh            # 启动脚本
├── routes/
│   ├── stocks.py       # 自选股路由
│   └── api.py          # API 接口
├── templates/
│   ├── base.html       # 基础模板
│   ├── login.html      # 登录页面
│   ├── register.html   # 注册页面
│   ├── dashboard.html  # 仪表盘
│   ├── watchlist.html  # 自选股列表
│   ├── analysis.html   # 股票分析
│   └── settings.html   # 设置页面
└── static/
    ├── css/            # 样式文件
    └── js/             # JavaScript 文件
```

---

## 🛠️ 开发说明

### 添加新功能
1. 在 `routes/` 创建新路由文件
2. 在 `app.py` 注册蓝图
3. 在 `templates/` 创建对应模板

### API 规范
- 所有 API 需要登录（`@login_required`）
- 返回 JSON 格式
- 错误使用 `{'error': '描述'}` 格式

---

## 🐛 常见问题

### 无法启动
检查依赖是否安装：
```bash
pip3 install Flask Flask-Login Flask-WTF bcrypt python-dotenv
```

### 数据库错误
删除 `stocks.db` 重新启动，会自动重建。

### TuShare API 失败
检查 `.env` 文件中的 token 是否正确。

---

*最后更新：2026-03-10*
