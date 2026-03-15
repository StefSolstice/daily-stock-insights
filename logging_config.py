#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志配置模块
提供统一的日志配置和彩色输出
"""

import logging
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import colorlog
    COLORLOG_AVAILABLE = True
except ImportError:
    COLORLOG_AVAILABLE = False


class LogFormatter:
    """日志格式化器"""
    
    # 彩色日志格式（终端）
    COLOR_FORMAT = (
        "%(log_color)s%(asctime)s | %(levelname)-8s | "
        "%(name)s | %(message)s%(reset)s"
    )
    
    # 详细日志格式（文件）
    FILE_FORMAT = (
        "%(asctime)s | %(levelname)-8s | %(name)s | "
        "%(filename)s:%(lineno)d | %(funcName)s | %(message)s"
    )
    
    # 简洁日志格式（控制台）
    SIMPLE_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    
    @staticmethod
    def get_color_formatter() -> logging.Formatter:
        """获取彩色日志格式化器"""
        if not COLORLOG_AVAILABLE:
            return logging.Formatter(LogFormatter.SIMPLE_FORMAT)
        
        return colorlog.ColoredFormatter(
            LogFormatter.COLOR_FORMAT,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            },
            reset=True,
            style='%'
        )
    
    @staticmethod
    def get_file_formatter() -> logging.Formatter:
        """获取文件日志格式化器"""
        return logging.Formatter(LogFormatter.FILE_FORMAT)
    
    @staticmethod
    def get_simple_formatter() -> logging.Formatter:
        """获取简洁日志格式化器"""
        return logging.Formatter(LogFormatter.SIMPLE_FORMAT)


def setup_logging(
    level: int = logging.INFO,
    log_dir: Optional[str] = None,
    log_file: Optional[str] = None,
    console_output: bool = True,
    file_output: bool = True,
    simple_console: bool = False
) -> logging.Logger:
    """配置日志系统
    
    Args:
        level: 日志级别，默认 INFO
        log_dir: 日志目录，默认 ./logs
        log_file: 日志文件名，默认自动生成
        console_output: 是否输出到控制台
        file_output: 是否输出到文件
        simple_console: 是否使用简洁控制台格式
        
    Returns:
        根日志记录器
    """
    # 获取根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # 清除现有处理器（避免重复）
    root_logger.handlers.clear()
    
    # 创建日志目录
    if log_dir is None:
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    
    if file_output:
        os.makedirs(log_dir, exist_ok=True)
        
        # 生成日志文件名
        if log_file is None:
            date_str = datetime.now().strftime('%Y%m%d')
            log_file = f"daily_stock_{date_str}.log"
        
        log_filepath = os.path.join(log_dir, log_file)
        
        # 文件处理器（详细格式）
        file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(LogFormatter.get_file_formatter())
        root_logger.addHandler(file_handler)
    
    # 控制台处理器（彩色格式）
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        if simple_console:
            console_handler.setFormatter(LogFormatter.get_simple_formatter())
        else:
            console_handler.setFormatter(LogFormatter.get_color_formatter())
        
        root_logger.addHandler(console_handler)
    
    # 捕获第三方库的过度日志
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('pillow').setLevel(logging.WARNING)
    
    # 输出日志配置信息
    logger = logging.getLogger(__name__)
    logger.info(f"日志系统初始化完成 - 级别：{logging.getLevelName(level)}")
    if file_output:
        logger.info(f"日志文件：{log_filepath}")
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """获取命名日志记录器
    
    Args:
        name: 日志记录器名称（通常是模块名）
        
    Returns:
        日志记录器
    """
    return logging.getLogger(name)


# 便捷函数
def debug(msg: str, *args, **kwargs):
    """输出 DEBUG 日志"""
    logging.getLogger(__name__).debug(msg, *args, **kwargs)


def info(msg: str, *args, **kwargs):
    """输出 INFO 日志"""
    logging.getLogger(__name__).info(msg, *args, **kwargs)


def warning(msg: str, *args, **kwargs):
    """输出 WARNING 日志"""
    logging.getLogger(__name__).warning(msg, *args, **kwargs)


def error(msg: str, *args, **kwargs):
    """输出 ERROR 日志"""
    logging.getLogger(__name__).error(msg, *args, **kwargs)


def critical(msg: str, *args, **kwargs):
    """输出 CRITICAL 日志"""
    logging.getLogger(__name__).critical(msg, *args, **kwargs)


if __name__ == "__main__":
    # 测试日志配置
    setup_logging(level=logging.DEBUG)
    logger = get_logger(__name__)
    
    logger.debug("这是一条 DEBUG 日志")
    logger.info("这是一条 INFO 日志")
    logger.warning("这是一条 WARNING 日志")
    logger.error("这是一条 ERROR 日志")
    logger.critical("这是一条 CRITICAL 日志")
