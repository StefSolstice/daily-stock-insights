#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
daily-stock-insights 主程序
基于 TuShare 的股票数据分析工具

支持：
- 单次运行分析指定股票
- 定时任务调度（每个交易日自动运行）
- 数据导出（CSV/Excel/JSON）
- 技术指标计算
- 基本面分析
"""

import argparse
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# 首先加载 .env 文件（在其他模块之前）
try:
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"[DEBUG] 已加载 .env 文件：{env_path}")
    else:
        print(f"[DEBUG] .env 文件不存在：{env_path}")
except ImportError:
    print("[DEBUG] python-dotenv 未安装，跳过 .env 加载")

# 导入日志配置
from logging_config import setup_logging, get_logger
# 导入调度器
from scheduler import TaskScheduler
# 导入核心模块
from config_loader import ConfigLoader
from stock_fetcher import StockFetcher
from technical_indicators import TechnicalIndicators
from fundamental_analyzer import FundamentalAnalyzer
from analyzer import Analyzer
from exporter import DataExporter
from visualizer import Visualizer
from alert_monitor import AlertMonitor


# 模块级日志记录器
logger = get_logger(__name__)


def run_single_analysis(ts_code: str, start_date: str, end_date: str, 
                        output_dir: str, config: dict) -> bool:
    """执行单次股票分析
    
    Args:
        ts_code: 股票代码
        start_date: 开始日期
        end_date: 结束日期
        output_dir: 输出目录
        config: 配置字典
        
    Returns:
        是否成功
    """
    try:
        logger.info(f"开始分析股票：{ts_code}")
        
        # 初始化模块
        fetcher = StockFetcher()
        ti = TechnicalIndicators()
        fundamental = FundamentalAnalyzer(ts_code)
        
        # 获取数据
        logger.info(f"获取股票数据：{ts_code} ({start_date} - {end_date})")
        df = fetcher.get_daily(ts_code, start_date, end_date)
        
        if df is None or df.empty:
            logger.error(f"获取数据失败：{ts_code}")
            return False
        
        logger.info(f"获取到 {len(df)} 条数据")
        
        # 处理成交量数据，确保为整数（成交量单位为手，应为整数）
        if 'vol' in df.columns:
            # TuShare API返回的vol有时会有小数，但成交量应为整数
            df['vol'] = df['vol'].round().astype(int)  # 四舍五入取整
        
        # 确保数据按日期升序排列（技术指标计算需要时间序列顺序）
        df = df.sort_values('trade_date', ascending=True).reset_index(drop=True)
        
        # 计算技术指标
        logger.info("计算技术指标...")
        df = ti.calculate_ma(df, window=5)
        df = ti.calculate_ma(df, window=10)
        df = ti.calculate_ma(df, window=20)
        df = ti.calculate_ma(df, window=60)  # 年线
        df = ti.calculate_macd(df)
        df = ti.calculate_rsi(df)
        df = ti.calculate_kdj(df)
        df = ti.calculate_bollinger_bands(df)
        df = ti.calculate_atr(df)
        df = ti.calculate_vol_ma(df, window=5)
        df = ti.calculate_vol_ma(df, window=10)
        df = ti.calculate_vol_ma(df, window=20)
        
        # 将数据按日期降序排列（最新的在前，便于查看）
        df = df.sort_values('trade_date', ascending=False).reset_index(drop=True)
        
        # 确保成交量为整数（在所有处理完成后）
        if 'vol' in df.columns:
            df['vol'] = df['vol'].round().astype(int)
        
        # 初始化导出器（在获取数据后）
        exporter = DataExporter(df, ts_code)
        
        # 基本面分析
        logger.info("获取基本面数据...")
        try:
            # 尝试使用 FundamentalAnalyzer 的方法
            valuation = fundamental.get_valuation_metrics()
            if valuation:
                logger.info(f"市盈率 (PE): {valuation.get('pe', 'N/A')}")
                logger.info(f"市盈率 (TTM): {valuation.get('pe_ttm', 'N/A')}")
                logger.info(f"市净率 (PB): {valuation.get('pb', 'N/A')}")
                logger.info(f"股息率：{valuation.get('dv_ratio', 'N/A')}")
        except Exception as e:
            logger.warning(f"获取基本面数据失败：{e}")
        
        # 导出数据
        logger.info(f"导出数据到：{output_dir}")
        csv_file = exporter.to_csv(output_dir=output_dir)
        logger.info(f"CSV 文件：{csv_file}")
        
        excel_file = exporter.to_excel(output_dir=output_dir)
        logger.info(f"Excel 文件：{excel_file}")
        
        json_file = exporter.to_json(output_dir=output_dir)
        logger.info(f"JSON 文件：{json_file}")
        
        logger.info(f"分析完成：{ts_code}")
        return True
        
    except Exception as e:
        logger.error(f"分析失败：{e}", exc_info=True)
        return False


def run_daily_analysis(config: dict):
    """执行每日自动分析（预设股票池）"""
    logger.info("开始每日自动分析...")
    
    # 从配置中读取股票池，如果没有配置则使用默认股票池
    default_stock_pool = [
        '000001.SZ',  # 平安银行
        '600519.SH',  # 贵州茅台
        '000858.SZ',  # 五粮液
        '601318.SH',  # 中国平安
    ]
    
    # 优先从配置中读取股票池
    stock_pool = config.get('STOCK_POOL', default_stock_pool)
    
    # 如果配置中的股票池为空，使用默认股票池
    if not stock_pool or len(stock_pool) == 0:
        stock_pool = default_stock_pool
    
    # 计算日期（最近一个交易日），获取更多历史数据以确保技术指标的准确性
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')  # 一年历史数据
    
    output_dir = './data/daily'
    
    success_count = 0
    for ts_code in stock_pool:
        if run_single_analysis(ts_code, start_date, end_date, output_dir, config):
            success_count += 1
    
    logger.info(f"每日分析完成：成功 {success_count}/{len(stock_pool)}")


def setup_scheduler(config: dict) -> TaskScheduler:
    """配置并启动调度器
    
    Args:
        config: 配置字典
        
    Returns:
        调度器实例
    """
    scheduler = TaskScheduler(use_background=True)
    
    # 添加每日分析任务（交易日 9:30）
    scheduler.add_job(
        job_id='daily_analysis',
        func=run_daily_analysis,
        trigger_type='cron',
        hour=9,
        minute=30,
        day_of_week='mon-fri',
        kwargs={'config': config}
    )
    
    logger.info("定时任务已配置：每个交易日 9:30 执行")
    
    return scheduler


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='daily-stock-insights - 基于 TuShare 的股票数据分析工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  %(prog)s --code 000001.SZ                    # 分析平安银行
  %(prog)s --code 600519.SH --start 20260101   # 分析贵州茅台（从 2026 年初开始）
  %(prog)s --daemon                            # 启动守护模式（定时任务）
  %(prog)s --code 000001.SZ --export ./output  # 分析并导出到指定目录
        '''
    )
    
    parser.add_argument('--code', type=str, help='股票代码 (如：000001.SZ)')
    parser.add_argument('--start', type=str, help='开始日期 (YYYYMMDD)，默认 60 天前')
    parser.add_argument('--end', type=str, help='结束日期 (YYYYMMDD)，默认今天')
    parser.add_argument('--export', type=str, default='./exports', help='导出目录')
    parser.add_argument('--daemon', action='store_true', help='启动守护模式（定时任务）')
    parser.add_argument('--log-level', type=str, default='INFO', 
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='日志级别')
    parser.add_argument('--log-file', type=str, help='日志文件路径')
    
    args = parser.parse_args()
    
    # 初始化日志系统
    log_level = getattr(__import__('logging'), args.log_level)
    setup_logging(
        level=log_level,
        log_file=args.log_file,
        console_output=True,
        file_output=True
    )
    
    logger.info("=" * 60)
    logger.info("daily-stock-insights 启动")
    logger.info(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    # 加载配置
    try:
        config_loader = ConfigLoader()
        config = config_loader.load()
        logger.info("配置加载成功")
    except Exception as e:
        logger.warning(f"配置加载失败，使用默认配置：{e}")
        config = {}
    
    # 守护模式：启动定时任务
    if args.daemon:
        logger.info("启动守护模式...")
        scheduler = setup_scheduler(config)
        
        try:
            scheduler.start()
            # 保持主线程运行
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("收到中断信号，关闭调度器...")
            scheduler.shutdown()
        except Exception as e:
            logger.error(f"守护模式异常：{e}")
            scheduler.shutdown()
            sys.exit(1)
    
    # 单次分析模式
    elif args.code:
        ts_code = args.code
        
        # 计算日期
        if not args.end:
            end_date = datetime.now().strftime('%Y%m%d')
        else:
            end_date = args.end
        
        if not args.start:
            # 获取更多历史数据以确保技术指标的准确性（至少250个交易日）
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
        else:
            start_date = args.start
        
        # 执行分析
        success = run_single_analysis(ts_code, start_date, end_date, args.export, config)
        
        if success:
            logger.info("分析成功完成")
            sys.exit(0)
        else:
            logger.error("分析失败")
            sys.exit(1)
    
    # 无参数：显示帮助
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
