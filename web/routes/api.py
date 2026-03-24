from flask import Blueprint, jsonify, request
from flask_login import login_required
import os
import sys
import pandas as pd

api_bp = Blueprint("api", __name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def calculate_comprehensive_score(df, latest, prev):
    """计算综合评分 (0-100)"""
    score = 0
    details = {}

    current_price = float(latest.get("close", 0))
    ma5 = (
        float(latest.get("close_ma5", 0)) if not pd.isna(latest.get("close_ma5")) else 0
    )
    ma10 = (
        float(latest.get("close_ma10", 0))
        if not pd.isna(latest.get("close_ma10"))
        else 0
    )
    ma20 = (
        float(latest.get("close_ma20", 0))
        if not pd.isna(latest.get("close_ma20"))
        else 0
    )
    rsi = float(latest.get("rsi", 50)) if not pd.isna(latest.get("rsi")) else 50
    macd = float(latest.get("macd", 0)) if not pd.isna(latest.get("macd")) else 0
    signal = float(latest.get("signal", 0)) if not pd.isna(latest.get("signal")) else 0
    kdj_k = float(latest.get("kdj_k", 50)) if not pd.isna(latest.get("kdj_k")) else 50
    kdj_d = float(latest.get("kdj_d", 50)) if not pd.isna(latest.get("kdj_d")) else 50
    vol_ma5 = (
        float(latest.get("vol_ma5", 0)) if not pd.isna(latest.get("vol_ma5")) else 0
    )
    current_vol = float(latest.get("vol", 0))
    atr = float(latest.get("atr", 0)) if not pd.isna(latest.get("atr")) else 0

    trend_score = 0
    if ma5 > ma10 > ma20:
        trend_score = 30
    elif ma5 > ma10:
        trend_score = 20
    elif ma5 > ma20:
        trend_score = 10
    details["trend"] = trend_score

    momentum_score = 0
    if rsi > 40 and rsi < 70:
        momentum_score = 20
    elif rsi >= 70:
        momentum_score = 10
    elif rsi <= 30:
        momentum_score = 5
    details["momentum"] = momentum_score

    kdj_score = 0
    if kdj_k > kdj_d and kdj_k < 80:
        kdj_score = 15
    elif kdj_k > 80:
        kdj_score = 5
    elif kdj_k < kdj_d and kdj_k > 20:
        kdj_score = 10
    details["kdj"] = kdj_score

    macd_score = 0
    if macd > signal > 0:
        macd_score = 15
    elif macd > signal:
        macd_score = 10
    elif macd < signal < 0:
        macd_score = 5
    details["macd"] = macd_score

    vol_score = 0
    if current_vol > vol_ma5 * 1.5:
        vol_score = 10
    elif current_vol > vol_ma5:
        vol_score = 5
    details["volume"] = vol_score

    score = trend_score + momentum_score + kdj_score + macd_score + vol_score
    details["total"] = score

    return score, details


def calculate_price_levels(df, latest):
    """计算关键价位"""
    current_price = float(latest.get("close", 0))
    ma5 = (
        float(latest.get("close_ma5", 0)) if not pd.isna(latest.get("close_ma5")) else 0
    )
    ma20 = (
        float(latest.get("close_ma20", 0))
        if not pd.isna(latest.get("close_ma20"))
        else 0
    )
    bb_upper = (
        float(latest.get("bb_upper", 0)) if not pd.isna(latest.get("bb_upper")) else 0
    )
    bb_lower = (
        float(latest.get("bb_lower", 0)) if not pd.isna(latest.get("bb_lower")) else 0
    )
    bb_middle = (
        float(latest.get("bb_middle", 0)) if not pd.isna(latest.get("bb_middle")) else 0
    )
    atr = float(latest.get("atr", 0)) if not pd.isna(latest.get("atr")) else 0

    levels = {
        "current": current_price,
        "resistance_1": round(ma5, 2) if ma5 > current_price else None,
        "resistance_2": round(bb_upper, 2) if bb_upper > current_price else None,
        "support_1": round(ma5, 2) if ma5 < current_price else None,
        "support_2": round(bb_lower, 2) if bb_lower < current_price else None,
        "stop_loss": round(current_price - atr * 1.5, 2) if atr > 0 else None,
        "boll_upper": round(bb_upper, 2),
        "boll_middle": round(bb_middle, 2),
        "boll_lower": round(bb_lower, 2),
    }

    return levels


def detect_signals(df, latest, prev):
    """检测买卖信号"""
    signals = []

    current_price = float(latest.get("close", 0))
    prev_price = float(prev.get("close", 0))
    ma5 = (
        float(latest.get("close_ma5", 0)) if not pd.isna(latest.get("close_ma5")) else 0
    )
    prev_ma5 = (
        float(prev.get("close_ma5", 0)) if not pd.isna(prev.get("close_ma5")) else 0
    )
    ma10 = (
        float(latest.get("close_ma10", 0))
        if not pd.isna(latest.get("close_ma10"))
        else 0
    )
    prev_ma10 = (
        float(prev.get("close_ma10", 0)) if not pd.isna(prev.get("close_ma10")) else 0
    )
    rsi = float(latest.get("rsi", 50)) if not pd.isna(latest.get("rsi")) else 50
    macd = float(latest.get("macd", 0)) if not pd.isna(latest.get("macd")) else 0
    prev_macd = float(prev.get("macd", 0)) if not pd.isna(prev.get("macd")) else 0
    signal = float(latest.get("signal", 0)) if not pd.isna(latest.get("signal")) else 0
    prev_signal = float(prev.get("signal", 0)) if not pd.isna(prev.get("signal")) else 0
    kdj_k = float(latest.get("kdj_k", 50)) if not pd.isna(latest.get("kdj_k")) else 50
    prev_kdj_k = float(prev.get("kdj_k", 50)) if not pd.isna(prev.get("kdj_k")) else 50
    kdj_d = float(latest.get("kdj_d", 50)) if not pd.isna(latest.get("kdj_d")) else 50
    prev_kdj_d = float(prev.get("kdj_d", 50)) if not pd.isna(prev.get("kdj_d")) else 50

    if ma5 > ma10 and prev_ma5 <= prev_ma10:
        signals.append(
            {
                "type": "golden_cross",
                "name": "MA5上穿MA10",
                "action": "buy",
                "desc": "短期趋势转强",
            }
        )

    if ma5 < ma10 and prev_ma5 >= prev_ma10:
        signals.append(
            {
                "type": "dead_cross",
                "name": "MA5下穿MA10",
                "action": "sell",
                "desc": "短期趋势转弱",
            }
        )

    if macd > signal and prev_macd <= prev_signal and macd > 0:
        signals.append(
            {
                "type": "macd_golden",
                "name": "MACD金叉",
                "action": "buy",
                "desc": "动能转多",
            }
        )

    if macd < signal and prev_macd >= prev_signal and macd < 0:
        signals.append(
            {
                "type": "macd_dead",
                "name": "MACD死叉",
                "action": "sell",
                "desc": "动能转空",
            }
        )

    if kdj_k > kdj_d and prev_kdj_k <= prev_kdj_d and kdj_k < 80:
        signals.append(
            {
                "type": "kdj_golden",
                "name": "KDJ金叉",
                "action": "buy",
                "desc": "短线买入信号",
            }
        )

    if kdj_k < kdj_d and prev_kdj_k >= prev_kdj_d and kdj_k > 20:
        signals.append(
            {
                "type": "kdj_dead",
                "name": "KDJ死叉",
                "action": "sell",
                "desc": "短线卖出信号",
            }
        )

    if rsi < 30:
        signals.append(
            {
                "type": "oversold",
                "name": "RSI超卖",
                "action": "watch_buy",
                "desc": "注意反弹机会",
            }
        )
    elif rsi > 70:
        signals.append(
            {
                "type": "overbought",
                "name": "RSI超买",
                "action": "watch_sell",
                "desc": "注意回调风险",
            }
        )

    if current_price > ma5 and prev_price <= ma5:
        signals.append(
            {
                "type": "price_break_ma5",
                "name": "价格突破MA5",
                "action": "buy",
                "desc": "短期强势",
            }
        )

    return signals


def detect_unusual_activity(df, latest, prev):
    """检测异动"""
    activities = []

    current_vol = float(latest.get("vol", 0))
    prev_vol = float(prev.get("vol", 0))
    vol_ma5 = (
        float(latest.get("vol_ma5", 0)) if not pd.isna(latest.get("vol_ma5")) else 0
    )
    vol_ma20 = (
        float(latest.get("vol_ma20", 0)) if not pd.isna(latest.get("vol_ma20")) else 0
    )

    current_price = float(latest.get("close", 0))
    prev_price = float(prev.get("close", 0))
    ma5 = (
        float(latest.get("close_ma5", 0)) if not pd.isna(latest.get("close_ma5")) else 0
    )

    if current_vol > vol_ma5 * 2:
        activities.append(
            {
                "type": "volume_surge",
                "level": "strong",
                "desc": f"成交量放大 {current_vol / vol_ma5:.1f}倍",
                "icon": "📈",
            }
        )
    elif current_vol > vol_ma5 * 1.5:
        activities.append(
            {
                "type": "volume_increase",
                "level": "medium",
                "desc": f"成交量较前日放大",
                "icon": "📊",
            }
        )

    if current_vol < vol_ma20 * 0.3 and vol_ma20 > 0:
        activities.append(
            {
                "type": "volume_shrink",
                "level": "low",
                "desc": "成交量大幅萎缩",
                "icon": "📉",
            }
        )

    price_change = (
        ((current_price - prev_price) / prev_price * 100) if prev_price > 0 else 0
    )
    if abs(price_change) > 5:
        activities.append(
            {
                "type": "price_surge",
                "level": "strong",
                "desc": f"价格波动 {price_change:+.2f}%",
                "icon": "🔥",
            }
        )
    elif abs(price_change) > 3:
        activities.append(
            {
                "type": "price_change",
                "level": "medium",
                "desc": f"价格变动 {price_change:+.2f}%",
                "icon": "⚡",
            }
        )

    if ma5 > 0 and current_price > ma5 * 1.1:
        activities.append(
            {
                "type": "breakout",
                "level": "strong",
                "desc": "价格突破MA5 10%以上",
                "icon": "🚀",
            }
        )
    elif ma5 > 0 and current_price < ma5 * 0.9:
        activities.append(
            {
                "type": "breakdown",
                "level": "strong",
                "desc": "价格跌破MA5 10%以上",
                "icon": "💥",
            }
        )

    return activities


@api_bp.route("/api/analyze")
@login_required
def analyze_stock():
    """分析股票"""
    ts_code = request.args.get("ts_code", "000001.SZ")

    try:
        from stock_fetcher import StockFetcher
        from technical_indicators import TechnicalIndicators
        from advanced_indicators import AdvancedIndicators

        token = os.getenv("TUSHARE_TOKEN")
        if not token:
            return jsonify({"error": "未配置 TuShare token"}), 500

        fetcher = StockFetcher(token)
        df = fetcher.get_daily(ts_code)

        if df is None or df.empty:
            return jsonify({"error": "获取数据失败"}), 400

        ti = TechnicalIndicators()
        ai = AdvancedIndicators()

        df = df.sort_values("trade_date", ascending=True).reset_index(drop=True)

        df = ti.calculate_ma(df, window=5)
        df = ti.calculate_ma(df, window=10)
        df = ti.calculate_ma(df, window=20)
        df = ti.calculate_ma(df, window=60)

        df = ti.calculate_macd(df)
        df = ti.calculate_rsi(df)
        df = ti.calculate_kdj(df)
        df = ti.calculate_bollinger_bands(df)
        df = ti.calculate_atr(df)

        df = ti.calculate_vol_ma(df, window=5)
        df = ti.calculate_vol_ma(df, window=10)
        df = ti.calculate_vol_ma(df, window=20)

        df = ai.calculate_all_advanced_indicators(df)

        df_desc = df.sort_values("trade_date", ascending=False).reset_index(drop=True)
        latest = df_desc.iloc[0]
        prev = df_desc.iloc[1] if len(df_desc) > 1 else latest

        current_price = float(latest.get("close", 0))
        prev_close = float(prev.get("close", current_price))
        change_percent = (
            ((current_price - prev_close) / prev_close * 100) if prev_close else 0
        )

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

        score, score_details = calculate_comprehensive_score(df_desc, latest, prev)
        price_levels = calculate_price_levels(df_desc, latest)
        signals = detect_signals(df_desc, latest, prev)
        activities = detect_unusual_activity(df_desc, latest, prev)

        result = {
            "ts_code": ts_code,
            "current_price": current_price,
            "change_percent": round(change_percent, 2),
            "score": score,
            "score_details": score_details,
            "price_levels": price_levels,
            "signals": signals,
            "activities": activities,
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

                score, _ = calculate_comprehensive_score(df, latest, prev)

                results.append(
                    {
                        "ts_code": ts_code,
                        "current_price": current_price,
                        "change_percent": round(change_percent, 2),
                        "score": score,
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
