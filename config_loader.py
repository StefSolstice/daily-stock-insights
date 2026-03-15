#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置加载器
用于加载和管理应用配置
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化配置加载器
        
        Args:
            config_path: 配置文件路径，默认为 .env 文件
        """
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), '.env')
        self.config = {}
        
        # 从环境变量和 .env 文件加载配置
        self.load()
    
    def load(self) -> Dict[str, Any]:
        """加载配置
        
        Returns:
            配置字典
        """
        # 首先从 .env 文件加载
        if os.path.exists(self.config_path):
            self._load_from_env_file(self.config_path)
        
        # 然后从环境变量加载（覆盖 .env 文件中的相同键）
        self._load_from_environment()
        
        # 设置默认值
        self._set_defaults()
        
        return self.config
    
    def _load_from_env_file(self, env_path: str):
        """从 .env 文件加载配置
        
        Args:
            env_path: .env 文件路径
        """
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # 跳过注释和空行
                    if not line or line.startswith('#'):
                        continue
                    
                    # 解析 KEY=VALUE 格式
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # 移除引号
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        self.config[key] = value
        except Exception as e:
            print(f"[DEBUG] 读取 .env 文件失败：{e}")
    
    def _load_from_environment(self):
        """从环境变量加载配置"""
        # 读取 TuShare Token
        token = os.getenv('TUSHARE_TOKEN')
        if token:
            self.config['TUSHARE_TOKEN'] = token
        
        # 读取日志级别
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.config['LOG_LEVEL'] = log_level
        
        # 读取导出目录
        export_dir = os.getenv('EXPORT_DIR', './exports')
        self.config['EXPORT_DIR'] = export_dir
        
        # 读取数据目录
        data_dir = os.getenv('DATA_DIR', './data')
        self.config['DATA_DIR'] = data_dir
        
        # 读取其他可能的配置
        for key, value in os.environ.items():
            if key.startswith(('TUSHARE_', 'LOG_', 'EXPORT_', 'DATA_', 'ALERT_', 'FETCH_', 'ANALYZE_')):
                self.config[key] = value
    
    def _set_defaults(self):
        """设置默认配置值"""
        defaults = {
            'TUSHARE_TOKEN': '',
            'LOG_LEVEL': 'INFO',
            'EXPORT_DIR': './exports',
            'DATA_DIR': './data',
            'DEFAULT_START_DAYS': 60,  # 默认开始天数
            'CACHE_ENABLED': True,     # 启用缓存
            'CACHE_DIR': './cache',    # 缓存目录
            'MAX_WORKERS': 4,          # 最大并发数
        }
        
        for key, default_value in defaults.items():
            if key not in self.config:
                self.config[key] = default_value
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """设置配置值
        
        Args:
            key: 配置键
            value: 配置值
        """
        self.config[key] = value
    
    def save(self, config_path: Optional[str] = None):
        """保存配置到文件
        
        Args:
            config_path: 配置文件路径，默认使用初始化时的路径
        """
        save_path = config_path or self.config_path
        if not save_path:
            raise ValueError("未指定配置文件路径")
        
        with open(save_path, 'w', encoding='utf-8') as f:
            for key, value in self.config.items():
                f.write(f"{key}={value}\n")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典
        
        Returns:
            配置字典
        """
        return self.config.copy()


if __name__ == "__main__":
    # 测试配置加载器
    loader = ConfigLoader()
    config = loader.load()
    
    print("配置加载完成：")
    for key, value in config.items():
        if key == 'TUSHARE_TOKEN':
            # 隐藏 token 的具体内容
            print(f"  {key}: {'*' * len(value) if value else 'NOT_SET'}")
        else:
            print(f"  {key}: {value}")