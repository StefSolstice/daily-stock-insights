# AGENTS.md — Daily Stock Insights

This file provides guidance to AI agents operating in this repository.

## Project Overview

- **Type**: Python 3.11+ stock analysis CLI tool
- **Framework**: TuShare (Chinese financial data API), Flask (optional web UI)
- **Testing**: unittest (built-in)
- **Dependencies**: See `requirements.txt`

---

## Build / Lint / Test Commands

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run the Application
```bash
# Single stock analysis
python main.py --code 000001.SZ

# With custom date range
python main.py --code 600519.SH --start 20250101 --end 20251231

# Stock selection (scan market)
python main.py --select --limit 50

# Daemon mode (scheduled tasks)
python main.py --daemon

# With debug logging
python main.py --code 000001.SZ --log-level DEBUG
```

### Run Tests

```bash
# Run all tests
python test_basic.py

# Or use unittest module
python -m unittest test_basic

# Run a specific test class
python -m unittest test_basic.TestStockFetcher

# Run a single test method
python -m unittest test_basic.TestStockFetcher.test_get_daily

# Run with verbose output
python -m unittest test_basic -v
```

### Module Testing (direct execution)
Most modules have `if __name__ == "__main__":` blocks for direct testing:
```bash
python stock_fetcher.py 000001.SZ
python config_loader.py
```

---

## Code Style Guidelines

### File Header (REQUIRED)
Every `.py` file must start with:
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module description
"""
```

### Imports
- Standard library first, then third-party, then local
- Use `typing` module for type hints
- Group by: `import os, sys` → `import pandas as pd` → `from module import Class`

```python
import os
import sys
from typing import List, Dict, Optional
from datetime import datetime

import pandas as pd
import numpy as np

from config_loader import ConfigLoader
```

### Type Hints
Use type hints for function parameters and return values:
```python
def get_daily(self, symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
def calculate_ma(df: pd.DataFrame, column: str = 'close', window: int = 5) -> pd.DataFrame:
```

### Naming Conventions
| Element | Convention | Example |
|---------|-----------|---------|
| Classes | CamelCase | `StockFetcher`, `TechnicalIndicators` |
| Functions/methods | snake_case | `get_daily()`, `calculate_ma()` |
| Variables | snake_case | `ts_code`, `start_date` |
| Constants | UPPER_SNAKE | `MAX_WORKERS`, `DEFAULT_START_DAYS` |
| Private methods | _snake_case | `_load_from_env_file()` |
| Module-level logger | `logger` | `logger = get_logger(__name__)` |

### Docstrings
Chinese docstrings for user-facing modules. Use Google style:
```python
def calculate_ma(self, df: pd.DataFrame, column: str = 'close',
                 window: int = 5) -> pd.DataFrame:
    """计算移动平均线
    
    Args:
        df: 包含价格数据的 DataFrame
        column: 计算均线的列名
        window: 均线周期
        
    Returns:
        添加了均线列的 DataFrame
    """
```

### Class Structure
```python
class ClassName:
    """Class docstring"""
    
    def __init__(self, param1: str, param2: int = None):
        """Initialize"""
        self.param1 = param1
        self.param2 = param2
    
    def public_method(self) -> None:
        """Public method"""
        pass
    
    def _private_method(self) -> None:
        """Private method (prefix with _)"""
        pass
```

### Error Handling
- Use try/except with specific exception types when possible
- Always log or print errors with context
- Never suppress errors silently

```python
try:
    df = self.pro.daily(ts_code=symbol, start_date=start_date, end_date=end_date)
except Exception as e:
    print(f"获取日线数据失败: {e}", file=sys.stderr)
    return pd.DataFrame()  # Return empty DataFrame on failure
```

### Logging
Use the project's `logging_config.py`:
```python
from logging_config import setup_logging, get_logger

logger = get_logger(__name__)

logger.info(f"开始分析股票：{ts_code}")
logger.warning(f"获取基本面数据失败：{e}")
logger.error(f"分析失败：{e}", exc_info=True)
```

### DataFrames
- Always make copies when modifying: `df = df.copy()`
- Use `.reset_index(drop=True)` after transformations
- Ensure proper column types:
```python
# Convert to numeric
df[col] = pd.to_numeric(df[col], errors='coerce')

# Ensure integer volumes
df['vol'] = df['vol'].round().astype(int)
```

### File Paths
- Use `os.path.join()` for path concatenation
- Use `pathlib.Path` for modern path operations:
```python
from pathlib import Path
output_dir = Path('./data/selection')
output_dir.mkdir(parents=True, exist_ok=True)
```

### Configuration
- Use `.env` file via `python-dotenv`
- Load at module initialization:
```python
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
```

---

## Project Structure

```
daily-stock-insights/
├── main.py                 # Entry point, CLI argument parsing
├── config_loader.py        # .env and config file loading
├── stock_fetcher.py       # TuShare data fetching
├── technical_indicators.py # MA, MACD, RSI, KDJ, BOLL, ATR
├── advanced_indicators.py  # Advanced stock selection indicators
├── stock_selection.py      # Stock screening strategy
├── analyzer.py            # Stock analysis and report generation
├── fundamental_analyzer.py # PE, PB, dividends analysis
├── exporter.py            # CSV/Excel/JSON export
├── visualizer.py          # Chart generation
├── notification_service.py # Telegram/WeChat push notifications
├── alert_monitor.py       # Alert monitoring
├── logging_config.py      # Logging setup with colorlog
├── scheduler.py           # APScheduler for timed tasks
├── test_basic.py          # Unit tests
├── requirements.txt       # Dependencies
└── .env                   # API tokens (not committed)
```

---

## Key Patterns

### Env File Loading (main.py pattern)
```python
try:
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
except ImportError:
    pass
```

### Optional Dependency Handling
```python
try:
    import colorlog
    COLORLOG_AVAILABLE = True
except ImportError:
    COLORLOG_AVAILABLE = False
```

### Return Empty Collection on Failure
```python
except Exception as e:
    print(f"获取股票基本信息失败: {e}", file=sys.stderr)
    return []  # or return {}, return pd.DataFrame()
```

### DataFrame Copy Pattern
```python
def calculate_ma(self, df: pd.DataFrame, ...) -> pd.DataFrame:
    df = df.copy()  # Always copy to avoid mutation
    df[f'{column}_ma{window}'] = df[column].rolling(window=window).mean()
    return df
```

---

## Git Ignore Patterns

```
__pycache__/
*.py[cod]
.env
*.log
data/
*.csv
*.json
cache/
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `TUSHARE_TOKEN` | TuShare API token (required) |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token |
| `TELEGRAM_CHAT_ID` | Telegram chat ID |
| `WECHAT_WEBHOOK` | WeChat enterprise webhook URL |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `EXPORT_DIR` | Data export directory |
| `DATA_DIR` | Data storage directory |
