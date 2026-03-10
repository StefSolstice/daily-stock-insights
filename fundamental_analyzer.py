#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票基本面分析模块
提供 PE、PB、ROE、毛利率等基本面指标分析
"""

import tushare as ts
from typing import Dict, Optional, List
from datetime import datetime


class FundamentalAnalyzer:
    """基本面分析器"""
    
    def __init__(self, ts_code: str, pro: Optional[ts.pro_api] = None):
        """初始化
        
        Args:
            ts_code: 股票代码
            pro: tushare pro API 实例
        """
        self.ts_code = ts_code
        self.pro = pro
        self.basic_info = None
        self.financial_data = None
    
    def get_basic_info(self) -> Dict:
        """获取股票基本信息
        
        Returns:
            基本信息字典
        """
        if self.basic_info:
            return self.basic_info
        
        if self.pro:
            df = self.pro.stock_basic(
                exchange='',
                list_status='L',
                fields='ts_code,symbol,name,area,industry,market,list_date'
            )
            stock = df[df['ts_code'] == self.ts_code]
            if not stock.empty:
                self.basic_info = stock.iloc[0].to_dict()
        
        return self.basic_info or {}
    
    def get_valuation_metrics(self, trade_date: Optional[str] = None) -> Dict:
        """获取估值指标
        
        Args:
            trade_date: 交易日期，默认最新
        
        Returns:
            估值指标字典
        """
        if not self.pro:
            return {"error": "需要配置 tushare pro API"}
        
        # 获取每日指标
        df = self.pro.daily_basic(
            ts_code=self.ts_code,
            trade_date=trade_date,
            fields='ts_code,trade_date,pe,pe_ttm,pb,ps,ps_ttm,dv_ratio,total_mv,circ_mv'
        )
        
        if df.empty:
            return {}
        
        data = df.iloc[0].to_dict()
        
        return {
            "ts_code": data.get('ts_code'),
            "trade_date": data.get('trade_date'),
            "pe": data.get('pe'),  # 市盈率
            "pe_ttm": data.get('pe_ttm'),  # 市盈率 TTM
            "pb": data.get('pb'),  # 市净率
            "ps": data.get('ps'),  # 市销率
            "ps_ttm": data.get('ps_ttm'),  # 市销率 TTM
            "dv_ratio": data.get('dv_ratio'),  # 股息率
            "total_mv": data.get('total_mv'),  # 总市值
            "circ_mv": data.get('circ_mv'),  # 流通市值
        }
    
    def get_profitability_metrics(self) -> Dict:
        """获取盈利能力指标
        
        Returns:
            盈利能力指标字典
        """
        if not self.pro:
            return {"error": "需要配置 tushare pro API"}
        
        # 获取财务指标
        df = self.pro.fina_indicator(
            ts_code=self.ts_code,
            fields='ts_code,ann_date,end_date,basic_eps,diluted_eps,roewa,roa,grossmargin,oper_profit'
        )
        
        if df.empty:
            return {}
        
        # 获取最新一期数据
        latest = df.iloc[0].to_dict()
        
        return {
            "ts_code": latest.get('ts_code'),
            "ann_date": latest.get('ann_date'),  # 公告日期
            "end_date": latest.get('end_date'),  # 报告期
            "basic_eps": latest.get('basic_eps'),  # 基本每股收益
            "diluted_eps": latest.get('diluted_eps'),  # 稀释每股收益
            "roe_wa": latest.get('roewa'),  # 加权净资产收益率
            "roa": latest.get('roa'),  # 总资产净利率
            "gross_margin": latest.get('grossmargin'),  # 毛利率
            "oper_profit": latest.get('oper_profit'),  # 营业利润
        }
    
    def get_growth_metrics(self) -> Dict:
        """获取成长能力指标
        
        Returns:
            成长能力指标字典
        """
        if not self.pro:
            return {"error": "需要配置 tushare pro API"}
        
        # 获取成长能力指标
        df = self.pro.fina_indicator(
            ts_code=self.ts_code,
            fields='ts_code,ann_date,end_date,yoy_sales,yoy_op,yoy_net_profit'
        )
        
        if df.empty:
            return {}
        
        latest = df.iloc[0].to_dict()
        
        return {
            "ts_code": latest.get('ts_code'),
            "ann_date": latest.get('ann_date'),
            "end_date": latest.get('end_date'),
            "yoy_sales": latest.get('yoy_sales'),  # 营收同比增长率
            "yoy_op": latest.get('yoy_op'),  # 营业利润同比增长率
            "yoy_net_profit": latest.get('yoy_net_profit'),  # 净利润同比增长率
        }
    
    def analyze_valuation_level(self, pe: float, pb: float, industry: str = '') -> Dict:
        """分析估值水平
        
        Args:
            pe: 市盈率
            pb: 市净率
            industry: 所属行业
        
        Returns:
            估值水平分析
        """
        result = {
            "pe_level": "unknown",
            "pb_level": "unknown",
            "overall": "unknown"
        }
        
        # PE 水平判断（简化版，实际应该对比行业和历史分位）
        if pe and pe > 0:
            if pe < 10:
                result["pe_level"] = "低估值"
            elif pe < 20:
                result["pe_level"] = "合理估值"
            elif pe < 40:
                result["pe_level"] = "中等偏高"
            else:
                result["pe_level"] = "高估值"
        
        # PB 水平判断
        if pb and pb > 0:
            if pb < 1.5:
                result["pb_level"] = "低估值"
            elif pb < 3:
                result["pb_level"] = "合理估值"
            elif pb < 5:
                result["pb_level"] = "中等偏高"
            else:
                result["pb_level"] = "高估值"
        
        # 综合判断
        pe_score = 0
        pb_score = 0
        
        if result["pe_level"] == "低估值":
            pe_score = 1
        elif result["pe_level"] == "合理估值":
            pe_score = 2
        elif result["pe_level"] == "中等偏高":
            pe_score = 3
        elif result["pe_level"] == "高估值":
            pe_score = 4
        
        if result["pb_level"] == "低估值":
            pb_score = 1
        elif result["pb_level"] == "合理估值":
            pb_score = 2
        elif result["pb_level"] == "中等偏高":
            pb_score = 3
        elif result["pb_level"] == "高估值":
            pb_score = 4
        
        avg_score = (pe_score + pb_score) / 2
        
        if avg_score <= 1.5:
            result["overall"] = "低估"
        elif avg_score <= 2.5:
            result["overall"] = "合理"
        elif avg_score <= 3.5:
            result["overall"] = "偏高"
        else:
            result["overall"] = "高估"
        
        return result
    
    def generate_fundamental_report(self) -> str:
        """生成基本面分析报告
        
        Returns:
            分析报告文本
        """
        basic = self.get_basic_info()
        valuation = self.get_valuation_metrics()
        profitability = self.get_profitability_metrics()
        growth = self.get_growth_metrics()
        
        if not valuation:
            return "❌ 无法获取基本面数据，请检查 tushare API 配置"
        
        report = f"""
📊 基本面分析报告 - {basic.get('name', self.ts_code)} ({self.ts_code})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏢 公司信息
   行业：{basic.get('industry', 'N/A')}
   地区：{basic.get('area', 'N/A')}
   上市日期：{basic.get('list_date', 'N/A')}

💰 估值指标 (日期：{valuation.get('trade_date', 'N/A')})
   市盈率 (PE): {valuation.get('pe', 'N/A')}
   市盈率 TTM: {valuation.get('pe_ttm', 'N/A')}
   市净率 (PB): {valuation.get('pb', 'N/A')}
   股息率：{valuation.get('dv_ratio', 'N/A')}%
   总市值：{valuation.get('total_mv', 'N/A')} 亿

📈 盈利能力 (报告期：{profitability.get('end_date', 'N/A')})
   每股收益：{profitability.get('basic_eps', 'N/A')}
   ROE: {profitability.get('roe_wa', 'N/A')}%
   毛利率：{profitability.get('gross_margin', 'N/A')}%

📉 成长能力
   营收增速：{growth.get('yoy_sales', 'N/A')}%
   利润增速：{growth.get('yoy_net_profit', 'N/A')}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 估值分析需要结合行业和历史数据，以上仅供参考
"""
        return report


if __name__ == "__main__":
    # 测试示例
    print("基本面分析模块 - 测试需要配置 tushare pro API")
    print("使用方式：")
    print("  analyzer = FundamentalAnalyzer('000001.SZ', pro)")
    print("  print(analyzer.generate_fundamental_report())")
