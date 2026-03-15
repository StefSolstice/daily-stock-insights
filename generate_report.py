#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成直观的股票分析报告
"""

import pandas as pd
import os

def generate_intuitive_report(csv_file):
    """生成直观的股票分析报告"""
    
    if not os.path.exists(csv_file):
        print(f"❌ 文件不存在: {csv_file}")
        return
    
    # 读取CSV文件
    df = pd.read_csv(csv_file)
    
    # 获取股票代码和名称
    ts_code = df['ts_code'].iloc[0] if 'ts_code' in df.columns else 'Unknown'
    
    print('📊 股票数据分析报告')
    print('=' * 60)
    print(f'股票代码: {ts_code}')
    print(f'数据条目数: {len(df)}')
    print(f'日期范围: {df["trade_date"].iloc[-1]} 到 {df["trade_date"].iloc[0]}')
    print('📊 数据说明: 成交量单位为"手"(1手=100股)，成交额单位为"千元"')
    print()
    
    # 显示最近5个交易日的详细数据
    print('📈 最近5个交易日详情:')
    print('-' * 80)
    columns_needed = ['trade_date', 'open', 'high', 'low', 'close', 'vol', 'amount']
    available_columns = [col for col in columns_needed if col in df.columns]
    recent_data = df.head(5)[available_columns]
    for idx, row in recent_data.iterrows():
        # 注意：TuShare的vol单位是"手"(1手=100股)，amount单位是"千元"
        vol_str = f"{row['vol']:,.2f}"  # 保持原始单位显示
        # amount是元，显示为万元
        amount_wan = row['amount'] / 10000  # 元/10000 = 万元
        print(f"📅 {row['trade_date']} | "
              f"开盘:{row['open']:>7.2f} | "
              f"最高:{row['high']:>7.2f} | "
              f"最低:{row['low']:>7.2f} | "
              f"收盘:{row['close']:>7.2f} | "
              f"成交量:{vol_str:>9}手 | "
              f"成交额:{amount_wan:>7.1f}万")
    print()
    
    # 价格统计
    print('💰 价格统计分析:')
    print('-' * 40)
    print(f'最高价(日内): {df["high"].max():>7.2f}')
    print(f'最低价(日内): {df["low"].min():>7.2f}')
    print(f'当前收盘价: {df["close"].iloc[0]:>7.2f}')
    print(f'平均收盘价: {df["close"].mean():>7.2f}')
    print(f'收盘价区间: {df["close"].min():.2f} ~ {df["close"].max():.2f}')
    print()
    
    # 技术指标分析
    print('📊 技术指标分析:')
    print('-' * 40)
    
    # MA指标 (寻找最近的有效值，而不仅仅是第一行)
    if 'close_ma5' in df.columns and not df['close_ma5'].isna().all():
        # 找到最近的有效MA值
        ma5_latest = df['close_ma5'].dropna().iloc[0] if not df['close_ma5'].dropna().empty else 'N/A'
        ma10_latest = df['close_ma10'].dropna().iloc[0] if not df['close_ma10'].dropna().empty else 'N/A'
        ma20_latest = df['close_ma20'].dropna().iloc[0] if not df['close_ma20'].dropna().empty else 'N/A'
        print(f'MA5:  {ma5_latest if isinstance(ma5_latest, str) else ma5_latest:>6.2f} | MA10: {ma10_latest if isinstance(ma10_latest, str) else ma10_latest:>6.2f} | MA20: {ma20_latest if isinstance(ma20_latest, str) else ma20_latest:>6.2f}')
    
    # MACD指标 (获取最新的有效值)
    if 'macd' in df.columns and not df['macd'].isna().all():
        # 获取当前（最新）的MACD值，而不是第一个
        macd_latest = df['macd'].iloc[0] if not pd.isna(df['macd'].iloc[0]) else 'N/A'
        signal_latest = df['signal'].iloc[0] if not pd.isna(df['signal'].iloc[0]) else 'N/A'
        histogram_latest = df['histogram'].iloc[0] if not pd.isna(df['histogram'].iloc[0]) else 'N/A'
        if isinstance(macd_latest, str):
            print(f'MACD: {macd_latest:>6} | Signal: {signal_latest:>6} | Histogram: {histogram_latest:>6}')
        else:
            print(f'MACD: {macd_latest:>6.3f} | Signal: {signal_latest:>6.3f} | Histogram: {histogram_latest:>6.3f}')
    
    # RSI指标 (获取最新的有效值)
    if 'rsi' in df.columns and not df['rsi'].isna().all():
        rsi_latest = df['rsi'].iloc[0] if not pd.isna(df['rsi'].iloc[0]) else 'N/A'
        if isinstance(rsi_latest, str):
            print(f'RSI:  {rsi_latest:>6}')
        else:
            print(f'RSI:  {rsi_latest:>6.2f}')
    
    print()
    
    # 数据质量统计
    print('🔍 数据质量统计:')
    print('-' * 40)
    total_records = len(df)
    print(f'总记录数: {total_records}')
    
    if 'close_ma5' in df.columns:
        ma5_valid = df['close_ma5'].count()
        print(f'MA5 有效数据: {ma5_valid}/{total_records} ({ma5_valid/total_records*100:.1f}%)')
    
    if 'rsi' in df.columns:
        rsi_valid = df['rsi'].count()
        print(f'RSI 有效数据: {rsi_valid}/{total_records} ({rsi_valid/total_records*100:.1f}%)')
    
    if 'macd' in df.columns:
        macd_valid = df['macd'].count()
        print(f'MACD 有效数据: {macd_valid}/{total_records} ({macd_valid/total_records*100:.1f}%)')
    
    print()
    print('📁 报告文件:')
    print(f'- CSV: {csv_file}')
    print(f'- Excel: {csv_file.replace(".csv", ".xlsx")}')
    print(f'- JSON: {csv_file.replace(".csv", ".json")}')


if __name__ == "__main__":
    import sys
    import glob
    from datetime import datetime
    
    # 如果提供了参数，当作股票代码处理
    if len(sys.argv) > 1:
        stock_code = sys.argv[1]
        # 查找对应的最新文件
        today = datetime.now().strftime('%Y%m%d')
        latest_csv = f"exports/{stock_code}_{today}.csv"
        
        # 如果今天的文件不存在，找最近的文件
        if not os.path.exists(latest_csv):
            # 搜索所有该股票的导出文件
            files = glob.glob(f"exports/{stock_code}_*.csv")
            if files:
                # 按文件名排序，选择最新的
                latest_csv = sorted(files)[-1]
            else:
                print(f"❌ 未找到股票 {stock_code} 的导出文件")
                print("可用的导出文件:")
                all_files = glob.glob("exports/*.csv")
                for f in sorted(all_files)[-10:]:  # 显示最近10个文件
                    print(f"  - {os.path.basename(f)}")
                sys.exit(1)
    else:
        # 默认分析最新的导出文件
        # 搜索所有导出文件，选择最新的
        all_files = glob.glob("exports/*.csv")
        if all_files:
            latest_csv = sorted(all_files)[-1]
        else:
            print("❌ 未找到任何导出文件")
            sys.exit(1)
    
    generate_intuitive_report(latest_csv)