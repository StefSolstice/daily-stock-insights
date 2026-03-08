#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TuShare 股票数据获取模块
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any


class StockFetcher:
    """股票数据获取器"""
    
    BASE_URL = "https://api.tushare.pro"
    
    def __init__(self, token: str = None):
        """初始化
        
        Args:
            token: TuShare API Token，默认从环境变量读取
        """
        self.token = token or os.getenv('TUSHARE_TOKEN')
        if not self.token:
            raise ValueError("请设置 TUSHARE_TOKEN 环境变量")
    
    def _request(self, api_name: str, params: Dict = None, fields: str = None) -> Dict:
        """发送请求到 TuShare API
        
        Args:
            api_name: API 名称
            params: 请求参数
            fields: 返回字段
        
        Returns:
            API 响应结果
        """
        payload = {
            "api_name": api_name,
            "token": self.token,
            "params": params or {},
        }
        if fields:
            payload["fields"] = fields
        
        try:
            response = requests.post(self.BASE_URL, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") != 0:
                print(f"API Error: {result.get('msg')}", file=sys.stderr)
                return {"data": {"items": [], "fields": []}}
            
            return result
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}", file=sys.stderr)
            return {"data": {"items": [], "fields": []}}
    
    def get_stock_basic(self, symbol: str = None) -> List[Dict]:
        """获取股票基本信息
        
        Args:
            symbol: 股票代码，如 000001.SZ
        
        Returns:
            股票基本信息列表
        """
        params = {}
        if symbol:
            params["ts_code"] = symbol
        
        fields = "ts_code,symbol,name,area,industry,list_date,market,exchange"
        result = self._request("stock_basic", params, fields)
        
        items = result.get("data", {}).get("items", [])
        fields_list = result.get("data", {}).get("fields", [])
        
        return [dict(zip(fields_list, item)) for item in items]
    
    def get_daily(self, symbol: str, start_date: str = None, end_date: str = None) -> List[Dict]:
        """获取日线行情数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD
        
        Returns:
            行情数据列表
        """
        # 默认获取最近30天数据
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
        
        params = {
            "ts_code": symbol,
            "start_date": start_date,
            "end_date": end_date
        }
        
        fields = "ts_code,trade_date,open,high,low,close,pre_close,change,pct_change,vol,amount"
        result = self._request("daily", params, fields)
        
        items = result.get("data", {}).get("items", [])
        fields_list = result.get("data", {}).get("fields", [])
        
        return [dict(zip(fields_list, item)) for item in items]
    
    def get_realtime_quote(self, symbols: List[str]) -> List[Dict]:
        """获取实时行情（需要实时行情权限）
        
        Args:
            symbols: 股票代码列表
        
        Returns:
            实时行情列表
        """
        params = {
            "ts_code": ",".join(symbols)
        }
        
        fields = "ts_code,name,open,high,low,close,pre_close,change,pct_change,vol,amount,trade_time"
        result = self._request("realtime_quote", params, fields)
        
        items = result.get("data", {}).get("items", [])
        fields_list = result.get("data", {}).get("fields", [])
        
        return [dict(zip(fields_list, item)) for item in items]
    
    def get_trade_cal(self, start_date: str, end_date: str) -> List[Dict]:
        """获取交易日历
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            交易日列表
        """
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "exchange": "SSE"
        }
        
        fields = "exchange,cal_date,is_open,pretrade_date"
        result = self._request("trade_cal", params, fields)
        
        items = result.get("data", {}).get("items", [])
        fields_list = result.get("data", {}).get("fields", [])
        
        return [dict(zip(fields_list, item)) for item in items]


def main():
    """测试函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="股票数据获取工具")
    parser.add_argument("symbol", help="股票代码")
    parser.add_argument("--token", help="TuShare Token")
    
    args = parser.parse_args()
    
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


if __name__ == "__main__":
    main()