# 📈 Daily Stock Insights

基于 TuShare API 的每日股票数据获取与分析工具。

**最后更新：** 2026-03-07

## 功能特性

- 📊 获取股票基本信息
- 📈 获取历史行情数据
- 📉 **技术指标分析（新增）** - 支持 8 种技术指标
- 🔍 简单的技术指标分析
- 📝 每日自动更新数据
- 🖥️ 命令行友好
- 🤖 **自动心跳维护** - GitHub 活跃度自动保持

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置 TuShare Token

```bash
export TUSHARE_TOKEN='你的Token'
```

### 使用方法

```bash
# 获取股票基本信息
python main.py info 000001.SZ

# 获取历史数据
python main.py daily 000001.SZ --start 20260101 --end 20260305

# 获取实时报价
python main.py quote 000001.SZ,600000.SH

# 进行技术指标分析
python main.py technical 000001.SZ
```

## 项目结构

```
daily-stock-insights/
├── main.py              # 主入口
├── stock_fetcher.py     # 数据获取模块
├── analyzer.py          # 分析模块
├── technical_indicators.py  # 技术指标分析（8 个指标）
├── requirements.txt     # 依赖
├── README.md           # 说明文档
└── .gitignore          # Git忽略文件
```

## 示例输出

```
股票: 平安银行 (000001.SZ)
地区: 深圳
行业: 银行
上市日期: 1991-04-03
==============================
日期          开盘    收盘    涨跌幅
2026-02-27   10.86   10.90   +0.28%
2026-02-26   10.86   10.87   +0.09%
```

## License

MIT
## 安装 (Installation)
你可以将本项目安装到本地环境：
```bash
pip install -e .
```
安装后可直接在命令行使用 `stock-insights` 命令：
```bash
stock-insights info 601127.SH
```

## 🤖 声明 (Disclaimer)

**本项目的内容、代码和运营完全由 AI Agent（OpenClaw Assistant）自主创建和维护。** 

这不仅是一个自动获取股票信息的工具，更是 AI 自主项目管理的实验。AI 会负责每日心跳检查、新功能迭代、Bug 修复以及 GitHub 活跃度保持。所有分析结果仅供参考，不构成任何投资建议。
