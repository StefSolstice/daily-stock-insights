#!/usr/bin/env python3
"""
Daily Stock Insights - Web UI 系统测试脚本
"""

import requests
import time
import sys

BASE_URL = 'http://localhost:5000'

def test_web_ui():
    """测试 Web UI 所有功能"""
    session = requests.Session()
    
    print("=" * 60)
    print("🧪 Daily Stock Insights Web UI 系统测试")
    print("=" * 60)
    
    # 测试 1: 访问登录页面
    print("\n1️⃣ 测试登录页面...")
    resp = session.get(f'{BASE_URL}/login')
    if resp.status_code == 200 and '登录' in resp.text:
        print('✅ 登录页面加载成功')
    else:
        print('❌ 登录页面加载失败')
        return False
    
    # 测试 2: 访问注册页面
    print("\n2️⃣ 测试注册页面...")
    resp = session.get(f'{BASE_URL}/register')
    if resp.status_code == 200 and '注册' in resp.text:
        print('✅ 注册页面加载成功')
    else:
        print('❌ 注册页面加载失败')
        return False
    
    # 测试 3: 用户注册
    print("\n3️⃣ 测试用户注册...")
    username = f'test_{int(time.time())}'
    password = 'test123'
    data = {
        'username': username,
        'password': password,
        'confirm_password': password
    }
    resp = session.post(f'{BASE_URL}/register', data=data, allow_redirects=False)
    if resp.status_code in [200, 302]:
        print(f'✅ 用户注册成功：{username}')
    else:
        print(f'❌ 用户注册失败：{resp.status_code}')
        return False
    
    # 测试 4: 用户登录
    print("\n4️⃣ 测试用户登录...")
    data = {'username': username, 'password': password}
    resp = session.post(f'{BASE_URL}/login', data=data, allow_redirects=False)
    if resp.status_code in [200, 302] and '仪表盘' in session.get(f'{BASE_URL}/dashboard').text:
        print('✅ 用户登录成功')
    else:
        print('❌ 用户登录失败')
        return False
    
    # 测试 5: 访问仪表盘
    print("\n5️⃣ 测试仪表盘...")
    resp = session.get(f'{BASE_URL}/dashboard')
    if resp.status_code == 200 and '仪表盘' in resp.text:
        print('✅ 仪表盘加载成功')
    else:
        print('❌ 仪表盘加载失败')
        return False
    
    # 测试 6: 访问自选股页面
    print("\n6️⃣ 测试自选股页面...")
    resp = session.get(f'{BASE_URL}/watchlist')
    if resp.status_code == 200 and '自选股' in resp.text:
        print('✅ 自选股页面加载成功')
    else:
        print('❌ 自选股页面加载失败')
        return False
    
    # 测试 7: 添加分类
    print("\n7️⃣ 测试添加分类...")
    data = {'name': f'测试分类_{int(time.time())}'}
    resp = session.post(f'{BASE_URL}/api/category/add', json=data)
    if resp.status_code == 200:
        print('✅ 分类添加成功')
        category_id = resp.json().get('id')
    else:
        print(f'⚠️  分类可能已存在：{resp.status_code}')
    
    # 测试 8: 股票搜索
    print("\n8️⃣ 测试股票搜索...")
    resp = session.get(f'{BASE_URL}/api/stock/search?q=平安')
    if resp.status_code == 200:
        stocks = resp.json()
        print(f'✅ 股票搜索成功，找到 {len(stocks)} 只股票')
        if stocks:
            print(f'   示例：{stocks[0].get("name")} ({stocks[0].get("ts_code")})')
    else:
        print(f'❌ 股票搜索失败：{resp.status_code}')
    
    # 测试 9: 添加自选股
    print("\n9️⃣ 测试添加自选股...")
    data = {'ts_code': '000001.SZ', 'name': '平安银行'}
    resp = session.post(f'{BASE_URL}/api/stock/add', json=data)
    if resp.status_code == 200:
        print('✅ 自选股添加成功')
    else:
        print(f'⚠️  股票可能已存在：{resp.json().get("error", "")}')
    
    # 测试 10: 股票分析
    print("\n🔟 测试股票分析 API...")
    resp = session.get(f'{BASE_URL}/api/analyze?ts_code=000001.SZ')
    if resp.status_code == 200:
        data = resp.json()
        if 'error' not in data:
            print('✅ 股票分析成功')
            print(f'   代码：{data.get("ts_code")}')
            print(f'   当前价：{data.get("current_price")}')
            if data.get('technical'):
                print(f'   RSI: {data["technical"].get("rsi")}')
        else:
            print(f'⚠️  分析返回错误：{data.get("error")}')
    else:
        print(f'❌ 股票分析失败：{resp.status_code}')
    
    # 测试 11: 访问分析页面
    print("\n1️⃣1️⃣ 测试分析页面...")
    resp = session.get(f'{BASE_URL}/analysis?ts_code=000001.SZ')
    if resp.status_code == 200 and '股票分析' in resp.text:
        print('✅ 分析页面加载成功')
    else:
        print('❌ 分析页面加载失败')
    
    # 测试 12: 访问设置页面
    print("\n1️⃣2️⃣ 测试设置页面...")
    resp = session.get(f'{BASE_URL}/settings')
    if resp.status_code == 200 and '设置' in resp.text:
        print('✅ 设置页面加载成功')
    else:
        print('❌ 设置页面加载失败')
    
    # 测试 13: 退出登录
    print("\n1️⃣3️⃣ 测试退出登录...")
    resp = session.get(f'{BASE_URL}/logout', allow_redirects=False)
    resp = session.get(f'{BASE_URL}/dashboard', allow_redirects=False)
    if resp.status_code in [302, 401]:
        print('✅ 退出登录成功')
    else:
        print('❌ 退出登录失败')
    
    print("\n" + "=" * 60)
    print("✅ 系统测试完成！")
    print("=" * 60)
    return True

if __name__ == '__main__':
    try:
        # 等待服务器启动
        print("⏳ 等待服务器启动...")
        time.sleep(2)
        
        success = test_web_ui()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试异常：{e}")
        sys.exit(1)
