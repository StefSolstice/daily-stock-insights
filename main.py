#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daily Stock Insights - 每日股票洞察
主程序入口
"""

import sys
import io
# 兼容tushare和新版pandas
# 先mock pandas.util.testing模块
sys.modules['pandas.util.testing'] = type('obj', (object,), {
    '_network_error_classes': (ConnectionError, IOError)
})()

import pandas.compat
pandas.compat.StringIO = io.StringIO

import tushare as ts
import os
from datetime import datetime
from typing import Optional

from stock_fetcher import StockFetcher
from analyzer import StockAnalyzer
from fundamental_analyzer import FundamentalAnalyzer
from visualizer import StockVisualizer, generate_visualization_report
from exporter import DataExporter
from alert_monitor import PriceAlert as AlertMonitor


def init_tushare() -> Optional[ts.pro_api]:
    """初始化 TuShare API
    
    Returns:
        pro API 实例或 None
    """
    # 尝试从环境变量获取 token
    token = os.getenv('TUSHARE_TOKEN')
    
    # 如果环境变量未设置，尝试从 .env 文件读取
    if not token:
        env_file = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        if key.strip() == 'TUSHARE_TOKEN':
                            token = value.strip()
                            os.environ['TUSHARE_TOKEN'] = token
                            break
    
    if not token:
        print("⚠️  未找到 TUSHARE_TOKEN 环境变量")
        print("请在 https://tushare.pro 注册并获取 token")
        print("然后设置：export TUSHARE_TOKEN='your_token'")
        return None
    
    ts.set_token(token)
    try:
        pro = ts.pro_api()
        print("✓ TuShare API 初始化成功")
        return pro
    except Exception as e:
        print(f"❌ TuShare API 初始化失败：{e}")
        return None


def daily_analysis(ts_code: str, name: str, pro: ts.pro_api, 
                   days: int = 100, output_charts: bool = True,
                   export_data: bool = True) -> dict:
    """执行每日分析
    
    Args:
        ts_code: 股票代码
        name: 股票名称
        pro: TuShare pro API
        days: 分析天数
        output_charts: 是否输出图表
        export_data: 是否导出数据
    
    Returns:
        分析结果字典
    """
    print(f"\n{'='*60}")
    print(f"📊 每日股票洞察 - {name} ({ts_code})")
    print(f"分析日期：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}\n")
    
    results = {
        'ts_code': ts_code,
        'name': name,
        'analysis_date': datetime.now().isoformat(),
        'technical': {},
        'fundamental': {},
        'charts': [],
        'exports': []
    }
    
    # 1. 获取历史数据
    print("📥 获取历史数据...")
    fetcher = StockFetcher()
    df = fetcher.get_daily(ts_code, start_date=None, end_date=None)
    
    if df is None or df.empty:
        print("❌ 无法获取股票数据")
        return results
    
    print(f"✓ 获取到 {len(df)} 条数据")
    
    # 2. 技术分析
    print("\n📈 技术分析...")
    analyzer = StockAnalyzer(ts_code, pro)
    df_with_indicators = analyzer.calculate_all_indicators(df)
    
    # 获取最新数据
    latest = df_with_indicators.iloc[-1]
    prev = df_with_indicators.iloc[-2] if len(df_with_indicators) > 1 else latest
    
    results['technical'] = {
        'date': latest.get('trade_date', ''),
        'close': latest.get('close', 0),
        'change': latest.get('close', 0) - prev.get('close', 0),
        'change_pct': ((latest.get('close', 0) / prev.get('close', 1) - 1) * 100) if prev.get('close', 0) != 0 else 0,
        'volume': latest.get('vol', 0),
        'ma5': latest.get('close_ma5', 0),
        'ma10': latest.get('close_ma10', 0),
        'ma20': latest.get('close_ma20', 0),
        'macd': latest.get('macd', 0),
        'rsi': latest.get('rsi', 0),
        'kdj_k': latest.get('kdj_k', 0),
        'kdj_d': latest.get('kdj_d', 0),
        'kdj_j': latest.get('kdj_j', 0),
        'cci': latest.get('cci', 0),
        'boll_upper': latest.get('boll_upper', 0),
        'boll_lower': latest.get('boll_lower', 0)
    }
    
    # 打印技术摘要
    print(f"\n最新价格：{results['technical']['close']:.2f}")
    print(f"涨跌幅：{results['technical']['change']:+.2f} ({results['technical']['change_pct']:+.2f}%)")
    print(f"成交量：{results['technical']['volume']:,.0f}")
    print(f"MA5: {results['technical']['ma5']:.2f}, MA10: {results['technical']['ma10']:.2f}, MA20: {results['technical']['ma20']:.2f}")
    print(f"RSI: {results['technical']['rsi']:.2f}, KDJ: {results['technical']['kdj_k']:.1f}/{results['technical']['kdj_d']:.1f}/{results['technical']['kdj_j']:.1f}")
    
    # 3. 基本面分析
    print("\n🏢 基本面分析...")
    fundamental = FundamentalAnalyzer(ts_code, pro)
    
    try:
        valuation = fundamental.get_valuation_metrics()
        profitability = fundamental.get_profitability_metrics()
        growth = fundamental.get_growth_metrics()
        
        results['fundamental'] = {
            'pe_ttm': valuation.get('pe_ttm'),
            'pb': valuation.get('pb'),
            'dv_ratio': valuation.get('dv_ratio'),
            'roe': profitability.get('roe_wa'),
            'gross_margin': profitability.get('gross_margin'),
            'yoy_sales': growth.get('yoy_sales'),
            'yoy_net_profit': growth.get('yoy_net_profit'),
        }
        
        if valuation:
            print(f"PE(TTM): {valuation.get('pe_ttm', 'N/A')}")
            print(f"PB: {valuation.get('pb', 'N/A')}")
            print(f"股息率：{valuation.get('dv_ratio', 'N/A')}%")
        if profitability:
            print(f"ROE: {profitability.get('roe_wa', 'N/A')}%")
            print(f"毛利率：{profitability.get('gross_margin', 'N/A')}%")
        if growth:
            print(f"营收增速：{growth.get('yoy_sales', 'N/A')}%")
            print(f"净利润增速：{growth.get('yoy_net_profit', 'N/A')}%")
    except Exception as e:
        print(f"⚠️  基本面分析跳过：{e}")
        results['fundamental'] = {'error': str(e)}
    
    # 4. 生成分析报告
    print("\n" + "="*60)
    tech_report = analyzer.generate_summary(df_with_indicators)
    print(tech_report)
    
    try:
        fund_report = fundamental.generate_fundamental_report()
        print(fund_report)
    except Exception as e:
        print(f"⚠️  基本面报告跳过：{e}")
    
    # 5. 可视化
    if output_charts:
        print("\n📊 生成可视化图表...")
        os.makedirs('charts', exist_ok=True)
        os.makedirs('exports', exist_ok=True)
        
        # 重命名 trade_date 为 date，适配 visualizer
        df_for_viz = df_with_indicators.copy()
        if 'trade_date' in df_for_viz.columns and 'date' not in df_for_viz.columns:
            df_for_viz = df_for_viz.rename(columns={'trade_date': 'date'})
        
        viz = StockVisualizer(df_for_viz, ts_code, name)
        
        # K 线图
        kline_path = f"charts/{ts_code}_kline_{datetime.now().strftime('%Y%m%d')}.png"
        viz.plot_kline(save_path=kline_path, show=False)
        results['charts'].append(kline_path)
        
        # 指标图
        indicators_path = f"charts/{ts_code}_indicators_{datetime.now().strftime('%Y%m%d')}.png"
        viz.plot_with_indicators(
            indicators=['MA5', 'MA10', 'MA20', 'VOL', 'MACD'],
            save_path=indicators_path,
            show=False
        )
        results['charts'].append(indicators_path)
        
        print(f"✓ 已生成 {len(results['charts'])} 张图表")
    
    # 6. 数据导出
    if export_data:
        print("\n💾 导出数据...")
        exporter = DataExporter(df_with_indicators, ts_code, name)
        
        export_paths = exporter.export_all()
        results['exports'] = list(export_paths.values())
        
        print(f"✓ 已导出 {len(results['exports'])} 个文件")
    
    # 7. 检查提醒
    print("\n🔔 检查价格提醒...")
    try:
        monitor = AlertMonitor()  # 使用默认 alerts.json 配置文件
        current_price = df_with_indicators.iloc[0]['close']
        current_prices = {ts_code: {'price': current_price, 'name': name}}
        alerts = monitor.check_alerts(current_prices)
        if alerts:
            print(f"⚠️  触发 {len(alerts)} 个价格提醒:")
            for alert in alerts:
                print(f"   - {alert['type']}: {alert['condition']} (当前：{alert['current_price']})")
        else:
            print("✓ 无触发的价格提醒")
    except Exception as e:
        print(f"⚠️  价格提醒检查跳过：{e}")
    
    print(f"\n{'='*60}")
    print("✅ 分析完成!")
    print(f"{'='*60}\n")
    
    return results


def run_daily_task(ts_codes: list = None, output_charts: bool = True,
                   export_data: bool = True):
    """执行每日任务
    
    Args:
        ts_codes: 股票代码列表
        output_charts: 是否输出图表
        export_data: 是否导出数据
    """
    # 初始化 TuShare
    pro = init_tushare()
    if not pro:
        return
    
    # 默认股票池（可自定义）
    if not ts_codes:
        ts_codes = [
            ('000001.SZ', '平安银行'),
            ('000002.SZ', '万科 A'),
            ('600000.SH', '浦发银行'),
        ]
    
    # 遍历股票池
    for ts_code, name in ts_codes:
        try:
            daily_analysis(
                ts_code=ts_code,
                name=name,
                pro=pro,
                output_charts=output_charts,
                export_data=export_data
            )
        except Exception as e:
            print(f"❌ {name} 分析失败：{e}")
            continue


if __name__ == "__main__":
    import sys
    
    # 命令行参数
    if len(sys.argv) > 1:
        ts_code = sys.argv[1]
        name = sys.argv[2] if len(sys.argv) > 2 else ''
        
        pro = init_tushare()
        if pro:
            daily_analysis(ts_code, name, pro)
    else:
        # 无参数时执行默认股票池
        run_daily_task()
