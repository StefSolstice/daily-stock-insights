"""
分析 API 路由
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required
import os
import sys

api_bp = Blueprint("api", __name__)

# 导入分析模块 - 使用绝对路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


@api_bp.route("/api/analyze")
@login_required
def analyze_stock():
    """分析股票"""
    ts_code = request.args.get("ts_code", "000001.SZ")

    try:
        from stock_fetcher import StockFetcher
        from technical_indicators import TechnicalIndicators
        from advanced_indicators import AdvancedIndicators

        # 获取 TuShare token
        token = os.getenv("TUSHARE_TOKEN")
        if not token:
            return jsonify({"error": "未配置 TuShare token"}), 500

        # 获取股票数据
        fetcher = StockFetcher(token)
        df = fetcher.get_daily(ts_code)

        if df is None or df.empty:
            return jsonify({"error": "获取数据失败"}), 400

        # 计算技术指标 (遵循 main.py 的模式)
        ti = TechnicalIndicators()
        ai = AdvancedIndicators()

        # 按日期升序排列（技术指标计算需要）
        df = df.sort_values("trade_date", ascending=True).reset_index(drop=True)

        # 计算均线
        df = ti.calculate_ma(df, window=5)
        df = ti.calculate_ma(df, window=10)
        df = ti.calculate_ma(df, window=20)
        df = ti.calculate_ma(df, window=60)

        # 计算 MACD, RSI, KDJ, BOLL, ATR
        df = ti.calculate_macd(df)
        df = ti.calculate_rsi(df)
        df = ti.calculate_kdj(df)
        df = ti.calculate_bollinger_bands(df)
        df = ti.calculate_atr(df)

        # 计算成交量均线
        df = ti.calculate_vol_ma(df, window=5)
        df = ti.calculate_vol_ma(df, window=10)
        df = ti.calculate_vol_ma(df, window=20)

        # 计算高级指标
        df = ai.calculate_all_advanced_indicators(df)

        # 按日期降序排列（最新在前）
        df = df.sort_values("trade_date", ascending=False).reset_index(drop=True)

        # 获取最新数据
        latest = df.iloc[0]
        prev = df.iloc[1] if len(df) > 1 else latest

        # 计算涨跌幅
        current_price = float(latest.get("close", 0))
        prev_close = float(prev.get("close", current_price))
        change_percent = (
            ((current_price - prev_close) / prev_close * 100) if prev_close else 0
        )

        # 格式化日期用于图表
        chart_data = []
        for _, row in df.sort_values("trade_date", ascending=True).iterrows():
            chart_data.append(
                {
                    "date": str(row.get("trade_date", "")),
                    "open": float(row.get("open", 0)),
                    "high": float(row.get("high", 0)),
                    "low": float(row.get("low", 0)),
                    "close": float(row.get("close", 0)),
                    "vol": int(row.get("vol", 0)) if not pd.isna(row.get("vol")) else 0,
                    "ma5": float(row.get("close_ma5", 0))
                    if not pd.isna(row.get("close_ma5"))
                    else None,
                    "ma10": float(row.get("close_ma10", 0))
                    if not pd.isna(row.get("close_ma10"))
                    else None,
                    "ma20": float(row.get("close_ma20", 0))
                    if not pd.isna(row.get("close_ma20"))
                    else None,
                    "rsi": float(row.get("rsi", 0))
                    if not pd.isna(row.get("rsi"))
                    else None,
                    "macd": float(row.get("macd", 0))
                    if not pd.isna(row.get("macd"))
                    else None,
                    "signal": float(row.get("signal", 0))
                    if not pd.isna(row.get("signal"))
                    else None,
                    "kdj_k": float(row.get("kdj_k", 0))
                    if not pd.isna(row.get("kdj_k"))
                    else None,
                    "kdj_d": float(row.get("kdj_d", 0))
                    if not pd.isna(row.get("kdj_d"))
                    else None,
                    "kdj_j": float(row.get("kdj_j", 0))
                    if not pd.isna(row.get("kdj_j"))
                    else None,
                }
            )

        result = {
            "ts_code": ts_code,
            "current_price": current_price,
            "change_percent": round(change_percent, 2),
            "technical": {
                "ma5": round(float(latest.get("close_ma5", 0)), 2)
                if not pd.isna(latest.get("close_ma5"))
                else None,
                "ma10": round(float(latest.get("close_ma10", 0)), 2)
                if not pd.isna(latest.get("close_ma10"))
                else None,
                "ma20": round(float(latest.get("close_ma20", 0)), 2)
                if not pd.isna(latest.get("close_ma20"))
                else None,
                "ma60": round(float(latest.get("close_ma60", 0)), 2)
                if not pd.isna(latest.get("close_ma60"))
                else None,
                "rsi": round(float(latest.get("rsi", 0)), 2)
                if not pd.isna(latest.get("rsi"))
                else None,
                "kdj_k": round(float(latest.get("kdj_k", 0)), 2)
                if not pd.isna(latest.get("kdj_k"))
                else None,
                "kdj_d": round(float(latest.get("kdj_d", 0)), 2)
                if not pd.isna(latest.get("kdj_d"))
                else None,
                "kdj_j": round(float(latest.get("kdj_j", 0)), 2)
                if not pd.isna(latest.get("kdj_j"))
                else None,
                "macd": round(float(latest.get("macd", 0)), 4)
                if not pd.isna(latest.get("macd"))
                else None,
                "signal": round(float(latest.get("signal", 0)), 4)
                if not pd.isna(latest.get("signal"))
                else None,
                "bb_upper": round(float(latest.get("bb_upper", 0)), 2)
                if not pd.isna(latest.get("bb_upper"))
                else None,
                "bb_middle": round(float(latest.get("bb_middle", 0)), 2)
                if not pd.isna(latest.get("bb_middle"))
                else None,
                "bb_lower": round(float(latest.get("bb_lower", 0)), 2)
                if not pd.isna(latest.get("bb_lower"))
                else None,
            },
            "chart_data": chart_data,
        }

        return jsonify(result)

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@api_bp.route("/api/batch-analyze", methods=["POST"])
@login_required
def batch_analyze():
    """批量分析股票"""
    data = request.get_json()
    ts_codes = data.get("ts_codes", [])

    if not ts_codes:
        return jsonify({"error": "股票代码列表为空"}), 400

    if len(ts_codes) > 20:
        return jsonify({"error": "一次最多分析20只股票"}), 400

    try:
        from stock_fetcher import StockFetcher
        from technical_indicators import TechnicalIndicators
        from advanced_indicators import AdvancedIndicators

        token = os.getenv("TUSHARE_TOKEN")
        if not token:
            return jsonify({"error": "未配置 TuShare token"}), 500

        fetcher = StockFetcher(token)
        ti = TechnicalIndicators()
        ai = AdvancedIndicators()

        results = []
        for ts_code in ts_codes:
            try:
                df = fetcher.get_daily(ts_code)
                if df is None or df.empty:
                    results.append({"ts_code": ts_code, "error": "获取数据失败"})
                    continue

                df = df.sort_values("trade_date", ascending=True).reset_index(drop=True)
                df = ti.calculate_ma(df, window=5)
                df = ti.calculate_ma(df, window=10)
                df = ti.calculate_ma(df, window=20)
                df = ti.calculate_macd(df)
                df = ti.calculate_rsi(df)
                df = ti.calculate_kdj(df)
                df = ti.calculate_bollinger_bands(df)
                df = ai.calculate_all_advanced_indicators(df)
                df = df.sort_values("trade_date", ascending=False).reset_index(
                    drop=True
                )

                latest = df.iloc[0]
                prev = df.iloc[1] if len(df) > 1 else latest

                current_price = float(latest.get("close", 0))
                prev_close = float(prev.get("close", current_price))
                change_percent = (
                    ((current_price - prev_close) / prev_close * 100)
                    if prev_close
                    else 0
                )

                results.append(
                    {
                        "ts_code": ts_code,
                        "current_price": current_price,
                        "change_percent": round(change_percent, 2),
                        "ma5": round(float(latest.get("close_ma5", 0)), 2)
                        if not pd.isna(latest.get("close_ma5"))
                        else None,
                        "ma10": round(float(latest.get("close_ma10", 0)), 2)
                        if not pd.isna(latest.get("close_ma10"))
                        else None,
                        "ma20": round(float(latest.get("close_ma20", 0)), 2)
                        if not pd.isna(latest.get("close_ma20"))
                        else None,
                        "rsi": round(float(latest.get("rsi", 0)), 2)
                        if not pd.isna(latest.get("rsi"))
                        else None,
                        "kdj_k": round(float(latest.get("kdj_k", 0)), 2)
                        if not pd.isna(latest.get("kdj_k"))
                        else None,
                    }
                )
            except Exception as e:
                results.append({"ts_code": ts_code, "error": str(e)})

        return jsonify({"results": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


import pandas as pd
