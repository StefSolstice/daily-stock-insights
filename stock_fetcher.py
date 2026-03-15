#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TuShare 股票数据获取模块
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any


class StockFetcher:
    """股票数据获取器"""
    
    def __init__(self, token: str = None):
        """初始化
        
        Args:
            token: TuShare API Token，默认从环境变量读取；也可以是 pro_api 对象
        """
        # 如果传入的是 pro_api 对象，直接使用
        if hasattr(token, 'daily'):  # 检查是否是 pro_api 对象
            self.pro = token
        else:
            # 否则从 token 或环境变量获取
            token = token or os.getenv('TUSHARE_TOKEN')
            if not token:
                raise ValueError("请设置 TUSHARE_TOKEN 环境变量")
            
            import tushare as ts
            ts.set_token(token)
            self.pro = ts.pro_api()
    
    def get_stock_basic(self, symbol: str = None) -> List[Dict]:
        """获取股票基本信息
        
        Args:
            symbol: 股票代码，如 000001.SZ
        
        Returns:
            股票基本信息列表
        """
        try:
            params = {}
            if symbol:
                params["ts_code"] = symbol
            
            fields = "ts_code,symbol,name,area,industry,list_date,market,exchange"
            df = self.pro.stock_basic(**params, fields=fields)
            
            # 转换为字典列表
            if df.empty:
                return []
            return df.to_dict('records')
        except Exception as e:
            print(f"获取股票基本信息失败: {e}", file=sys.stderr)
            return []
    
    def get_daily(self, symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """获取日线行情数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD
        
        Returns:
            行情数据 DataFrame
        """
        # 默认获取最近30天数据
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
        
        try:
            fields = "ts_code,trade_date,open,high,low,close,pre_close,change,pct_change,vol,amount"
            df = self.pro.daily(ts_code=symbol, start_date=start_date, end_date=end_date, fields=fields)
            
            # 将数值列转换为数字类型
            numeric_cols = ['open', 'high', 'low', 'close', 'pre_close', 'change', 'pct_change', 'vol', 'amount']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 按日期降序排列（最新日期在前）
            df = df.sort_values('trade_date', ascending=False).reset_index(drop=True)
            
            return df
        except Exception as e:
            print(f"获取日线数据失败: {e}", file=sys.stderr)
            return pd.DataFrame()
    
    def get_realtime_quote(self, symbols: List[str]) -> List[Dict]:
        """获取实时行情（需要实时行情权限）
        
        Args:
            symbols: 股票代码列表
        
        Returns:
            实时行情列表
        """
        try:
            # TuShare 没有专门的实时行情接口，使用当日数据
            results = []
            for symbol in symbols:
                df = self.pro.daily(ts_code=symbol, start_date=datetime.now().strftime("%Y%m%d"), 
                                  end_date=datetime.now().strftime("%Y%m%d"))
                if not df.empty:
                    record = df.iloc[0].to_dict()
                    results.append(record)
            return results
        except Exception as e:
            print(f"获取实时行情失败: {e}", file=sys.stderr)
            return []
    
    def get_trade_cal(self, start_date: str, end_date: str, exchange: str = "SSE") -> List[Dict]:
        """获取交易日历
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            exchange: 交易所 SSE上交所,SZSE深交所,CFFEX期交所
        
        Returns:
            交易日列表
        """
        try:
            df = self.pro.trade_cal(exchange=exchange, start_date=start_date, end_date=end_date)
            return df.to_dict('records') if not df.empty else []
        except Exception as e:
            print(f"获取交易日历失败: {e}", file=sys.stderr)
            return []


def main():
    """测试函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="股票数据获取工具")
    parser.add_argument("symbol", help="股票代码")
    parser.add_argument("--token", help="TuShare Token")
    
    args = parser.parse_args()
    
    try:
        fetcher = StockFetcher(args.token)
        
        # 获取股票信息
        print(f"获取股票信息: {args.symbol}")
        info = fetcher.get_stock_basic(args.symbol)
        for stock in info:
            print(f"  代码: {stock.get('ts_code')}")
            print(f"  名称: {stock.get('name')}")
            print(f"  地区: {stock.get('area')}")
            print(f"  行业: {stock.get('industry')}")
            print(f"  上市日期: {stock.get('list_date')}")
            print()
        
        # 获取日线数据
        print(f"获取日线数据: {args.symbol}")
        df = fetcher.get_daily(args.symbol)
        if not df.empty:
            print(f"  获取到 {len(df)} 条数据")
            if len(df) > 0:
                latest = df.iloc[0]
                print(f"  最新价格: {latest.get('close', 'N/A')}")
                print(f"  最新成交量: {latest.get('vol', 'N/A')} 手")
                print(f"  最新成交额: {latest.get('amount', 'N/A')} 元")
        else:
            print("  未获取到数据")
    
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    main()