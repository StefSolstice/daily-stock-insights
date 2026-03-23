from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required
import os
import sys

selection_bp = Blueprint("selection", __name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT_DIR = os.path.dirname(PROJECT_ROOT)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)


@selection_bp.route("/selection")
@login_required
def selection_page():
    return render_template("selection.html")


@selection_bp.route("/api/selection/scan", methods=["POST"])
@login_required
def scan_stocks():
    data = request.get_json() or {}
    limit = min(data.get("limit", 30), 50)

    try:
        from stock_selection import StockSelectionStrategy

        token = os.getenv("TUSHARE_TOKEN")
        if not token:
            return jsonify({"error": "未配置 TuShare token"}), 500

        selector = StockSelectionStrategy(token)
        results = selector.scan_all_stocks(limit=limit)

        formatted_results = []
        for r in results:
            tech = r.get("tech_analysis", {})
            fund = r.get("fundamental_analysis", {})
            money = r.get("money_flow_analysis", {})

            formatted_results.append(
                {
                    "ts_code": r.get("ts_code"),
                    "total_score": r.get("total_score", 0),
                    "tech_score": tech.get("score", 0),
                    "tech_conditions": tech.get("conditions_met", []),
                    "fund_score": fund.get("fundamental_score", 0),
                    "fund_pe": fund.get("pe"),
                    "fund_pb": fund.get("pb"),
                    "money_score": money.get("money_flow_score", 0),
                    "money_conditions": money.get("conditions_met", []),
                    "data_points": r.get("data_points", 0),
                }
            )

        return jsonify({"count": len(formatted_results), "results": formatted_results})

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@selection_bp.route("/api/selection/analyze", methods=["POST"])
@login_required
def analyze_single():
    data = request.get_json() or {}
    ts_code = data.get("ts_code")

    if not ts_code:
        return jsonify({"error": "股票代码不能为空"}), 400

    try:
        from stock_selection import StockSelectionStrategy

        token = os.getenv("TUSHARE_TOKEN")
        if not token:
            return jsonify({"error": "未配置 TuShare token"}), 500

        selector = StockSelectionStrategy(token)
        result = selector.analyze_single_stock(ts_code)

        tech = result.get("tech_analysis", {})
        fund = result.get("fundamental_analysis", {})
        money = result.get("money_flow_analysis", {})

        return jsonify(
            {
                "ts_code": result.get("ts_code"),
                "recommend": result.get("recommend", False),
                "total_score": result.get("total_score", 0),
                "tech_score": tech.get("score", 0),
                "tech_valid": tech.get("valid", False),
                "tech_conditions_met": tech.get("conditions_met", []),
                "tech_conditions_failed": tech.get("conditions_failed", []),
                "fund_score": fund.get("fundamental_score", 0),
                "fund_valid": fund.get("valid", False),
                "fund_pe": fund.get("pe"),
                "fund_pb": fund.get("pb"),
                "fund_dv_ratio": fund.get("dv_ratio"),
                "money_score": money.get("money_flow_score", 0),
                "money_valid": money.get("valid", False),
                "money_conditions_met": money.get("conditions_met", []),
                "data_points": result.get("data_points", 0),
            }
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
