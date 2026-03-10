#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据导出模块
支持 CSV、Excel、JSON 等格式导出
"""

import pandas as pd
import json
import os
from typing import Optional, Dict, Any
from datetime import datetime


class DataExporter:
    """数据导出器"""
    
    def __init__(self, df: pd.DataFrame, ts_code: str = '', name: str = ''):
        """初始化
        
        Args:
            df: 数据 DataFrame
            ts_code: 股票代码
            name: 股票名称
        """
        self.df = df
        self.ts_code = ts_code
        self.name = name
    
    def to_csv(self, filepath: Optional[str] = None, 
               include_index: bool = False) -> str:
        """导出为 CSV
        
        Args:
            filepath: 文件路径，默认自动生成
            include_index: 是否包含索引
        
        Returns:
            文件路径
        """
        if not filepath:
            date_str = datetime.now().strftime('%Y%m%d')
            stock_name = self.name.replace(' ', '') if self.name else self.ts_code
            filepath = f"./exports/{self.ts_code}_{date_str}.csv"
        
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
        self.df.to_csv(filepath, index=include_index, encoding='utf-8-sig')
        
        print(f"✓ CSV 已导出：{filepath}")
        return filepath
    
    def to_excel(self, filepath: Optional[str] = None,
                sheet_name: str = 'Stock Data') -> str:
        """导出为 Excel
        
        Args:
            filepath: 文件路径
            sheet_name: 工作表名称
        
        Returns:
            文件路径
        """
        if not filepath:
            date_str = datetime.now().strftime('%Y%m%d')
            stock_name = self.name.replace(' ', '') if self.name else self.ts_code
            filepath = f"./exports/{self.ts_code}_{date_str}.xlsx"
        
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            self.df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # 自动调整列宽
            worksheet = writer.sheets[sheet_name]
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"✓ Excel 已导出：{filepath}")
        return filepath
    
    def to_json(self, filepath: Optional[str] = None,
                orient: str = 'records', pretty: bool = True) -> str:
        """导出为 JSON
        
        Args:
            filepath: 文件路径
            orient: JSON 方向
            pretty: 是否美化格式
        
        Returns:
            文件路径
        """
        if not filepath:
            date_str = datetime.now().strftime('%Y%m%d')
            filepath = f"./exports/{self.ts_code}_{date_str}.json"
        
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
        
        # 转换为 JSON
        if orient == 'records':
            data = self.df.to_dict(orient='records')
        else:
            data = self.df.to_dict(orient=orient)
        
        # 添加元数据
        output = {
            "ts_code": self.ts_code,
            "name": self.name,
            "export_time": datetime.now().isoformat(),
            "record_count": len(self.df),
            "data": data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(output, f, ensure_ascii=False, indent=2, default=str)
            else:
                json.dump(output, f, ensure_ascii=False, default=str)
        
        print(f"✓ JSON 已导出：{filepath}")
        return filepath
    
    def export_all(self, base_path: Optional[str] = None) -> Dict[str, str]:
        """导出所有格式
        
        Args:
            base_path: 基础路径
        
        Returns:
            各格式文件路径字典
        """
        date_str = datetime.now().strftime('%Y%m%d')
        stock_name = self.name.replace(' ', '') if self.name else self.ts_code
        
        if not base_path:
            base_path = f"./exports/{self.ts_code}_{date_str}"
        
        results = {}
        
        # CSV
        results['csv'] = self.to_csv(f"{base_path}.csv")
        
        # Excel
        results['excel'] = self.to_excel(f"{base_path}.xlsx")
        
        # JSON
        results['json'] = self.to_json(f"{base_path}.json")
        
        print(f"\n✓ 已导出 3 种格式，文件前缀：{base_path}")
        
        return results
    
    def generate_summary(self) -> Dict[str, Any]:
        """生成数据摘要
        
        Returns:
            摘要字典
        """
        numeric_cols = self.df.select_dtypes(include=[float, int]).columns
        
        summary = {
            "ts_code": self.ts_code,
            "name": self.name,
            "total_records": len(self.df),
            "date_range": {
                "start": str(self.df['date'].min()) if 'date' in self.df.columns else None,
                "end": str(self.df['date'].max()) if 'date' in self.df.columns else None
            },
            "columns": list(self.df.columns),
            "numeric_stats": {}
        }
        
        for col in numeric_cols:
            summary["numeric_stats"][col] = {
                "mean": float(self.df[col].mean()) if not self.df[col].isna().all() else None,
                "min": float(self.df[col].min()) if not self.df[col].isna().all() else None,
                "max": float(self.df[col].max()) if not self.df[col].isna().all() else None,
                "std": float(self.df[col].std()) if not self.df[col].isna().all() else None
            }
        
        return summary


if __name__ == "__main__":
    print("数据导出模块")
    print("使用方式：")
    print("  exporter = DataExporter(df, '000001.SZ', '平安银行')")
    print("  exporter.to_csv()")
    print("  exporter.to_excel()")
    print("  exporter.export_all()")
