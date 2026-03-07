#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daily Stock Insights - 主程序
"""

import os
import sys
import argparse
from stock_fetcher import StockFetcher
from analyzer import StockAnalyzer, calculate_support_resistance, detect_patterns
from alert_monitor import PriceAlert


def cmd_stock_info(args):
    """获取股票基本信息"""
    fetcher = StockFetcher(args.token)
    
    stocks = fetcher.get_stock_basic(args.symbol)
    
    if not stocks:
        print(f"未找到股票：{args.symbol}")
        return
    
    for stock in stocks:
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"股票代码：{stock.get('ts_code')}")
        print(f"股票简称：{stock.get('symbol')}")
        print(f"股票全称：{stock.get('name')}")
        print(f"所在地区：{stock.get('area')}")
        print(f"所属行业：{stock.get('industry')}")
        print(f"上市日期：{stock.get('list_date')}")
        print(f"交易所：  {stock.get('exchange')}")
        print(f"市场：    {stock.get('market')}")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


def cmd_daily(args):
    """获取历史行情"""
    fetcher = StockFetcher(args.token)
    
    data = fetcher.get_daily(
        args.symbol, 
        start_date=args.start,
        end_date=args.end
    )
    
    if not data:
        print(f"未获取到数据：{args.symbol}")
        return
    
    # 显示数据
    print(f"\n📈 {args.symbol} 行情数据")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"{'日期':<12} {'开盘':>8} {'最高':>8} {'最低':>8} {'收盘':>8} {'涨跌幅':>10}")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    for row in data[:args.limit]:
        trade_date = row.get('trade_date', '')
        if trade_date:
            # 格式化日期
            if len(trade_date) == 8:
                trade_date = f"{trade_date[:4]}-{trade_date[4:6]}-{trade_date[6:]}"
        
        print(f"{trade_date:<12} "
              f"{row.get('open', 0):>8.2f} "
              f"{row.get('high', 0):>8.2f} "
              f"{row.get('low', 0):>8.2f} "
              f"{row.get('close', 0):>8.2f} "
              f"{row.get('pct_change', 0):>9.2f}%")
    
    # 分析数据
    if args.analyze:
        print(f"\n📊 数据分析")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        analyzer = StockAnalyzer(data)
        print(analyzer.generate_summary())
        
        # 支撑位和阻力位
        sr = calculate_support_resistance(data)
        print(f"支撑位：{sr['support']}")
        print(f"阻力位：{sr['resistance']}")
        
        # 技术形态
        patterns = detect_patterns(data)
        if patterns:
            print(f"\n🔍 检测到形态：{', '.join(patterns)}")


def cmd_quote(args):
    """获取实时报价"""
    fetcher = StockFetcher(args.token)
    
    symbols = args.symbols.split(',')
    data = fetcher.get_realtime_quote(symbols)
    
    if not data:
        print("未获取到实时数据")
        return
    
    print(f"\n📈 实时报价")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"{'代码':<12} {'名称':<10} {'现价':>8} {'涨跌':>8} {'涨跌幅':>10}")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    for row in data:
        print(f"{row.get('ts_code'):<12} "
              f"{row.get('name', ''):<10} "
              f"{row.get('close', 0):>8.2f} "
              f"{row.get('change', 0):>8.2f} "
              f"{row.get('pct_change', 0):>9.2f}%")


def cmd_watchlist(args):
    """监控自选股"""
    fetcher = StockFetcher(args.token)
    
    watchlist = args.symbols.split(',')
    
    print(f"\n📋 自选股监控")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    for symbol in watchlist:
        # 获取基本信息
        stocks = fetcher.get_stock_basic(symbol.strip())
        if stocks:
            stock = stocks[0]
            print(f"\n📌 {stock.get('name')} ({symbol})")
            print(f"   行业：{stock.get('industry')}")
            print(f"   地区：{stock.get('area')}")
        
        # 获取最新行情
        data = fetcher.get_daily(symbol.strip(), start_date=args.start, end_date=args.end)
        if data:
            latest = data[0]
            print(f"   收盘：{latest.get('close')} ({latest.get('pct_change'):.2f}%)")


def cmd_alert(args):
    """价格提醒管理"""
    alert = PriceAlert()
    
    if args.action == "add":
        alert.add_alert(args.symbol, args.type, args.price, args.name)
    elif args.action == "list":
        alert.list_alerts(args.symbol if hasattr(args, 'symbol') else None)
    elif args.action == "remove":
        idx = args.index if hasattr(args, 'index') else None
        alert.remove_alert(args.symbol, idx)
    elif args.action == "check":
        # 检查当前价格是否触发提醒
        fetcher = StockFetcher(args.token)
        data = fetcher.get_realtime_quote([args.symbol])
        if data:
            current = data[0]
            triggered = alert.check_alerts({
                args.symbol: {
                    'price': current.get('close', 0),
                    'name': current.get('name', args.symbol)
                }
            })
            alert.print_triggered_alerts(triggered)
        else:
            print(f"⚠️  无法获取 {args.symbol} 的当前价格")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="📈 Daily Stock Insights - 每日股票数据分析工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s info 000001.SZ                    查看股票基本信息
  %(prog)s daily 000001.SZ --start 20260101  获取历史行情
  %(prog)s daily 000001.SZ --analyze         获取并分析行情
  %(prog)s quote 000001.SZ,600000.SH         获取实时报价
  %(prog)s watch 000001.SZ,600000.SH          监控自选股
  %(prog)s alert add TSLA below 375 --name 特斯拉  添加价格提醒
  %(prog)s alert list                      查看所有提醒
        """
    )
    
    parser.add_argument("--token", help="TuShare API Token")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # info 命令
    info_parser = subparsers.add_parser("info", help="获取股票基本信息")
    info_parser.add_argument("symbol", help="股票代码")
    
    # daily 命令
    daily_parser = subparsers.add_parser("daily", help="获取历史行情")
    daily_parser.add_argument("symbol", help="股票代码")
    daily_parser.add_argument("--start", "-s", help="开始日期 YYYYMMDD")
    daily_parser.add_argument("--end", "-e", help="结束日期 YYYYMMDD")
    daily_parser.add_argument("--limit", "-l", type=int, default=30, help="显示条数 默认 30")
    daily_parser.add_argument("--analyze", "-a", action="store_true", help="分析数据")
    
    # quote 命令
    quote_parser = subparsers.add_parser("quote", help="获取实时报价")
    quote_parser.add_argument("symbols", help="股票代码，用逗号分隔")
    
    # watch 命令
    watch_parser = subparsers.add_parser("watch", help="监控自选股")
    watch_parser.add_argument("symbols", help="股票代码，用逗号分隔")
    watch_parser.add_argument("--start", "-s", help="开始日期 YYYYMMDD")
    watch_parser.add_argument("--end", "-e", help="结束日期 YYYYMMDD")
    
    # alert 命令
    alert_parser = subparsers.add_parser("alert", help="价格提醒管理")
    alert_subparsers = alert_parser.add_subparsers(dest="action", help="提醒操作")
    
    # alert add
    alert_add = alert_subparsers.add_parser("add", help="添加价格提醒")
    alert_add.add_argument("symbol", help="股票代码")
    alert_add.add_argument("type", choices=['above', 'below', 'cross'], help="提醒类型")
    alert_add.add_argument("price", type=float, help="目标价格")
    alert_add.add_argument("--name", "-n", help="股票名称")
    
    # alert list
    alert_list = alert_subparsers.add_parser("list", help="列出提醒")
    alert_list.add_argument("symbol", nargs="?", help="股票代码（可选）")
    
    # alert remove
    alert_remove = alert_subparsers.add_parser("remove", help="删除提醒")
    alert_remove.add_argument("symbol", help="股票代码")
    alert_remove.add_argument("--index", "-i", type=int, help="提醒编号")
    
    # alert check
    alert_check = alert_subparsers.add_parser("check", help="检查提醒")
    alert_check.add_argument("symbol", help="股票代码")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 检查 token
    if not args.token and not os.getenv('TUSHARE_TOKEN'):
        print("请设置 TUSHARE_TOKEN 环境变量或使用 --token 参数")
        sys.exit(1)
    
    # 执行命令
    if args.command == "info":
        cmd_stock_info(args)
    elif args.command == "daily":
        cmd_daily(args)
    elif args.command == "quote":
        cmd_quote(args)
    elif args.command == "watch":
        cmd_watchlist(args)
    elif args.command == "alert":
        cmd_alert(args)


if __name__ == "__main__":
    main()
