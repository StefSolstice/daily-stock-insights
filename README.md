# 📈 Daily Stock Insights

基于 TuShare API 的每日股票数据获取与分析工具。

**最后更新：** 2026-03-06

## 功能特性

- 📊 获取股票基本信息
- 📈 获取历史行情数据
- 📉 **技术指标分析（新增）** - 支持 8 种技术指标
- 🔍 简单的技术指标分析
- 📝 每日自动更新数据
- 🖥️ 命令行友好

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