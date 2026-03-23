#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
选股策略模块
实现多种选股策略，包括技术面、基本面和资金面的综合分析
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from stock_fetcher import StockFetcher
from technical_indicators import TechnicalIndicators
from advanced_indicators import AdvancedIndicators
from fundamental_analyzer import FundamentalAnalyzer


class StockSelectionStrategy:
    """股票选股策略类"""
    
    def __init__(self, token: str = None):
        """初始化选股策略
        
        Args:
            token: TuShare API Token
        """
        self.fetcher = StockFetcher(token)
        self.ti = TechnicalIndicators()
        self.ai = AdvancedIndicators()
        self.fundamental = None  # 会在具体分析中初始化
    
    def get_a_share_list(self) -> List[Dict]:
        """获取A股股票列表
        
        Returns:
            A股股票列表
        """
        try:
            # 获取所有A股列表
            df = self.fetcher.pro.stock_basic(
                exchange='', 
                list_status='L',  # 上市状态
                fields='ts_code,symbol,name,area,industry,market,list_date'
            )
            return df.to_dict('records')
        except Exception as e:
            print(f"获取A股列表失败: {e}")
            return []
    
    def screen_by_technical_conditions(self, df: pd.DataFrame) -> Dict:
        """根据技术条件筛选股票
        
        Args:
            df: 包含所有指标的DataFrame
            
        Returns:
            筛选结果
        """
        if df.empty:
            return {"valid": False, "conditions_met": [], "conditions_failed": []}
        
        # 获取最新数据
        latest = df.iloc[0]  # 注意：数据已经是降序排列，所以第一行是最新数据
        
        conditions = {
            # MA5上穿MA10的条件
            "ma5_cross_ma10": (
                latest.get('close_ma5', 0) > latest.get('close_ma10', 0) and 
                df.iloc[1]['close_ma5'] <= df.iloc[1]['close_ma10']  # 前一日MA5 <= MA10
            ),
            # 成交量放大条件
            "volume_amplified": (
                latest.get('vol', 0) > latest.get('vol_ma5', 0) * 1.5  # 当日成交量 > 5日均量1.5倍
            ),
            # RSI条件（非超买超卖）
            "rsi_normal": (
                30 < latest.get('rsi', 50) < 70
            ),
            # MACD金叉条件
            "macd_golden_cross": (
                latest.get('macd', 0) > latest.get('signal', 0) and 
                df.iloc[1]['macd'] <= df.iloc[1]['signal']  # 前一日MACD <= Signal
            ),
            # 股价在布林带中轨上方
            "price_above_bb_middle": (
                latest.get('close', 0) > latest.get('bb_middle', 0)
            ),
            # 换手率适中（不过低也不过高）
            "turnover_rate_normal": (
                1 < latest.get('turnover_rate', 0) < 10
            ),
            # 近期涨幅适中（避免过度投机）
            "recent_performance_normal": (
                -10 < latest.get('pct_change_5d', 0) < 15  # 5日涨幅在-10%到15%之间
            )
        }
        
        conditions_met = [k for k, v in conditions.items() if v]
        conditions_failed = [k for k, v in conditions.items() if not v]
        
        return {
            "valid": len(conditions_met) >= 3,  # 至少满足3个条件
            "conditions_met": conditions_met,
            "conditions_failed": conditions_failed,
            "score": len(conditions_met)  # 条件满足数量作为分数
        }
    
    def screen_by_fundamental_conditions(self, ts_code: str) -> Dict:
        """根据基本面条件筛选股票
        
        Args:
            ts_code: 股票代码
            
        Returns:
            基本面筛选结果
        """
        try:
            self.fundamental = FundamentalAnalyzer(ts_code, self.fetcher.pro)
            
            # 获取估值指标
            valuation = self.fundamental.get_valuation_metrics()
            if not valuation or 'pe' not in valuation:
                return {"valid": False, "fundamental_score": 0, "reason": "无法获取基本面数据"}
            
            # 基本面条件
            pe = valuation.get('pe', -1)
            pb = valuation.get('pb', -1)
            dv_ratio = valuation.get('dv_ratio', -1)
            
            conditions = {
                "pe_valid": (0 < pe < 50),  # PE在合理区间
                "pb_valid": (0 < pb < 5),   # PB在合理区间
                "dividend_exists": (dv_ratio > 0)  # 有分红
            }
            
            conditions_met = sum([1 for v in conditions.values() if v])
            
            return {
                "valid": conditions_met >= 2,  # 至少满足2个基本面条件
                "fundamental_score": conditions_met,
                "pe": pe,
                "pb": pb,
                "dv_ratio": dv_ratio,
                "conditions_met": [k for k, v in conditions.items() if v]
            }
        except Exception as e:
            print(f"基本面分析失败: {e}")
            return {"valid": False, "fundamental_score": 0, "reason": str(e)}
    
    def screen_by_money_flow_conditions(self, df: pd.DataFrame) -> Dict:
        """根据资金流向条件筛选股票
        
        Args:
            df: 包含资金流向指标的DataFrame
            
        Returns:
            资金面筛选结果
        """
        if df.empty:
            return {"valid": False, "money_flow_score": 0}
        
        latest = df.iloc[0]
        
        # 资金流向条件
        conditions = {
            "主力资金净流入": (latest.get('主力净流入', 0) > 0),
            "MFI正常": (20 < latest.get('mfi', 50) < 80),  # 避开极端值
            "量价配合良好": (latest.get('volume_price_alignment', 0) in [1, 0.5])  # 价涨量增或价涨量缩（缩量上涨有时也健康）
        }
        
        conditions_met = sum([1 for v in conditions.values() if v])
        
        return {
            "valid": conditions_met >= 2,  # 至少满足2个资金面条件
            "money_flow_score": conditions_met,
            "conditions_met": [k for k, v in conditions.items() if v]
        }
    
    def analyze_single_stock(self, ts_code: str) -> Dict:
        """分析单个股票
        
        Args:
            ts_code: 股票代码
            
        Returns:
            分析结果
        """
        # 获取一年的数据以确保指标的稳定性
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
        
        # 获取日线数据
        df = self.fetcher.get_daily(ts_code, start_date, end_date)
        
        if df is None or df.empty:
            return {"valid": False, "error": f"无法获取{ts_code}的数据"}
        
        # 计算技术指标
        df = self.ti.add_all_indicators(df)
        
        # 计算高级指标
        df = self.ai.calculate_all_advanced_indicators(df)
        
        # 技术面分析
        tech_result = self.screen_by_technical_conditions(df)
        
        # 基本面分析
        fund_result = self.screen_by_fundamental_conditions(ts_code)
        
        # 资金面分析
        money_result = self.screen_by_money_flow_conditions(df)
        
        # 综合评分
        total_score = tech_result.get('score', 0) + fund_result.get('fundamental_score', 0) + money_result.get('money_flow_score', 0)
        
        return {
            "ts_code": ts_code,
            "tech_analysis": tech_result,
            "fundamental_analysis": fund_result,
            "money_flow_analysis": money_result,
            "total_score": total_score,
            "recommend": tech_result["valid"] and fund_result["valid"] and money_result["valid"],
            "data_points": len(df)
        }
    
    def scan_all_stocks(self, limit: int = 50) -> List[Dict]:
        """扫描所有A股进行选股
        
        Args:
            limit: 限制扫描的股票数量（避免API调用过多）
            
        Returns:
            符合条件的股票列表
        """
        print(f"开始扫描A股，限制数量: {limit}")
        
        # 获取A股列表
        stocks = self.get_a_share_list()
        
        if not stocks:
            print("无法获取A股列表")
            return []
        
        # 只扫描前limit只股票（避免API限制）
        stocks = stocks[:limit]
        
        selected_stocks = []
        
        for i, stock in enumerate(stocks):
            ts_code = stock['ts_code']
            name = stock['name']
            
            print(f"正在分析: {ts_code} {name} ({i+1}/{min(len(stocks), limit)})")
            
            try:
                result = self.analyze_single_stock(ts_code)
                
                if result.get("recommend"):
                    selected_stocks.append(result)
                    
                    # 输出简要信息
                    tech_score = result['tech_analysis'].get('score', 0)
                    fund_score = result['fundamental_analysis'].get('fundamental_score', 0)
                    money_score = result['money_flow_analysis'].get('money_flow_score', 0)
                    
                    print(f"  ✓ 推荐! 总分: {result['total_score']} "
                          f"(技:{tech_score} 基:{fund_score} 资:{money_score}) "
                          f"数据点: {result['data_points']}")
                
            except Exception as e:
                print(f"  ✗ 分析失败: {e}")
                continue
        
        # 按总分排序
        selected_stocks.sort(key=lambda x: x['total_score'], reverse=True)
        
        return selected_stocks
    
    def generate_selection_report(self, results: List[Dict]) -> str:
        """生成选股报告
        
        Args:
            results: 选股结果列表
            
        Returns:
            选股报告字符串
        """
        if not results:
            return "没有找到符合条件的股票"
        
        report = "🔍 股票筛选结果报告\n"
        report += "=" * 60 + "\n\n"
        
        for i, result in enumerate(results, 1):
            ts_code = result['ts_code']
            tech_analysis = result['tech_analysis']
            fund_analysis = result['fundamental_analysis']
            money_analysis = result['money_flow_analysis']
            
            report += f"{i}. {ts_code}\n"
            report += f"   总分: {result['total_score']} | 技术:{tech_analysis.get('score', 0)} "
            report += f"| 基本面:{fund_analysis.get('fundamental_score', 0)} | 资金:{money_analysis.get('money_flow_score', 0)}\n"
            report += f"   数据点: {result['data_points']}\n"
            
            # 技术面详情
            tech_met = tech_analysis.get('conditions_met', [])
            report += f"   技术面满足: {', '.join(tech_met) if tech_met else '无'}\n"
            
            # 基本面详情
            fund_data = result['fundamental_analysis']
            if fund_data.get('valid'):
                report += f"   基本面: PE={fund_data.get('pe', 'N/A'):.2f}, "
                report += f"PB={fund_data.get('pb', 'N/A'):.2f}, "
                report += f"股息率={fund_data.get('dv_ratio', 'N/A'):.2f}%\n"
            
            # 资金面详情
            money_met = money_analysis.get('conditions_met', [])
            report += f"   资金面满足: {', '.join(money_met) if money_met else '无'}\n"
            
            report += "\n"
        
        report += f"总计: {len(results)} 只符合条件的股票\n"
        
        return report


def main():
    """测试函数"""
    import os
    import argparse
    
    parser = argparse.ArgumentParser(description="股票选股策略测试")
    parser.add_argument("--token", help="TuShare Token，如果不提供则从环境变量读取")
    parser.add_argument("--code", help="单个股票代码测试，例如 000001.SZ")
    parser.add_argument("--scan", action="store_true", help="扫描全市场股票")
    parser.add_argument("--limit", type=int, default=10, help="扫描股票数量限制（默认10）")
    
    args = parser.parse_args()
    
    # 获取Token
    token = args.token or os.getenv('TUSHARE_TOKEN')
    if not token:
        print("错误: 请提供TuShare Token或设置TUSHARE_TOKEN环境变量")
        return
    
    # 创建选股策略实例
    selector = StockSelectionStrategy(token)
    
    if args.code:
        # 单个股票测试
        print(f"分析单个股票: {args.code}")
        result = selector.analyze_single_stock(args.code)
        
        if result.get("valid") is False and "error" in result:
            print(f"错误: {result['error']}")
            return
        
        print(f"股票: {result['ts_code']}")
        print(f"推荐: {'是' if result['recommend'] else '否'}")
        print(f"总分: {result['total_score']}")
        print(f"数据点: {result['data_points']}")
        
        # 显示技术面分析
        tech = result['tech_analysis']
        print(f"技术面得分: {tech.get('score', 0)}")
        print(f"满足条件: {', '.join(tech.get('conditions_met', []))}")
        
        # 显示基本面分析
        fund = result['fundamental_analysis']
        print(f"基本面得分: {fund.get('fundamental_score', 0)}")
        print(f"PE: {fund.get('pe', 'N/A')}, PB: {fund.get('pb', 'N/A')}, 股息率: {fund.get('dv_ratio', 'N/A')}")
        
        # 显示资金面分析
        money = result['money_flow_analysis']
        print(f"资金面得分: {money.get('money_flow_score', 0)}")
        print(f"资金面条件: {', '.join(money.get('conditions_met', []))}")
    
    elif args.scan:
        # 全市场扫描
        print(f"开始扫描A股，限制数量: {args.limit}")
        results = selector.scan_all_stocks(limit=args.limit)
        
        # 生成报告
        report = selector.generate_selection_report(results)
        print(report)
    
    else:
        # 默认测试
        test_code = "000001.SZ"  # 平安银行
        print(f"测试股票: {test_code}")
        result = selector.analyze_single_stock(test_code)
        
        if result.get("valid") is False and "error" in result:
            print(f"错误: {result['error']}")
            return
        
        print(f"推荐: {'是' if result['recommend'] else '否'}")
        print(f"总分: {result['total_score']}")
        print(f"技术面: {result['tech_analysis'].get('conditions_met', [])}")
        print(f"基本面: {result['fundamental_analysis'].get('conditions_met', [])}")
        print(f"资金面: {result['money_flow_analysis'].get('conditions_met', [])}")


if __name__ == "__main__":
    main()