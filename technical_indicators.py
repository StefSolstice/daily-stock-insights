#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术指标计算模块 - 类实现
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict


class TechnicalIndicators:
    """技术指标计算器"""
    
    def __init__(self):
        """初始化技术指标计算器"""
        pass
    
    def calculate_ma(self, df: pd.DataFrame, column: str = 'close', 
                     window: int = 5) -> pd.DataFrame:
        """计算移动平均线
        
        Args:
            df: 包含价格数据的 DataFrame
            column: 计算均线的列名
            window: 均线周期
            
        Returns:
            添加了均线列的 DataFrame
        """
        df = df.copy()
        df[f'{column}_ma{window}'] = df[column].rolling(window=window).mean()
        return df
    
    def calculate_macd(self, df: pd.DataFrame, fast: int = 12, 
                       slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """计算 MACD 指标
        
        Args:
            df: 包含收盘价数据的 DataFrame
            fast: 快线 EMA 周期
            slow: 慢线 EMA 周期
            signal: 信号线周期
            
        Returns:
            添加了 MACD 相关列的 DataFrame
        """
        df = df.copy()
        
        exp1 = df['close'].ewm(span=fast, adjust=False).mean()
        exp2 = df['close'].ewm(span=slow, adjust=False).mean()
        
        df['macd'] = exp1 - exp2
        df['signal'] = df['macd'].ewm(span=signal, adjust=False).mean()
        df['histogram'] = df['macd'] - df['signal']
        
        return df
    
    def calculate_rsi(self, df: pd.DataFrame, column: str = 'close', 
                      window: int = 14) -> pd.DataFrame:
        """计算 RSI 相对强弱指标
        
        Args:
            df: 包含价格数据的 DataFrame
            column: 计算 RSI 的列名
            window: RSI 周期
            
        Returns:
            添加了 RSI 列的 DataFrame
        """
        df = df.copy()
        
        delta = df[column].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        return df
    
    def calculate_bollinger_bands(self, df: pd.DataFrame, column: str = 'close',
                                   window: int = 20, std_dev: float = 2.0) -> pd.DataFrame:
        """计算布林带
        
        Args:
            df: 包含价格数据的 DataFrame
            column: 计算布林带的列名
            window: 移动平均周期
            std_dev: 标准差倍数
            
        Returns:
            添加了布林带相关列的 DataFrame
        """
        df = df.copy()
        
        df['bb_middle'] = df[column].rolling(window=window).mean()
        rolling_std = df[column].rolling(window=window).std()
        df['bb_upper'] = df['bb_middle'] + (std_dev * rolling_std)
        df['bb_lower'] = df['bb_middle'] - (std_dev * rolling_std)
        df['bb_bandwidth'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle'] * 100
        
        return df
    
    def calculate_kdj(self, df: pd.DataFrame, period: int = 9) -> pd.DataFrame:
        """计算 KDJ 随机指标
        
        Args:
            df: 包含最高价、最低价、收盘价的 DataFrame
            period: 计算周期
            
        Returns:
            添加了 KDJ 相关列的 DataFrame
        """
        df = df.copy()
        
        lowest_low = df['low'].rolling(window=period).min()
        highest_high = df['high'].rolling(window=period).max()
        
        rsv = (df['close'] - lowest_low) / (highest_high - lowest_low) * 100
        
        df['kdj_k'] = rsv.rolling(window=3).mean()
        df['kdj_d'] = df['kdj_k'].rolling(window=3).mean()
        df['kdj_j'] = 3 * df['kdj_k'] - 2 * df['kdj_d']
        
        return df
    
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """计算 ATR 平均真实波幅
        
        Args:
            df: 包含最高价、最低价、收盘价的 DataFrame
            period: 计算周期
            
        Returns:
            添加了 ATR 列的 DataFrame
        """
        df = df.copy()
        
        high_low = df['high'] - df['low']
        high_close = (df['high'] - df['close'].shift(1)).abs()
        low_close = (df['low'] - df['close'].shift(1)).abs()
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr'] = true_range.rolling(window=period).mean()
        
        return df
    
    def calculate_obv(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算 OBV 能量潮
        
        Args:
            df: 包含收盘价和成交量的 DataFrame
            
        Returns:
            添加了 OBV 列的 DataFrame
        """
        df = df.copy()
        
        direction = np.sign(df['close'] - df['close'].shift(1))
        df['obv'] = (direction * df['vol']).cumsum()
        
        return df
    
    def add_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """添加所有技术指标
        
        Args:
            df: 包含价格数据的 DataFrame
            
        Returns:
            添加了所有技术指标的 DataFrame
        """
        df = self.calculate_ma(df, window=5)
        df = self.calculate_ma(df, window=10)
        df = self.calculate_ma(df, window=20)
        df = self.calculate_macd(df)
        df = self.calculate_rsi(df)
        df = self.calculate_bollinger_bands(df)
        df = self.calculate_kdj(df)
        df = self.calculate_atr(df)
        df = self.calculate_obv(df)
        
        return df


if __name__ == "__main__":
    # 测试
    import pandas as pd
    
    test_df = pd.DataFrame({
        'close': [10.0, 10.5, 11.0, 10.8, 11.2, 11.5, 11.3, 11.8, 12.0, 12.2],
        'high': [10.2, 10.7, 11.3, 11.0, 11.5, 11.8, 11.6, 12.0, 12.3, 12.5],
        'low': [9.8, 10.3, 10.8, 10.5, 11.0, 11.3, 11.1, 11.6, 11.8, 12.0],
        'vol': [1000, 1200, 1100, 1300, 1400, 1500, 1350, 1600, 1700, 1800]
    })
    
    ti = TechnicalIndicators()
    result = ti.add_all_indicators(test_df)
    print(result)
