# Daily Stock Insights

基于 TuShare 的股票数据分析工具，提供全面的技术指标分析、基本面分析和选股策略。

## 功能特性

### 1. 数据层面增强
- ✅ **数据量扩展**：从原来的37条扩展到250+条（默认一年数据约250个交易日）
- ✅ **丰富数据字段**：新增换手率、量比、振幅等关键指标

### 2. 选股工具维度
- ✅ **量价关系分析**：放量上涨 vs 缩量上涨判断
- ✅ **换手率指标**：判断筹码活跃度
- ✅ **多维度涨跌幅**：当日、近5日、近20日、近60日涨跌幅
- ✅ **资金流向分析**：主力净流入/流出、资金流指数(MFI)
- ✅ **行业排名预留**：通过基本面数据获取行业信息

### 3. 个股研判维度
- ✅ **关键价位识别**：支撑位/压力位计算
- ✅ **布林带指标**：判断波动率和价格位置
- ✅ **KDJ指标**：短线超买超卖比RSI更灵敏
- ✅ **成交量均线**：量能趋势分析
- ✅ **财务数据**：PE、PB、市值等基本面指标

### 4. 推送机制
- ✅ **Telegram推送**：支持Markdown格式的消息推送
- ✅ **企业微信推送**：支持企业微信机器人推送
- ✅ **智能推送条件**：满足多重技术指标后自动推送

## 安装依赖

```bash
pip install tushare pandas numpy requests python-dotenv
```

## 配置

### 1. TuShare Token
获取免费的 TuShare Token：https://tushare.pro/

### 2. 环境变量配置
创建 `.env` 文件：
```env
TUSHARE_TOKEN=your_tushare_token_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
WECHAT_WEBHOOK=your_wechat_webhook_url
```

### 3. 选股策略配置
在配置文件中可以设置：
- 股票池（自选股）
- 扫描范围（全市场或特定板块）
- 推送条件

## 使用方法

### 1. 单只股票分析
```bash
python main.py --code 000001.SZ
```

### 2. 自定义时间段分析
```bash
python main.py --code 600519.SH --start 20250101 --end 20251231
```

### 3. 股票筛选（全市场扫描）
```bash
python main.py --select --limit 50  # 扫描前50只股票
```

### 4. 守护模式（定时任务）
```bash
python main.py --daemon
```

## 选股策略说明

### 技术面筛选条件
- MA5上穿MA10
- 成交量放大1.5倍以上
- RSI在30-70合理区间
- MACD金叉
- 股价在布林带中轨上方
- 换手率在1%-10%合理区间

### 基本面筛选条件
- PE在0-50合理区间
- PB在0-5合理区间
- 有分红记录

### 资金面筛选条件
- 主力资金净流入
- MFI在20-80合理区间
- 量价配合良好

## 文件结构

```
projects/daily-stock-insights/
├── main.py                 # 主程序入口
├── config_loader.py        # 配置加载器
├── stock_fetcher.py        # 股票数据获取器
├── technical_indicators.py # 基础技术指标
├── advanced_indicators.py  # 高级技术指标
├── stock_selection.py      # 选股策略
├── notification_service.py # 推送通知服务
├── fundamental_analyzer.py # 基本面分析
├── analyzer.py            # 综合分析器
├── exporter.py            # 数据导出器
├── visualizer.py          # 数据可视化
└── alert_monitor.py       # 预警监控器
```

## 定时任务

系统支持自动化的定时任务：
- 每个交易日9:30自动分析预设股票池
- 每日自动执行选股策略
- 支持推送符合条件的股票

## 输出格式

支持多种数据输出格式：
- CSV格式：便于Excel分析
- Excel格式：带图表的报表
- JSON格式：便于程序处理

## 注意事项

1. **API限制**：TuShare有调用频次限制，大批量扫描时请注意
2. **数据质量**：历史数据可能存在缺失，系统会自动处理
3. **网络连接**：确保网络连接稳定，避免数据获取失败
4. **推送频率**：避免过于频繁的推送，以免被限制

## 更新日志

### v2.0 - 选股增强版
- 扩展数据量至一年（约250个交易日）
- 新增换手率、资金流向等关键指标
- 实现多维度选股策略
- 集成推送通知功能

### v1.0 - 基础版
- 基础技术指标计算
- TuShare数据接入
- 基本面分析
- 数据导出功能