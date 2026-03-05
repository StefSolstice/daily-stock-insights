#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据分析模块
"""

from typing import List, Dict, Optional
from datetime import datetime


class StockAnalyzer:
    """股票数据分析器"""
    
    def __init__(self, data: List[Dict]):
        """初始化
        
        Args:
            data: 股票数据列表
        """
        self.data = sorted(data, key=lambda x: x.get('trade_date', ''), reverse=True)
    
    def get_latest(self) -> Optional[Dict]:
        """获取最新一条数据"""
        return self.data[0] if self.data else None
    
    def get_price_change(self, days: int = 5) -> Dict:
        """计算价格变化
        
        Args:
            days: 计算天数
        
        Returns:
            价格变化信息
        """
        if len(self.data) < 2:
            return {"change": 0, "pct_change": 0}
        
        latest = self.data[0]
        old = self.data[min(days, len(self.data) - 1)]
        
        change = float(latest.get('close', 0)) - float(old.get('close', 0))
        pct_change = float(latest.get('pct_change', 0))
        
        return {
            "change": round(change, 2),
            "pct_change": round(pct_change, 2),
            "from_date": old.get('trade_date'),
            "to_date": latest.get('trade_date')
        }
    
    def calculate_ma(self, days: int = 5) -> float:
        """计算移动平均价
        
        Args:
            days: 均线周期
        
        Returns:
            移动平均价
        """
        if not self.data:
            return 0
        
        recent = self.data[:days]
        total = sum(float(d.get('close', 0)) for d in recent)
        return round(total / len(recent), 2)
    
    def calculate_volatility(self, days: int = 10) -> float:
        """计算波动率
        
        Args:
            days: 计算天数
        
        Returns:
            波动率
        """
        if len(self.data) < 2:
            return 0
        
        prices = [float(d.get('close', 0)) for d in self.data[:days]]
        if len(prices) < 2:
            return 0
        
        mean = sum(prices) / len(prices)
        variance = sum((p - mean) ** 2 for p in prices) / len(prices)
        volatility = (variance ** 0.5) / mean * 100
        
        return round(volatility, 2)
    
    def get_volume_analysis(self, days: int = 5) -> Dict:
        """成交量分析
        
        Args:
            days: 分析天数
        
        Returns:
            成交量分析结果
        """
        if not self.data:
            return {"avg_volume": 0, "trend": "neutral"}
        
        recent = self.data[:days]
        avg_volume = sum(float(d.get('vol', 0)) for d in recent) / len(recent)
        
        # 判断趋势
        if len(recent) >= 2:
            first_vol = float(recent[-1].get('vol', 0))
            last_vol = float(recent[0].get('vol', 0))
            if last_vol > first_vol * 1.2:
                trend = "increasing"
            elif last_vol < first_vol * 0.8:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "neutral"
        
        return {
            "avg_volume": round(avg_volume, 2),
            "trend": trend,
            "days": days
        }
    
    def generate_summary(self) -> str:
        """生成分析摘要
        
        Returns:
            分析摘要文本
        """
        if not self.data:
            return "暂无数据"
        
        latest = self.data[0]
        change_info = self.get_price_change(5)
        ma5 = self.calculate_ma(5)
        ma10 = self.calculate_ma(10)
        volatility = self.calculate_volatility(10)
        volume_info = self.get_volume_analysis(5)
        
        summary = f"""
📊 股票分析报告 - {latest.get('ts_code')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 行情数据 (更新日期: {latest.get('trade_date')})
   收盘价: {latest.get('close')}
   涨跌幅: {latest.get('pct_change')}%
   涨跌额: {latest.get('change')}

📉 近期表现 (近5日)
   涨跌幅: {change_info['pct_change']}%

📊 技术指标
   MA(5):  {ma5}
   MA(10): {ma10}
   波动率: {volatility}%

🔊 成交量分析
   平均成交量: {volume_info['avg_volume']}
   趋势: {volume_info['trend']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return summary


def calculate_support_resistance(data: List[Dict], days: int = 20) -> Dict:
    """计算支撑位和阻力位
    
    Args:
        data: 股票数据
        days: 计算天数
    
    Returns:
        支撑位和阻力位
    """
    if not data:
        return {"support": 0, "resistance": 0}
    
    recent = data[:days]
    highs = [float(d.get('high', 0)) for d in recent]
    lows = [float(d.get('low', 0)) for d in recent]
    
    return {
        "support": round(min(lows), 2),
        "resistance": round(max(highs), 2)
    }


def detect_patterns(data: List[Dict]) -> List[str]:
    """识别常见技术形态
    
    Args:
        data: 股票数据
    
    Returns:
        识别出的形态列表
    """
    patterns = []
    
    if len(data) < 5:
        return patterns
    
    # 检查是否形成连续上涨/下跌
    consecutive = 0
    for i in range(len(data) - 1):
        if float(data[i].get('close', 0)) > float(data[i+1].get('close', 0)):
            consecutive += 1
        else:
            break
    
    if consecutive >= 4:
        patterns.append("连续上涨形态")
    elif consecutive <= -4:
        patterns.append("连续下跌形态")
    
    # 检查是否突破新高/新低
    if data:
        latest = data[0]
        prices = [float(d.get('close', 0)) for d in data]
        
        if float(latest.get('close', 0)) == max(prices):
            patterns.append("突破新高")
        elif float(latest.get('close', 0)) == min(prices):
            patterns.append("创出新低")
    
    return patterns


if __name__ == "__main__":
    # 测试
    test_data = [
        {"trade_date": "20260227", "close": 10.90, "high": 10.92, "low": 10.84, "vol": 612227.96, "pct_change": 0.28},
        {"trade_date": "20260226", "close": 10.87, "high": 10.91, "low": 10.80, "vol": 712730.19, "pct_change": 0.09},
        {"trade_date": "20260225", "close": 10.86, "high": 10.95, "low": 10.78, "vol": 1063134.87, "pct_change": -0.46},
    ]
    
    analyzer = StockAnalyzer(test_data)
    print(analyzer.generate_summary())