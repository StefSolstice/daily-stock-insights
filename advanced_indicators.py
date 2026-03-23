#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级技术指标计算模块 - 选股核心指标
包含换手率、资金流向、涨跌幅等关键选股维度
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, List
from datetime import datetime, timedelta


class AdvancedIndicators:
    """高级技术指标计算器"""
    
    def __init__(self):
        """初始化高级指标计算器"""
        pass
    
    def calculate_turnover_rate_rank(self, df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        """计算换手率排名（反映筹码活跃度）
        
        Args:
            df: 包含换手率数据的 DataFrame
            window: 计算窗口
            
        Returns:
            添加了换手率排名的 DataFrame
        """
        df = df.copy()
        
        # 计算换手率在窗口期内的排名百分位
        df['turnover_rate_rank'] = df['turnover_rate'].rolling(window=window).apply(
            lambda x: pd.Series(x).rank(pct=True).iloc[-1] if len(x) >= window else np.nan
        )
        
        return df
    
    def calculate_price_changes(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算多个时间维度的涨跌幅
        
        Args:
            df: 包含价格数据的 DataFrame
            
        Returns:
            添加了多维度涨跌幅的 DataFrame
        """
        df = df.copy()
        
        # 当日涨跌幅（已存在 pct_change）
        # 近5日涨跌幅
        df['pct_change_5d'] = ((df['close'] / df['close'].shift(5)) - 1) * 100
        # 近20日涨跌幅
        df['pct_change_20d'] = ((df['close'] / df['close'].shift(20)) - 1) * 100
        # 近60日涨跌幅
        df['pct_change_60d'] = ((df['close'] / df['close'].shift(60)) - 1) * 100
        
        return df
    
    def calculate_volume_price_relationship(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算量价关系指标
        
        Args:
            df: 包含价格和成交量数据的 DataFrame
            
        Returns:
            添加了量价关系指标的 DataFrame
        """
        df = df.copy()
        
        # 计算价格变化和成交量变化
        df['price_change_pct'] = df['close'].pct_change()
        df['volume_change_pct'] = df['vol'].pct_change()
        
        # 量价配合度：价格上涨且成交量放大
        df['volume_price_alignment'] = np.where(
            (df['price_change_pct'] > 0) & (df['volume_change_pct'] > 0),
            1,  # 价涨量增
            np.where(
                (df['price_change_pct'] > 0) & (df['volume_change_pct'] <= 0),
                0.5,  # 价涨量缩
                np.where(
                    (df['price_change_pct'] <= 0) & (df['volume_change_pct'] > 0),
                    -0.5,  # 价跌量增
                    -1  # 价跌量缩
                )
            )
        )
        
        # 放量比例（相对于均值）
        df['volume_amplification'] = df['vol'] / df['vol'].rolling(window=20).mean()
        
        return df
    
    def calculate_support_resistance(self, df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        """计算关键支撑位和压力位
        
        Args:
            df: 包含最高价、最低价数据的 DataFrame
            window: 计算窗口
            
        Returns:
            添加了支撑压力位的 DataFrame
        """
        df = df.copy()
        
        # 计算窗口期内的最高价（压力位）和最低价（支撑位）
        df['resistance'] = df['high'].rolling(window=window).max()
        df['support'] = df['low'].rolling(window=window).min()
        
        # 计算当前价格相对于支撑压力的位置
        df['price_position'] = (df['close'] - df['support']) / (df['resistance'] - df['support'])
        
        return df
    
    def calculate_money_flow(self, df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        """计算资金流向指标
        
        Args:
            df: 包含价格和成交量数据的 DataFrame
            window: 计算窗口
            
        Returns:
            添加了资金流向指标的 DataFrame
        """
        df = df.copy()
        
        # 计算典型价格（最高价+最低价+收盘价）/ 3
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        
        # 计算资金流量（价格变化 × 成交量）
        money_flow = typical_price * df['vol']
        
        # 计算资金流指数（MFI）- 类似RSI但包含成交量
        positive_flow = pd.Series(index=df.index, dtype=float)
        negative_flow = pd.Series(index=df.index, dtype=float)
        
        for i in range(1, len(df)):
            if typical_price.iloc[i] > typical_price.iloc[i-1]:
                positive_flow.iloc[i] = money_flow.iloc[i]
                negative_flow.iloc[i] = 0
            else:
                positive_flow.iloc[i] = 0
                negative_flow.iloc[i] = money_flow.iloc[i]
        
        df['positive_flow'] = positive_flow.rolling(window=window).sum()
        df['negative_flow'] = negative_flow.rolling(window=window).sum()
        
        # 避免除零错误
        df['mfi'] = 100 - (100 / (1 + (df['positive_flow'] / df['negative_flow']).replace([np.inf, -np.inf], np.nan)))
        
        # 计算主力资金净流入（简单版本：大额交易估算）
        price_range = df['high'] - df['low']
        mid_price = df['low'] + price_range / 2
        price_position = (df['close'] - df['low']) / price_range
        
        # 估算主力资金流向（基于价格位置和成交量）
        df['主力净流入'] = np.where(
            price_position > 0.6,  # 收盘价在上半部分，视为资金流入
            df['vol'] * (price_position - 0.5) * 2,
            np.where(
                price_position < 0.4,  # 收盘价在下半部分，视为资金流出
                -df['vol'] * (0.5 - price_position) * 2,
                0  # 中性
            )
        )
        
        return df
    
    def calculate_relative_strength(self, df: pd.DataFrame, benchmark_df: pd.DataFrame, 
                                    window: int = 20) -> pd.DataFrame:
        """计算相对强度（个股vs大盘）
        
        Args:
            df: 个股数据
            benchmark_df: 基准数据（如大盘指数）
            window: 计算窗口
            
        Returns:
            添加了相对强度指标的 DataFrame
        """
        df = df.copy()
        
        # 计算个股和基准的收益率
        df['stock_return'] = df['close'].pct_change()
        benchmark_df['benchmark_return'] = benchmark_df['close'].pct_change()
        
        # 计算相对强度
        df['relative_strength'] = df['stock_return'] - benchmark_df['benchmark_return']
        df['relative_strength_ma'] = df['relative_strength'].rolling(window=window).mean()
        
        return df
    
    def calculate_volatility_breakout(self, df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        """计算波动率突破指标
        
        Args:
            df: 包含价格数据的 DataFrame
            window: 计算窗口
            
        Returns:
            添加了波动率突破指标的 DataFrame
        """
        df = df.copy()
        
        # 计算波动率
        df['returns'] = df['close'].pct_change()
        df['volatility'] = df['returns'].rolling(window=window).std() * np.sqrt(252)  # 年化波动率
        
        # 计算ATR（平均真实波幅）作为波动率指标
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift(1))
        low_close = abs(df['low'] - df['close'].shift(1))
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr'] = true_range.rolling(window=window).mean()
        
        # 计算价格相对于波动率的位置
        df['volatility_position'] = (df['close'] - df['close'].rolling(window=window).mean()) / df['volatility']
        
        return df
    
    def calculate_all_advanced_indicators(self, df: pd.DataFrame, 
                                        benchmark_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """计算所有高级指标
        
        Args:
            df: 包含股票数据的 DataFrame
            benchmark_df: 基准数据（可选，用于相对强度分析）
            
        Returns:
            添加了所有高级指标的 DataFrame
        """
        df = self.calculate_turnover_rate_rank(df)
        df = self.calculate_price_changes(df)
        df = self.calculate_volume_price_relationship(df)
        df = self.calculate_support_resistance(df)
        df = self.calculate_money_flow(df)
        df = self.calculate_volatility_breakout(df)
        
        # 如果提供了基准数据，则计算相对强度
        if benchmark_df is not None:
            df = self.calculate_relative_strength(df, benchmark_df)
        
        return df
    
    def generate_stock_selection_signals(self, df: pd.DataFrame) -> Dict:
        """生成股票选择信号
        
        Args:
            df: 包含所有指标的 DataFrame
            
        Returns:
            股票选择信号字典
        """
        if df.empty:
            return {"signals": []}
        
        # 获取最新一行数据
        latest = df.iloc[-1]
        
        signals = []
        
        # 换手率信号（活跃度）
        if latest.get('turnover_rate', 0) > 3:  # 换手率大于3%表示活跃
            signals.append("高换手率 - 筹码活跃")
        elif latest.get('turnover_rate', 0) < 1:  # 换手率小于1%表示冷淡
            signals.append("低换手率 - 筹码稳定")
        
        # 量价配合信号
        if latest.get('volume_price_alignment', 0) == 1:
            signals.append("价涨量增 - 强势信号")
        elif latest.get('volume_price_alignment', 0) == -1:
            signals.append("价跌量增 - 弱势信号")
        
        # 资金流向信号
        if latest.get('主力净流入', 0) > 0:
            signals.append("主力资金净流入")
        elif latest.get('主力净流入', 0) < 0:
            signals.append("主力资金净流出")
        
        # MFI资金流指数信号
        mfi = latest.get('mfi', 50)
        if mfi > 80:
            signals.append("MFI超买")
        elif mfi < 20:
            signals.append("MFI超卖")
        
        # 价格位置信号（相对于支撑压力）
        pos = latest.get('price_position', 0.5)
        if pos > 0.8:
            signals.append("接近压力位")
        elif pos < 0.2:
            signals.append("接近支撑位")
        
        # 近期涨幅信号
        pct_5d = latest.get('pct_change_5d', 0)
        if pct_5d > 10:
            signals.append("近5日大涨")
        elif pct_5d < -10:
            signals.append("近5日大跌")
        
        return {
            "signals": signals,
            "turnover_rate": latest.get('turnover_rate', 0),
            "volume_price_alignment": latest.get('volume_price_alignment', 0),
            "主力净流入": latest.get('主力净流入', 0),
            "mfi": latest.get('mfi', 50),
            "price_position": latest.get('price_position', 0.5),
            "pct_change_5d": latest.get('pct_change_5d', 0),
            "pct_change_20d": latest.get('pct_change_20d', 0)
        }


if __name__ == "__main__":
    # 测试
    import pandas as pd
    
    # 创建测试数据
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    test_df = pd.DataFrame({
        'trade_date': dates,
        'close': [10 + i * 0.1 + np.random.normal(0, 0.5) for i in range(100)],
        'high': [10.5 + i * 0.1 + np.random.normal(0, 0.3) for i in range(100)],
        'low': [9.5 + i * 0.1 + np.random.normal(0, 0.3) for i in range(100)],
        'vol': [1000 + i * 10 + np.random.normal(0, 200) for i in range(100)],
        'turnover_rate': [1 + np.random.normal(0, 0.5) for _ in range(100)]
    })
    
    ai = AdvancedIndicators()
    result = ai.calculate_all_advanced_indicators(test_df)
    
    print("高级指标计算完成")
    print(f"数据形状: {result.shape}")
    print("列名:", list(result.columns))
    
    # 生成选股信号
    signals = ai.generate_stock_selection_signals(result)
    print("\n选股信号:")
    for signal in signals['signals']:
        print(f"  - {signal}")