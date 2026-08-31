#!/usr/bin/env python3
"""
检查会话和Cookie状态的详细测试
"""

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://tooeasy.onrender.com"

def check_session_details():
    """详细检查会话和Cookie状态"""
    session = requests.Session()
    
    print("🔍 详细会话检查...")
    
    # 1. 首次访问登录页面
    print("\n1. 首次访问登录页面:")
    response = session.get(f"{BASE_URL}/login")
    print(f"   状态: {response.status_code}")
    print(f"   Cookies: {dict(session.cookies)}")
    
    # 2. 尝试登录
    print("\n2. 尝试登录:")
    login_data = {
        'username': 'test_student',
        'password': 'test_password'
    }
    
    response = session.post(f"{BASE_URL}/login", data=login_data)
    print(f"   登录状态: {response.status_code}")
    print(f"   重定向到: {response.url}")
    print(f"   登录后Cookies: {dict(session.cookies)}")
    
    # 3. 检查响应头
    print(f"   响应头 - Set-Cookie: {response.headers.get('Set-Cookie', 'None')}")
    
    # 4. 手动尝试访问学生仪表板
    print("\n3. 手动访问学生仪表板:")
    response = session.get(f"{BASE_URL}/student_dashboard")
    print(f"   状态: {response.status_code}")
    print(f"   实际URL: {response.url}")
    print(f"   当前Cookies: {dict(session.cookies)}")
    
    # 5. 检查页面内容
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 检查是否有登录表单（说明被重定向回登录）
        login_form = soup.find('form', {'method': 'POST'})
        if login_form:
            print("   ❌ 仍然在登录页面")
        else:
            print("   ✅ 可能在仪表板页面")
            
        # 检查页面标题
        title = soup.find('title')
        if title:
            print(f"   页面标题: {title.text}")
            
        # 检查特定文本
        if "暂无可用作业" in response.text:
            print("   📝 找到'暂无可用作业'提示")
        elif "Login" in response.text:
            print("   🔐 找到登录相关文本")
    
    # 6. 测试index页面（应该重定向到正确仪表板）
    print("\n4. 测试首页重定向:")
    response = session.get(BASE_URL)
    print(f"   状态: {response.status_code}")
    print(f"   重定向到: {response.url}")

if __name__ == "__main__":
    check_session_details()