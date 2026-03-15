# Daily Stock Insights - 每日股票洞察

📊 基于 TuShare API 的股票数据分析工具，提供技术指标、基本面分析、可视化和数据导出功能。

## ✨ 功能特性

### 📈 技术指标分析
- **均线系统**: MA5, MA10, MA20, MA60
- **趋势指标**: MACD, DMI, CCI
- **动量指标**: RSI, KDJ, BOLL
- **成交量分析**: 量价关系、均量线

### 🏢 基本面分析 (NEW!)
- **估值指标**: PE, PB, PS, 股息率
- **盈利能力**: ROE, ROA, 毛利率
- **成长能力**: 营收增速，利润增速
- **估值水平评估**: 低/合理/高估判断

### 📊 数据可视化 (NEW!)
- **K 线图**: 红阳绿阴，带成交量
- **指标图**: 多指标组合展示
- **价格分布**: 直方图分析
- **成交量分析**: 量价关系图

### 💾 数据导出 (NEW!)
- **CSV**: 通用格式，支持 Excel 打开
- **Excel**: 自动调整列宽
- **JSON**: 结构化数据，带元数据

### 🔔 价格提醒
- 支持设置价格阈值
- 实时监控触发条件
- 灵活的提醒策略

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置 TuShare Token

1. **获取 Token**: 访问 https://tushare.pro 注册并获取免费 token
2. **配置 Token**: 在项目根目录创建 `.env` 文件，写入：

```bash
# .env
TUSHARE_TOKEN=your_tushare_token_here
```

### 命令行使用（推荐）

项目支持命令行方式直接分析股票：

```bash
# 分析单个股票（平安银行）
python main.py --code 000001.SZ

# 指定日期范围分析
python main.py --code 000001.SZ --start 20260101 --end 20260315

# 分析并导出到指定目录
python main.py --code 000001.SZ --export ./my_exports

# 启动守护模式（定时任务）
python main.py --daemon
```

### Python 代码使用

```python
from analyzer import StockAnalyzer

# 创建分析器
analyzer = StockAnalyzer('000001.SZ', pro)

# 获取历史数据
df = analyzer.get_history(days=100)

# 计算技术指标
df_with_indicators = analyzer.calculate_all_indicators(df)

# 生成分析报告
report = analyzer.generate_report(df)
print(report)
```

### 基本使用

```python
from analyzer import StockAnalyzer

# 创建分析器
analyzer = StockAnalyzer('000001.SZ', pro)

# 获取历史数据
df = analyzer.get_history(days=100)

# 计算技术指标
df_with_indicators = analyzer.calculate_all_indicators(df)

# 生成分析报告
report = analyzer.generate_report(df)
print(report)
```

### 基本面分析

```python
from fundamental_analyzer import FundamentalAnalyzer

# 创建基本面分析器
fund = FundamentalAnalyzer('000001.SZ', pro)

# 获取估值指标
valuation = fund.get_valuation_metrics()
print(f"PE: {valuation.get('pe_ttm', 'N/A')}, PB: {valuation.get('pb', 'N/A')}")

# 生成基本面报告
report = fund.generate_fundamental_report()
print(report)
```

### 数据可视化

```python
from visualizer import StockVisualizer

# 创建可视化器
viz = StockVisualizer(df, '000001.SZ', '平安银行')

# 绘制 K 线图
viz.plot_kline(save_path='./charts/kline.png', show=False)

# 绘制带指标的 K 线图
viz.plot_with_indicators(
    indicators=['MA5', 'MA10', 'MA20', 'VOL', 'MACD'],
    save_path='./charts/indicators.png',
    show=False
)
```

### 数据导出

```python
from exporter import DataExporter

# 创建导出器
exporter = DataExporter(df, '000001.SZ', '平安银行')

# 导出所有格式
exporter.export_all()

# 单独导出
exporter.to_csv()
exporter.to_excel()
exporter.to_json()
```

### 实际运行示例

```bash
# 分析平安银行（000001.SZ）
python main.py --code 000001.SZ

# 分析贵州茅台（600519.SH）并导出到指定目录
python main.py --code 600519.SH --export ./my_analysis

# 分析指定时间段
python main.py --code 000001.SZ --start 20260101 --end 20260228

# 查看帮助信息
python main.py --help
```

## 📁 项目结构

```
daily-stock-insights/
├── README.md                 # 项目文档
├── requirements.txt          # 依赖列表
├── stock_fetcher.py          # 数据获取模块
├── analyzer.py               # 技术分析模块
├── technical_indicators.py   # 技术指标计算
├── alert_monitor.py          # 价格提醒监控
├── fundamental_analyzer.py   # 基本面分析 (NEW!)
├── visualizer.py             # 数据可视化 (NEW!)
├── exporter.py               # 数据导出 (NEW!)
├── main.py                   # 主程序入口
├── charts/                   # 图表输出目录
└── exports/                  # 数据导出目录
```

## 📋 更新日志

### 2026-03-10
- ✨ 新增基本面分析模块，支持 PE、PB、ROE 等指标
- ✨ 新增数据可视化模块，支持 K 线图、指标图
- ✨ 新增数据导出模块，支持 CSV/Excel/JSON 格式
- 🐛 修复多处 bug，支持程序完整运行
- ✨ 新增 `.env` 文件配置 TuShare token（推荐方式）
- 📝 更新 README 文档，添加配置说明和使用示例

### 2026-03-09
- ✨ 新增价格提醒监控功能
- ✨ 新增 8 个技术指标计算
- 📝 完善项目文档和示例

## 🔧 配置说明

### TuShare Token 和股票池配置（推荐方式）

**方式 1：`.env` 文件（推荐）**

在项目根目录创建 `.env` 文件，写入你的 token 和股票池配置：

```bash
# .env
TUSHARE_TOKEN=your_tushare_token_here
STOCK_POOL=000001.SZ,600519.SH,000858.SZ,601318.SH
```

程序会自动读取该文件，无需手动配置。

**STOCK_POOL 配置说明：**
- 使用逗号分隔多个股票代码
- 支持沪深两市股票代码（如：000001.SZ、600519.SH）
- 如果未配置 STOCK_POOL，将使用默认的股票池
- 仅在守护模式（--daemon）下生效

**方式 2：环境变量**

运行前设置环境变量：
```bash
export TUSHARE_TOKEN=your_token
```

**方式 3：代码中配置**

直接在代码中设置：
```python
import tushare as ts
ts.set_token('your_token')
```

> 💡 提示：获取 TuShare token 请访问 https://tushare.pro

### 输出目录

- `charts/` - 可视化图表保存目录
- `exports/` - 数据导出文件目录

## 📝 使用场景

1. **每日复盘**: 获取持仓股票的技术指标和基本面数据
2. **选股分析**: 对比多只股票的估值和成长能力
3. **数据研究**: 导出历史数据进行量化分析
4. **价格监控**: 设置提醒，及时捕捉买卖点

## ⚠️ 免责声明

本工具仅供学习和研究使用，不构成投资建议。股市有风险，投资需谨慎。

## 📄 License

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

*每日更新，持续改进*
