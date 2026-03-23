#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
推送通知模块
支持Telegram、微信、邮件等多种推送方式
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime
import requests
from pathlib import Path


class NotificationService:
    """通知服务类"""
    
    def __init__(self, config: Dict = None):
        """初始化通知服务
        
        Args:
            config: 配置字典，包含各种推送服务的配置
        """
        self.config = config or {}
        self.telegram_bot_token = self.config.get('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = self.config.get('TELEGRAM_CHAT_ID')
        self.wechat_webhook = self.config.get('WECHAT_WEBHOOK')
        self.email_config = self.config.get('EMAIL_CONFIG', {})
    
    def send_telegram_message(self, message: str, parse_mode: str = 'Markdown') -> bool:
        """发送Telegram消息
        
        Args:
            message: 消息内容
            parse_mode: 解析模式，'Markdown' 或 'HTML'
            
        Returns:
            发送是否成功
        """
        if not self.telegram_bot_token or not self.telegram_chat_id:
            print("Telegram配置不完整，跳过推送")
            return False
        
        url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
        
        try:
            payload = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get('ok'):
                print("✅ Telegram消息发送成功")
                return True
            else:
                print(f"❌ Telegram消息发送失败: {result.get('description')}")
                return False
                
        except Exception as e:
            print(f"❌ Telegram消息发送异常: {e}")
            return False
    
    def send_wechat_message(self, message: str) -> bool:
        """发送企业微信消息
        
        Args:
            message: 消息内容
            
        Returns:
            发送是否成功
        """
        if not self.wechat_webhook:
            print("企业微信Webhook未配置，跳过推送")
            return False
        
        try:
            payload = {
                "msgtype": "text",
                "text": {
                    "content": message
                }
            }
            
            response = requests.post(self.wechat_webhook, json=payload, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get('errcode') == 0:
                print("✅ 企业微信消息发送成功")
                return True
            else:
                print(f"❌ 企业微信消息发送失败: {result.get('errmsg')}")
                return False
                
        except Exception as e:
            print(f"❌ 企业微信消息发送异常: {e}")
            return False
    
    def format_stock_selection_report(self, results: List[Dict]) -> str:
        """格式化股票筛选报告
        
        Args:
            results: 选股结果列表
            
        Returns:
            格式化的报告字符串
        """
        if not results:
            return "🔍 股票筛选结果\n\n今日未发现符合条件的股票。"
        
        report = "🔍 股票筛选结果\n"
        report += f"📅 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # 限制最多显示10只股票，避免消息过长
        display_results = results[:10]
        
        for i, result in enumerate(display_results, 1):
            ts_code = result['ts_code']
            tech_analysis = result['tech_analysis']
            fund_analysis = result['fundamental_analysis']
            money_analysis = result['money_flow_analysis']
            
            report += f"{i}. {ts_code}\n"
            report += f"   📊 总分: {result['total_score']} | 技术:{tech_analysis.get('score', 0)} "
            report += f"| 基本面:{fund_analysis.get('fundamental_score', 0)} | 资金:{money_analysis.get('money_flow_score', 0)}\n"
            
            # 简化显示条件
            tech_met = tech_analysis.get('conditions_met', [])[:3]  # 只显示前3个
            if tech_met:
                report += f"   📈 技术面: {', '.join(tech_met)}\n"
            
            # 基本面简要信息
            pe = fund_analysis.get('pe', 'N/A')
            pb = fund_analysis.get('pb', 'N/A')
            if pe != 'N/A' and pb != 'N/A':
                report += f"   💰 基本面: PE={pe:.2f}, PB={pb:.2f}\n"
            
            # 资金面简要信息
            money_met = money_analysis.get('conditions_met', [])[:2]  # 只显示前2个
            if money_met:
                report += f"   💵 资金面: {', '.join(money_met)}\n"
            
            report += "\n"
        
        if len(results) > 10:
            report += f"...\n共找到 {len(results)} 只符合条件的股票，以上显示前10只。\n"
        
        report += f"\n📋 筛选条件: MA5上穿MA10, 成交量放大, RSI正常, MACD金叉, 价格在布林带中轨上方等"
        
        return report
    
    def send_stock_selection_notification(self, results: List[Dict]) -> Dict[str, bool]:
        """发送股票筛选结果通知
        
        Args:
            results: 选股结果列表
            
        Returns:
            各种推送方式的成功状态
        """
        if not results:
            message = "🔍 股票筛选结果\n\n今日未发现符合条件的股票。"
        else:
            message = self.format_stock_selection_report(results)
        
        results = {}
        
        # 发送Telegram消息
        if self.telegram_bot_token and self.telegram_chat_id:
            results['telegram'] = self.send_telegram_message(message)
        else:
            print("Telegram配置不完整，跳过推送")
            results['telegram'] = False
        
        # 发送企业微信消息
        if self.wechat_webhook:
            results['wechat'] = self.send_wechat_message(message)
        else:
            print("企业微信Webhook未配置，跳过推送")
            results['wechat'] = False
        
        return results
    
    def send_custom_notification(self, message: str, channels: List[str] = None) -> Dict[str, bool]:
        """发送自定义通知
        
        Args:
            message: 消息内容
            channels: 推送渠道列表，如 ['telegram', 'wechat']
            
        Returns:
            各种推送方式的成功状态
        """
        if channels is None:
            channels = ['telegram', 'wechat']
        
        results = {}
        
        for channel in channels:
            if channel == 'telegram':
                results['telegram'] = self.send_telegram_message(message)
            elif channel == 'wechat':
                results['wechat'] = self.send_wechat_message(message)
        
        return results


def load_config_from_file(config_path: str = './config.json') -> Dict:
    """从文件加载配置
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"配置文件 {config_path} 不存在，使用默认配置")
        return {}
    except Exception as e:
        print(f"读取配置文件失败: {e}")
        return {}


def main():
    """测试函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="通知服务测试")
    parser.add_argument("--test-telegram", action="store_true", help="测试Telegram推送")
    parser.add_argument("--test-wechat", action="store_true", help="测试企业微信推送")
    parser.add_argument("--message", type=str, default="这是一条测试消息", help="测试消息内容")
    
    args = parser.parse_args()
    
    # 从环境变量加载配置
    config = {
        'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN'),
        'TELEGRAM_CHAT_ID': os.getenv('TELEGRAM_CHAT_ID'),
        'WECHAT_WEBHOOK': os.getenv('WECHAT_WEBHOOK')
    }
    
    notifier = NotificationService(config)
    
    if args.test_telegram:
        print("测试Telegram推送...")
        success = notifier.send_telegram_message(args.message)
        print(f"Telegram推送结果: {'成功' if success else '失败'}")
    
    if args.test_wechat:
        print("测试企业微信推送...")
        success = notifier.send_wechat_message(args.message)
        print(f"企业微信推送结果: {'成功' if success else '失败'}")


if __name__ == "__main__":
    main()