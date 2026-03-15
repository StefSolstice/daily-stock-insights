#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据可视化模块
提供 K 线图、技术指标图等可视化功能
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
import pandas as pd
import numpy as np
from typing import Optional, List, Tuple
from datetime import datetime
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class StockVisualizer:
    """股票可视化器"""
    
    def __init__(self, df: pd.DataFrame, ts_code: str = '', name: str = ''):
        """初始化
        
        Args:
            df: 股票数据 DataFrame，需包含 date, open, high, low, close, volume 列
            ts_code: 股票代码
            name: 股票名称
        """
        self.df = df.copy()
        self.ts_code = ts_code
        self.name = name
        self.fig_size = (14, 10)
        
        # 确保 date 列是 datetime 类型
        if 'date' in self.df.columns:
            self.df['date'] = pd.to_datetime(self.df['date'])
            self.df = self.df.sort_values('date')
    
    def plot_kline(self, save_path: Optional[str] = None, show: bool = True,
                   title: Optional[str] = None) -> plt.Figure:
        """绘制 K 线图
        
        Args:
            save_path: 保存路径
            show: 是否显示
            title: 图表标题
        
        Returns:
            Figure 对象
        """
        fig, ax = plt.subplots(figsize=self.fig_size)
        
        # 准备数据
        dates = self.df['date'].values
        opens = self.df['open'].values
        highs = self.df['high'].values
        lows = self.df['low'].values
        closes = self.df['close'].values
        volumes = self.df['vol'].values if 'vol' in self.df.columns else self.df.get('volume', [0]*len(dates))
        
        # 绘制 K 线
        for i in range(len(dates)):
            if closes[i] >= opens[i]:
                # 阳线（红色）
                ax.plot([dates[i], dates[i]], [lows[i], highs[i]], color='red', linewidth=0.8)
                ax.plot([dates[i], dates[i]], [opens[i], closes[i]], color='red', linewidth=2)
            else:
                # 阴线（绿色）
                ax.plot([dates[i], dates[i]], [lows[i], highs[i]], color='green', linewidth=0.8)
                ax.plot([dates[i], dates[i]], [opens[i], closes[i]], color='green', linewidth=2)
        
        # 绘制成交量柱状图（副图）
        ax2 = ax.twinx()
        colors = ['red' if closes[i] >= opens[i] else 'green' for i in range(len(dates))]
        ax2.bar(dates, volumes, color=colors, alpha=0.3, width=0.8)
        ax2.set_ylabel('成交量', fontsize=10)
        
        # 设置标题和标签
        stock_name = f"{self.name} ({self.ts_code})" if self.name else self.ts_code
        ax.set_title(title or f"K 线图 - {stock_name}", fontsize=14, fontweight='bold')
        ax.set_xlabel('日期', fontsize=10)
        ax.set_ylabel('价格', fontsize=10)
        
        # 格式化 x 轴日期
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        plt.xticks(rotation=45)
        
        # 网格
        ax.grid(True, alpha=0.3)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图片
        if save_path:
            os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)
            fig.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"✓ K 线图已保存至：{save_path}")
        
        if show:
            plt.show()
        else:
            plt.close()
        
        return fig
    
    def plot_with_indicators(self, indicators: List[str] = ['MA5', 'MA10', 'MA20'],
                            save_path: Optional[str] = None, show: bool = True) -> plt.Figure:
        """绘制带技术指标的 K 线图
        
        Args:
            indicators: 要显示的指标列表
            save_path: 保存路径
            show: 是否显示
        
        Returns:
            Figure 对象
        """
        # 创建多子图
        n_plots = 1 + len(indicators)
        fig, axes = plt.subplots(n_plots, 1, figsize=(self.fig_size[0], self.fig_size[1] + 2),
                                sharex=True, gridspec_kw={'height_ratios': [3] + [1] * len(indicators)})
        
        if n_plots == 1:
            axes = [axes]
        
        # 主图 - K 线
        ax = axes[0]
        dates = self.df['date'].values
        closes = self.df['close'].values
        opens = self.df['open'].values
        highs = self.df['high'].values
        lows = self.df['low'].values
        
        for i in range(len(dates)):
            color = 'red' if closes[i] >= opens[i] else 'green'
            ax.plot([dates[i], dates[i]], [lows[i], highs[i]], color=color, linewidth=0.8)
            ax.plot([dates[i], dates[i]], [opens[i], closes[i]], color=color, linewidth=2)
        
        stock_name = f"{self.name} ({self.ts_code})" if self.name else self.ts_code
        ax.set_title(f"K 线图与技术指标 - {stock_name}", fontsize=14, fontweight='bold')
        ax.set_ylabel('价格', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # 绘制均线
        if 'MA5' in indicators and 'close_ma5' in self.df.columns:
            ax.plot(dates, self.df['close_ma5'].values, label='MA5', color='orange', linewidth=1)
        if 'MA10' in indicators and 'close_ma10' in self.df.columns:
            ax.plot(dates, self.df['close_ma10'].values, label='MA10', color='purple', linewidth=1)
        if 'MA20' in indicators and 'close_ma20' in self.df.columns:
            ax.plot(dates, self.df['close_ma20'].values, label='MA20', color='blue', linewidth=1)
        if 'MA60' in indicators and 'close_ma60' in self.df.columns:
            ax.plot(dates, self.df['close_ma60'].values, label='MA60', color='green', linewidth=1)
        
        ax.legend(loc='upper left')
        
        # 绘制其他指标
        for idx, indicator in enumerate(indicators, 1):
            ax_ind = axes[idx]
            
            if indicator == 'VOL':
                if 'vol' in self.df.columns:
                    colors = ['red' if closes[i] >= opens[i] else 'green' for i in range(len(dates))]
                    ax_ind.bar(dates, self.df['vol'].values, color=colors, alpha=0.5)
                ax_ind.set_ylabel('成交量', fontsize=9)
            
            elif indicator == 'MACD':
                if all(col in self.df.columns for col in ['macd', 'signal', 'hist']):
                    ax_ind.plot(dates, self.df['macd'].values, label='MACD', color='black', linewidth=1)
                    ax_ind.plot(dates, self.df['signal'].values, label='Signal', color='red', linewidth=1)
                    ax_ind.bar(dates, self.df['hist'].values, color='gray', alpha=0.5, label='Hist')
                ax_ind.set_ylabel('MACD', fontsize=9)
                ax_ind.legend(loc='upper left', fontsize=8)
            
            elif indicator == 'KDJ':
                if all(col in self.df.columns for col in ['kdj_k', 'kdj_d', 'kdj_j']):
                    ax_ind.plot(dates, self.df['kdj_k'].values, label='K', linewidth=1)
                    ax_ind.plot(dates, self.df['kdj_d'].values, label='D', linewidth=1)
                    ax_ind.plot(dates, self.df['kdj_j'].values, label='J', linewidth=1)
                ax_ind.set_ylabel('KDJ', fontsize=9)
                ax_ind.axhline(y=80, color='r', linestyle='--', alpha=0.5)
                ax_ind.axhline(y=20, color='g', linestyle='--', alpha=0.5)
                ax_ind.legend(loc='upper left', fontsize=8)
            
            elif indicator == 'RSI':
                if 'rsi' in self.df.columns:
                    ax_ind.plot(dates, self.df['rsi'].values, color='purple', linewidth=1)
                ax_ind.set_ylabel('RSI', fontsize=9)
                ax_ind.axhline(y=70, color='r', linestyle='--', alpha=0.5)
                ax_ind.axhline(y=30, color='g', linestyle='--', alpha=0.5)
            
            elif indicator == 'CCI':
                if 'cci' in self.df.columns:
                    ax_ind.plot(dates, self.df['cci'].values, color='blue', linewidth=1)
                ax_ind.set_ylabel('CCI', fontsize=9)
                ax_ind.axhline(y=100, color='r', linestyle='--', alpha=0.5)
                ax_ind.axhline(y=-100, color='g', linestyle='--', alpha=0.5)
            
            ax_ind.grid(True, alpha=0.3)
        
        # 设置 x 轴
        axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        axes[-1].xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        # 保存图片
        if save_path:
            os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)
            fig.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"✓ 指标图已保存至：{save_path}")
        
        if show:
            plt.show()
        else:
            plt.close()
        
        return fig
    
    def plot_price_distribution(self, save_path: Optional[str] = None, 
                               show: bool = True) -> plt.Figure:
        """绘制价格分布直方图
        
        Args:
            save_path: 保存路径
            show: 是否显示
        
        Returns:
            Figure 对象
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        closes = self.df['close'].values
        
        ax.hist(closes, bins=30, color='skyblue', edgecolor='black', alpha=0.7)
        ax.axvline(closes.mean(), color='red', linestyle='--', label=f'均价：{closes.mean():.2f}')
        
        stock_name = f"{self.name} ({self.ts_code})" if self.name else self.ts_code
        ax.set_title(f"价格分布 - {stock_name}", fontsize=14)
        ax.set_xlabel('价格', fontsize=10)
        ax.set_ylabel('频数', fontsize=10)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"✓ 价格分布图已保存至：{save_path}")
        
        if show:
            plt.show()
        else:
            plt.close()
        
        return fig
    
    def plot_volume_analysis(self, save_path: Optional[str] = None,
                            show: bool = True) -> plt.Figure:
        """绘制成交量分析图
        
        Args:
            save_path: 保存路径
            show: 是否显示
        
        Returns:
            Figure 对象
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
        
        dates = self.df['date'].values
        volumes = self.df['vol'].values if 'vol' in self.df.columns else self.df.get('volume', [0]*len(dates))
        closes = self.df['close'].values
        opens = self.df['open'].values
        
        # 上图：成交量
        colors = ['red' if closes[i] >= opens[i] else 'green' for i in range(len(dates))]
        ax1.bar(dates, volumes, color=colors, alpha=0.5)
        ax1.set_ylabel('成交量', fontsize=10)
        ax1.set_title(f"成交量分析 - {self.name or self.ts_code}", fontsize=14)
        ax1.grid(True, alpha=0.3)
        
        # 下图：收盘价和均量线
        ax2.plot(dates, closes, label='收盘价', color='black', linewidth=1)
        if 'vol_ma5' in self.df.columns:
            ax2_twin = ax2.twinx()
            ax2_twin.plot(dates, self.df['vol_ma5'].values, label='5 日均量', color='orange', linewidth=1.5)
            ax2_twin.set_ylabel('均量', fontsize=10)
        ax2.set_ylabel('价格', fontsize=10)
        ax2.legend(loc='upper left')
        ax2.grid(True, alpha=0.3)
        
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"✓ 成交量分析图已保存至：{save_path}")
        
        if show:
            plt.show()
        else:
            plt.close()
        
        return fig


def generate_visualization_report(df: pd.DataFrame, ts_code: str, name: str,
                                  output_dir: str = './reports') -> str:
    """生成可视化报告
    
    Args:
        df: 股票数据
        ts_code: 股票代码
        name: 股票名称
        output_dir: 输出目录
    
    Returns:
        报告路径
    """
    os.makedirs(output_dir, exist_ok=True)
    viz = StockVisualizer(df, ts_code, name)
    
    report_path = f"{output_dir}/{ts_code}_{datetime.now().strftime('%Y%m%d')}"
    
    # 生成各种图表
    viz.plot_kline(save_path=f"{report_path}_kline.png", show=False)
    viz.plot_with_indicators(
        indicators=['MA5', 'MA10', 'MA20', 'VOL', 'MACD'],
        save_path=f"{report_path}_indicators.png",
        show=False
    )
    viz.plot_price_distribution(save_path=f"{report_path}_distribution.png", show=False)
    
    return report_path


if __name__ == "__main__":
    print("可视化模块 - 需要安装 matplotlib")
    print("pip install matplotlib")

# 提供一个别名，兼容旧代码
Visualizer = StockVisualizer
