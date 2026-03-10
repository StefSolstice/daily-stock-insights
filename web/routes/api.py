"""
分析 API 路由
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required
import os
import sys

api_bp = Blueprint('api', __name__)

# 导入分析模块 - 使用绝对路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
from analyzer import StockAnalyzer
from stock_fetcher import StockFetcher

@api_bp.route('/api/analyze')
@login_required
def analyze_stock():
    """分析股票"""
    ts_code = request.args.get('ts_code', '000001.SZ')
    
    try:
        # 获取 TuShare token
        token = os.getenv('TUSHARE_TOKEN')
        if not token:
            return jsonify({'error': '未配置 TuShare token'}), 500
        
        # 获取股票数据
        fetcher = StockFetcher(token)
        data = fetcher.fetch_daily(ts_code, start_date='', end_date='', limit=60)
        
        if not data:
            return jsonify({'error': '获取数据失败'}), 400
        
        # 技术分析
        analyzer = StockAnalyzer(ts_code=ts_code, pro=None, data=data)
        
        # 计算指标
        df = analyzer.calculate_ma()
        df = analyzer.calculate_rsi()
        df = analyzer.calculate_kdj()
        
        # 获取最新数据
        latest = df.iloc[0] if len(df) > 0 else {}
        prev = df.iloc[1] if len(df) > 1 else {}
        
        # 计算涨跌幅
        current_price = latest.get('close', 0)
        prev_close = prev.get('close', current_price)
        change_percent = ((current_price - prev_close) / prev_close * 100) if prev_close else 0
        
        # 生成报告
        report = analyzer.generate_summary(df)
        
        result = {
            'ts_code': ts_code,
            'name': latest.get('ts_code', ''),
            'current_price': current_price,
            'change_percent': change_percent,
            'technical': {
                'ma5': round(latest.get('ma5', 0), 2) if latest.get('ma5') else None,
                'ma10': round(latest.get('ma10', 0), 2) if latest.get('ma10') else None,
                'ma20': round(latest.get('ma20', 0), 2) if latest.get('ma20') else None,
                'rsi': round(latest.get('rsi', 0), 2) if latest.get('rsi') else None,
                'kdj_k': round(latest.get('kdj_k', 0), 2) if latest.get('kdj_k') else None,
                'kdj_d': round(latest.get('kdj_d', 0), 2) if latest.get('kdj_d') else None,
                'kdj_j': round(latest.get('kdj_j', 0), 2) if latest.get('kdj_j') else None,
            },
            'report': report
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
