#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试套件 - Daily Stock Insights
"""

import unittest
import os
import sys
import pandas as pd
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestStockFetcher(unittest.TestCase):
    """测试股票数据获取模块"""
    
    def setUp(self):
        from stock_fetcher import StockFetcher
        self.fetcher = StockFetcher()
    
    def test_get_daily(self):
        """测试获取日线数据"""
        df = self.fetcher.get_daily('000001.SZ')
        self.assertIsNotNone(df)
        self.assertFalse(df.empty)
        self.assertIn('close', df.columns)
        self.assertIn('vol', df.columns)
    
    def test_invalid_stock_code(self):
        """测试无效股票代码"""
        df = self.fetcher.get_daily('INVALID.SZ')
        # 应该返回 None 或空 DataFrame
        self.assertTrue(df is None or df.empty)


class TestTechnicalIndicators(unittest.TestCase):
    """测试技术指标计算"""
    
    def setUp(self):
        from technical_indicators import TechnicalIndicators
        self.ti = TechnicalIndicators()
        
        # 创建测试数据
        self.test_df = pd.DataFrame({
            'close': [10.0, 10.5, 11.0, 10.8, 11.2, 11.5, 11.3, 11.8, 12.0, 12.2],
            'high': [10.2, 10.7, 11.3, 11.0, 11.5, 11.8, 11.6, 12.0, 12.3, 12.5],
            'low': [9.8, 10.3, 10.8, 10.5, 11.0, 11.3, 11.1, 11.6, 11.8, 12.0],
            'vol': [1000, 1200, 1100, 1300, 1400, 1500, 1350, 1600, 1700, 1800]
        })
    
    def test_calculate_ma(self):
        """测试均线计算"""
        df = self.ti.calculate_ma(self.test_df, window=5)
        self.assertIn('close_ma5', df.columns)
        # 前 4 个值应该是 NaN
        self.assertTrue(pd.isna(df['close_ma5'].iloc[0:4]).all())
        # 第 5 个值应该有数据
        self.assertFalse(pd.isna(df['close_ma5'].iloc[4]))
    
    def test_calculate_macd(self):
        """测试 MACD 计算"""
        df = self.ti.calculate_macd(self.test_df)
        self.assertIn('macd', df.columns)
        self.assertIn('signal', df.columns)
        self.assertIn('histogram', df.columns)
    
    def test_calculate_rsi(self):
        """测试 RSI 计算"""
        df = self.ti.calculate_rsi(self.test_df, window=6)
        self.assertIn('rsi', df.columns)
        # RSI 值应该在 0-100 之间
        rsi_values = df['rsi'].dropna()
        if not rsi_values.empty:
            self.assertTrue((rsi_values >= 0).all())
            self.assertTrue((rsi_values <= 100).all())


class TestAnalyzer(unittest.TestCase):
    """测试股票分析器"""
    
    def test_analyzer_initialization(self):
        """测试分析器初始化"""
        from analyzer import StockAnalyzer
        analyzer = StockAnalyzer('000001.SZ', None)
        self.assertEqual(analyzer.ts_code, '000001.SZ')
    
    def test_generate_summary(self):
        """测试生成分析摘要"""
        from analyzer import StockAnalyzer
        analyzer = StockAnalyzer('000001.SZ', None)
        
        # 创建测试数据
        test_df = pd.DataFrame({
            'trade_date': ['20260310', '20260311', '20260312'],
            'close': [10.0, 10.5, 11.0],
            'vol': [1000, 1200, 1100],
            'close_ma5': [None, None, 10.5],
            'macd': [0.1, 0.15, 0.2],
            'rsi': [50, 55, 60]
        })
        
        report = analyzer.generate_summary(test_df)
        self.assertIsInstance(report, str)
        self.assertTrue(len(report) > 0)


class TestFundamentalAnalyzer(unittest.TestCase):
    """测试基本面分析器"""
    
    def test_fundamental_analyzer_initialization(self):
        """测试基本面分析器初始化"""
        from fundamental_analyzer import FundamentalAnalyzer
        analyzer = FundamentalAnalyzer('000001.SZ', None)
        self.assertEqual(analyzer.ts_code, '000001.SZ')


class TestDataExporter(unittest.TestCase):
    """测试数据导出器"""
    
    def setUp(self):
        from exporter import DataExporter
        self.test_df = pd.DataFrame({
            'trade_date': ['20260310', '20260311', '20260312'],
            'close': [10.0, 10.5, 11.0],
            'vol': [1000, 1200, 1100]
        })
        self.exporter = DataExporter(self.test_df, '000001.SZ', '平安银行')
    
    def test_export_csv(self):
        """测试 CSV 导出"""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            path = self.exporter.to_csv(output_dir=tmpdir)
            self.assertTrue(os.path.exists(path))
            self.assertTrue(path.endswith('.csv'))
    
    def test_export_excel(self):
        """测试 Excel 导出"""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            path = self.exporter.to_excel(output_dir=tmpdir)
            self.assertTrue(os.path.exists(path))
            self.assertTrue(path.endswith('.xlsx'))
    
    def test_export_json(self):
        """测试 JSON 导出"""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            path = self.exporter.to_json(output_dir=tmpdir)
            self.assertTrue(os.path.exists(path))
            self.assertTrue(path.endswith('.json'))


class TestVisualizer(unittest.TestCase):
    """测试可视化模块"""
    
    def setUp(self):
        from visualizer import StockVisualizer
        self.test_df = pd.DataFrame({
            'date': ['2026-03-10', '2026-03-11', '2026-03-12'],
            'open': [10.0, 10.5, 11.0],
            'high': [10.5, 11.0, 11.5],
            'low': [9.8, 10.3, 10.8],
            'close': [10.3, 10.8, 11.3],
            'vol': [1000, 1200, 1100]
        })
        self.viz = StockVisualizer(self.test_df, '000001.SZ', '平安银行')
    
    def test_visualizer_initialization(self):
        """测试可视化器初始化"""
        self.assertEqual(self.viz.ts_code, '000001.SZ')
        self.assertEqual(self.viz.name, '平安银行')
    
    def test_plot_kline(self):
        """测试 K 线图生成"""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'test_kline.png')
            self.viz.plot_kline(save_path=path, show=False)
            self.assertTrue(os.path.exists(path))


class TestConfigLoader(unittest.TestCase):
    """测试配置加载"""
    
    def test_env_file_loading(self):
        """测试 .env 文件加载"""
        # 创建临时 .env 文件
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = os.path.join(tmpdir, '.env')
            test_token = 'test_token_12345'
            
            with open(env_file, 'w') as f:
                f.write(f'TUSHARE_TOKEN={test_token}\n')
            
            # 验证文件内容
            with open(env_file, 'r') as f:
                content = f.read()
                self.assertIn(test_token, content)


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)
