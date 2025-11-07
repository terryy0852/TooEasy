#!/usr/bin/env python3
"""
诊断会话超时和自动重定向问题
"""

import requests
import time
from bs4 import BeautifulSoup

BASE_URL = "https://tooeasy.onrender.com"

def test_session_timeout():
    """测试会话是否在15分钟后过期"""
    print("🔍 测试会话超时问题...")
    
    session = requests.Session()
    
    # 1. 登录
    print("\n1. 登录...")
    login_data = {
        'username': 'Schumacherm2013',
        'password': 'mS93294073'
    }
    
    login_response = session.post(f"{BASE_URL}/login", data=login_data)
    print(f"   登录状态: {login_response.status_code}")
    print(f"   重定向到: {login_response.url}")
    
    # 2. 检查初始仪表板访问
    print("\n2. 初始仪表板访问...")
    dashboard_response = session.get(f"{BASE_URL}/student_dashboard")
    print(f"   仪表板状态: {dashboard_response.status_code}")
    
    # 检查作业数量
    soup = BeautifulSoup(dashboard_response.text, 'html.parser')
    assignments = soup.find_all(class_='card')
    print(f"   初始作业数量: {len(assignments)}")
    
    # 3. 等待15分钟
    print("\n3. 等待15分钟...")
    wait_minutes = 15
    for minute in range(1, wait_minutes + 1):
        print(f"   等待中... {minute}分钟")
        time.sleep(60)  # 等待1分钟
        
        # 每分钟检查一次会话状态
        check_response = session.get(f"{BASE_URL}/student_dashboard")
        if check_response.status_code != 200 or "login" in check_response.url:
            print(f"   ❌ 会话在第{minute}分钟过期!")
            return True, minute
    
    # 4. 15分钟后检查最终状态
    print("\n4. 15分钟后检查...")
    final_response = session.get(f"{BASE_URL}/student_dashboard")
    print(f"   最终状态: {final_response.status_code}")
    print(f"   最终URL: {final_response.url}")
    
    # 检查是否被重定向到登录页面
    if "login" in final_response.url:
        print("   ❌ 会话已过期 - 被重定向到登录页面")
        return True, wait_minutes
    
    # 检查作业是否仍然显示
    final_soup = BeautifulSoup(final_response.text, 'html.parser')
    final_assignments = final_soup.find_all(class_='card')
    print(f"   最终作业数量: {len(final_assignments)}")
    
    if len(final_assignments) == 0:
        print("   ❌ 作业消失了!")
        return True, wait_minutes
    else:
        print("   ✅ 作业仍然显示")
        return False, wait_minutes

def check_auto_refresh():
    """检查页面是否有自动刷新或重定向逻辑"""
    print("\n🔍 检查自动刷新逻辑...")
    
    session = requests.Session()
    
    # 获取登录页面
    login_response = session.get(f"{BASE_URL}/login")
    soup = BeautifulSoup(login_response.text, 'html.parser')
    
    # 检查meta refresh标签
    meta_refresh = soup.find('meta', attrs={'http-equiv': 'refresh'})
    if meta_refresh:
        print(f"   ❌ 发现meta refresh标签: {meta_refresh}")
        return True
    
    # 检查JavaScript重定向
    scripts = soup.find_all('script')
    for script in scripts:
        if script.string and ('setTimeout' in script.string or 'setInterval' in script.string or 
                            'location.href' in script.string or 'window.location' in script.string):
            print(f"   ❌ 发现JavaScript重定向代码")
            print(f"      代码片段: {script.string[:200]}...")
            return True
    
    print("   ✅ 未发现自动刷新或重定向逻辑")
    return False

if __name__ == "__main__":
    print("=" * 60)
    print("诊断会话超时和自动重定向问题")
    print("=" * 60)
    
    # 检查自动刷新逻辑
    has_auto_refresh = check_auto_refresh()
    
    # 测试会话超时
    print("\n" + "=" * 40)
    print("开始会话超时测试...")
    print("=" * 40)
    
    try:
        session_expired, expired_minute = test_session_timeout()
        
        print("\n" + "=" * 60)
        print("诊断结果:")
        print("=" * 60)
        
        if has_auto_refresh:
            print("❌ 问题: 发现自动刷新或重定向逻辑")
        
        if session_expired:
            print(f"❌ 问题: 会话在第{expired_minute}分钟过期")
            print("   可能原因:")
            print("   - Flask会话配置问题")
            print("   - 服务器端会话清理")
            print("   - 负载均衡器会话超时")
        else:
            print("✅ 会话保持正常")
            
        if not has_auto_refresh and not session_expired:
            print("✅ 未发现自动刷新或会话超时问题")
            print("   作业消失可能是其他原因导致")
            
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")