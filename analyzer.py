#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据分析模块
"""

from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd
import numpy as np


class StockAnalyzer:
    """股票数据分析器"""
    
    def __init__(self, ts_code: str = None, pro = None, data: List[Dict] = None):
        """初始化
        
        Args:
            ts_code: 股票代码
            pro: TuShare pro API 实例
            data: 股票数据列表
        """
        self.ts_code = ts_code
        self.pro = pro
        self.data = sorted(data, key=lambda x: x.get('trade_date', ''), reverse=True) if data else []
    
    def calculate_ma(self, period: int = 5) -> float:
        """计算移动平均线
        
        Args:
            period: 周期
            
        Returns:
            MA 值
        """
        if len(self.data) < period:
            return 0.0
        
        prices = [float(d.get('close', 0)) for d in self.data[:period]]
        return sum(prices) / period
    
    def calculate_volatility(self, period: int = 10) -> float:
        """计算波动率
        
        Args:
            period: 周期
            
        Returns:
            波动率百分比
        """
        if len(self.data) < period:
            return 0.0
        
        changes = []
        for i in range(1, min(period, len(self.data))):
            prev_close = float(self.data[i-1].get('close', 0))
            curr_close = float(self.data[i].get('close', 0))
            if prev_close > 0:
                changes.append((curr_close - prev_close) / prev_close)
        
        if not changes:
            return 0.0
        
        mean = sum(changes) / len(changes)
        variance = sum((x - mean) ** 2 for x in changes) / len(changes)
        return (variance ** 0.5) * 100
    
    def get_price_change(self, days: int = 5) -> Dict:
        """获取价格变化
        
        Args:
            days: 天数
            
        Returns:
            价格变化信息
        """
        if len(self.data) < days:
            return {'change': 0, 'pct_change': 0}
        
        latest = float(self.data[0].get('close', 0))
        old = float(self.data[days-1].get('close', 0))
        
        if old == 0:
            return {'change': 0, 'pct_change': 0}
        
        return {
            'change': latest - old,
            'pct_change': ((latest - old) / old) * 100
        }
    
    def get_volume_analysis(self, days: int = 5) -> Dict:
        """获取成交量分析
        
        Args:
            days: 天数
            
        Returns:
            成交量分析信息
        """
        if len(self.data) < days:
            return {'avg_volume': 0, 'trend': 'unknown'}
        
        volumes = [float(d.get('vol', 0)) for d in self.data[:days]]
        avg_volume = sum(volumes) / len(volumes)
        latest_volume = volumes[0] if volumes else 0
        
        trend = 'unknown'
        if latest_volume > avg_volume * 1.2:
            trend = '放量'
        elif latest_volume < avg_volume * 0.8:
            trend = '缩量'
        else:
            trend = '平量'
        
        return {
            'avg_volume': avg_volume,
            'trend': trend
        }
    
    def calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算所有技术指标
        
        Args:
            df: 股票数据 DataFrame，包含 close, high, low, vol 等列
        
        Returns:
            添加了技术指标的 DataFrame
        """
        df = df.copy()
        
        # 确保数据按日期排序（升序）
        df = df.sort_values('trade_date').reset_index(drop=True)
        
        # 计算均线
        df['close_ma5'] = df['close'].rolling(window=5).mean()
        df['close_ma10'] = df['close'].rolling(window=10).mean()
        df['close_ma20'] = df['close'].rolling(window=20).mean()
        
        # 计算 MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd_diff'] = exp1 - exp2
        df['macd_signal'] = df['macd_diff'].ewm(span=9, adjust=False).mean()
        df['macd'] = df['macd_diff'] - df['macd_signal']
        
        # 计算 RSI
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # 计算 KDJ
        low_min = df['low'].rolling(window=9).min()
        high_max = df['high'].rolling(window=9).max()
        rsv = (df['close'] - low_min) / (high_max - low_min) * 100
        df['kdj_k'] = rsv.ewm(com=2, adjust=False).mean()
        df['kdj_d'] = df['kdj_k'].ewm(com=2, adjust=False).mean()
        df['kdj_j'] = 3 * df['kdj_k'] - 2 * df['kdj_d']
        
        # 计算 CCI
        tp = (df['high'] + df['low'] + df['close']) / 3
        ma_tp = tp.rolling(window=20).mean()
        mad_tp = tp.rolling(window=20).apply(lambda x: np.fabs(x - x.mean()).mean())
        df['cci'] = (tp - ma_tp) / (0.015 * mad_tp)
        
        # 计算 BOLL
        df['boll_mid'] = df['close'].rolling(window=20).mean()
        boll_std = df['close'].rolling(window=20).std()
        df['boll_upper'] = df['boll_mid'] + 2 * boll_std
        df['boll_lower'] = df['boll_mid'] - 2 * boll_std
        
        # 填充 NaN 值
        df = df.bfill().ffill().fillna(0)
        
        return df
    
    def generate_summary(self, df=None) -> str:
        """生成分析摘要
        
        Args:
            df: 包含技术指标的 DataFrame（可选）
        
        Returns:
            分析摘要文本
        """
        if df is not None and not df.empty:
            return self._generate_full_summary(df)
        
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

📈 行情数据 (更新日期：{latest.get('trade_date')})
   收盘价：{latest.get('close')}
   涨跌幅：{latest.get('pct_change')}%
   涨跌额：{latest.get('change')}

📉 近期表现 (近 5 日)
   涨跌幅：{change_info['pct_change']}%

📊 技术指标
   MA(5):  {ma5}
   MA(10): {ma10}
   波动率：{volatility}%

🔊 成交量分析
   平均成交量：{volume_info['avg_volume']}
   趋势：{volume_info['trend']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return summary
    
    def _generate_full_summary(self, df) -> str:
        """生成完整技术指标摘要"""
        if df.empty:
            return "暂无数据"
        
        latest = df.iloc[-1]
        ts_code = latest.get('ts_code', 'Unknown')
        trade_date = latest.get('trade_date', 'Unknown')
        
        close = latest.get('close', 0)
        pct_change = latest.get('pct_change', 0)
        change = latest.get('change', 0)
        vol = latest.get('vol', 0)
        
        ma5 = latest.get('close_ma5', 0)
        ma10 = latest.get('close_ma10', 0)
        ma20 = latest.get('close_ma20', 0)
        
        macd = latest.get('macd', 0)
        macd_signal = latest.get('macd_signal', 0)
        macd_diff = latest.get('macd_diff', 0)
        
        rsi = latest.get('rsi', 0)
        kdj_k = latest.get('kdj_k', 0)
        kdj_d = latest.get('kdj_d', 0)
        kdj_j = latest.get('kdj_j', 0)
        
        cci = latest.get('cci', 0)
        boll_upper = latest.get('boll_upper', 0)
        boll_mid = latest.get('boll_mid', 0)
        boll_lower = latest.get('boll_lower', 0)
        
        signals = []
        if macd > 0:
            signals.append("MACD 金叉 (看涨)")
        elif macd < 0:
            signals.append("MACD 死叉 (看跌)")
        if rsi > 70:
            signals.append("RSI 超买 (>70)")
        elif rsi < 30:
            signals.append("RSI 超卖 (<30)")
        if kdj_k > kdj_d and kdj_j > kdj_k:
            signals.append("KDJ 金叉 (看涨)")
        elif kdj_k < kdj_d and kdj_j < kdj_k:
            signals.append("KDJ 死叉 (看跌)")
        if cci > 100:
            signals.append("CCI 超买 (>100)")
        elif cci < -100:
            signals.append("CCI 超卖 (<-100)")
        if close > boll_upper:
            signals.append("股价突破 BOLL 上轨")
        elif close < boll_lower:
            signals.append("股价跌破 BOLL 下轨")
        
        signals_str = "\n   " + "\n   ".join(signals) if signals else "   无明显信号"
        
        summary = f"""
📊 股票技术分析报告 - {ts_code}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 行情数据 (更新日期：{trade_date})
   收盘价：{close:.2f}
   涨跌幅：{pct_change:.2f}%
   涨跌额：{change:.2f}
   成交量：{vol:,.0f}

📊 均线系统
   MA(5):  {ma5:.2f}
   MA(10): {ma10:.2f}
   MA(20): {ma20:.2f}

📈 MACD 指标
   DIFF: {macd_diff:.4f}
   DEA:  {macd_signal:.4f}
   MACD: {macd:.4f}

📊 RSI 指标
   RSI(14): {rsi:.2f}

📈 KDJ 指标
   K: {kdj_k:.2f}
   D: {kdj_d:.2f}
   J: {kdj_j:.2f}

📊 CCI 指标
   CCI(20): {cci:.2f}

📉 BOLL 通道
   上轨：{boll_upper:.2f}
   中轨：{boll_mid:.2f}
   下轨：{boll_lower:.2f}

🔔 技术信号：
{signals_str}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return summary
