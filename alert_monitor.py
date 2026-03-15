#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
价格提醒监控模块
支持设置价格提醒阈值，监控股票价格变化
"""

import json
import os
from datetime import datetime


class PriceAlert:
    """价格提醒管理器"""
    
    def __init__(self, config_file='alerts.json'):
        self.config_file = config_file
        self.alerts = self.load_alerts()
    
    def load_alerts(self):
        """加载提醒配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_alerts(self):
        """保存提醒配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.alerts, f, ensure_ascii=False, indent=2)
    
    def add_alert(self, symbol, alert_type, price, name=None):
        """
        添加价格提醒
        
        Args:
            symbol: 股票代码
            alert_type: 提醒类型 (above/below/cross)
            price: 目标价格
            name: 股票名称（可选）
        """
        if symbol not in self.alerts:
            self.alerts[symbol] = []
        
        alert = {
            'type': alert_type,
            'price': float(price),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'active': True
        }
        
        if name:
            alert['name'] = name
        
        self.alerts[symbol].append(alert)
        self.save_alerts()
        
        alert_type_cn = {'above': '上涨超过', 'below': '下跌低于', 'cross': ' crossing'}
        print(f"✅ 已添加提醒：{symbol} {alert_type_cn.get(alert_type, alert_type)} ¥{price}")
    
    def list_alerts(self, symbol=None):
        """列出所有提醒"""
        if symbol:
            alerts = self.alerts.get(symbol, [])
            if alerts:
                print(f"\n📌 {symbol} 的提醒设置:")
                for i, alert in enumerate(alerts, 1):
                    status = "🟢" if alert.get('active', True) else "🔴"
                    type_cn = {'above': '上涨超过', 'below': '下跌低于', 'cross': '穿过'}
                    print(f"  {status} #{i}: {type_cn.get(alert['type'], alert['type'])} ¥{alert['price']}")
            else:
                print(f"⚠️  {symbol} 没有设置提醒")
        else:
            if not self.alerts:
                print("📭 暂无任何提醒设置")
                return
            
            print("\n📋 所有提醒设置:")
            for sym, alerts in self.alerts.items():
                print(f"\n  {sym} ({alerts[0].get('name', 'Unknown')}):")
                for i, alert in enumerate(alerts, 1):
                    status = "🟢" if alert.get('active', True) else "🔴"
                    type_cn = {'above': '上涨超过', 'below': '下跌低于', 'cross': '穿过'}
                    print(f"    {status} #{i}: {type_cn.get(alert['type'], alert['type'])} ¥{alert['price']}")
    
    def remove_alert(self, symbol, alert_index=None):
        """删除提醒"""
        if symbol not in self.alerts:
            print(f"⚠️  {symbol} 没有提醒设置")
            return
        
        if alert_index is None:
            # 删除所有提醒
            count = len(self.alerts[symbol])
            del self.alerts[symbol]
            self.save_alerts()
            print(f"✅ 已删除 {symbol} 的全部 {count} 个提醒")
        else:
            # 删除指定提醒
            if 0 <= alert_index < len(self.alerts[symbol]):
                removed = self.alerts[symbol].pop(alert_index)
                self.save_alerts()
                print(f"✅ 已删除提醒：{symbol} {removed['type']} ¥{removed['price']}")
            else:
                print(f"⚠️  无效的提醒编号")
    
    def check_alerts(self, current_prices):
        """
        检查当前价格是否触发提醒
        
        Args:
            current_prices: dict {symbol: {'price': float, 'name': str}}
        
        Returns:
            list: 触发的提醒列表
        """
        triggered = []
        
        for symbol, data in current_prices.items():
            if symbol not in self.alerts:
                continue
            
            current_price = data.get('price', 0)
            
            for alert in self.alerts[symbol]:
                if not alert.get('active', True):
                    continue
                
                target_price = alert['price']
                alert_type = alert['type']
                
                triggered_alert = None
                
                if alert_type == 'above' and current_price >= target_price:
                    triggered_alert = {
                        'symbol': symbol,
                        'name': data.get('name', symbol),
                        'type': '上涨突破',
                        'target': target_price,
                        'current': current_price
                    }
                elif alert_type == 'below' and current_price <= target_price:
                    triggered_alert = {
                        'symbol': symbol,
                        'name': data.get('name', symbol),
                        'type': '下跌突破',
                        'target': target_price,
                        'current': current_price
                    }
                
                if triggered_alert:
                    triggered.append(triggered_alert)
        
        return triggered
    
    def print_triggered_alerts(self, triggered):
        """打印触发的提醒"""
        if not triggered:
            print("✅ 无提醒触发")
            return
        
        print("\n🚨 提醒触发！")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        for alert in triggered:
            direction = "📈" if alert['type'] == '上涨突破' else "📉"
            print(f"{direction} {alert['name']} ({alert['symbol']})")
            print(f"    {alert['type']} ¥{alert['target']:.2f}")
            print(f"    当前价格：¥{alert['current']:.2f}")
            print(f"    变化：¥{alert['current'] - alert['target']:+.2f}")
            print()


def main():
    """CLI 入口"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="💰 价格提醒监控工具",
        epilog="""
示例:
  %(prog)s add 000001.SZ above 12.5 --name 平安银行
  %(prog)s add TSLA below 375 --name 特斯拉
  %(prog)s list
  %(prog)s list TSLA
  %(prog)s remove TSLA
  %(prog)s remove TSLA --index 0
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # add 命令
    add_parser = subparsers.add_parser("add", help="添加价格提醒")
    add_parser.add_argument("symbol", help="股票代码")
    add_parser.add_argument("type", choices=['above', 'below', 'cross'], help="提醒类型")
    add_parser.add_argument("price", type=float, help="目标价格")
    add_parser.add_argument("--name", "-n", help="股票名称")
    
    # list 命令
    list_parser = subparsers.add_parser("list", help="列出提醒")
    list_parser.add_argument("symbol", nargs="?", help="股票代码（可选）")
    
    # remove 命令
    remove_parser = subparsers.add_parser("remove", help="删除提醒")
    remove_parser.add_argument("symbol", help="股票代码")
    remove_parser.add_argument("--index", "-i", type=int, help="提醒编号（从 0 开始）")
    
    # check 命令
    check_parser = subparsers.add_parser("check", help="检查提醒（需要提供价格）")
    check_parser.add_argument("symbol", help="股票代码")
    check_parser.add_argument("price", type=float, help="当前价格")
    check_parser.add_argument("--name", "-n", help="股票名称")
    
    args = parser.parse_args()
    
    alert = PriceAlert()
    
    if args.command == "add":
        alert.add_alert(args.symbol, args.type, args.price, args.name)
    elif args.command == "list":
        alert.list_alerts(args.symbol)
    elif args.command == "remove":
        alert.remove_alert(args.symbol, args.index)
    elif args.command == "check":
        triggered = alert.check_alerts({args.symbol: {'price': args.price, 'name': args.name or args.symbol}})
        alert.print_triggered_alerts(triggered)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

# 提供一个别名，兼容旧代码
AlertMonitor = PriceAlert
