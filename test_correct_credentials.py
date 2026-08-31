#!/usr/bin/env python3
"""
使用正确的凭据测试登录：Schumacherm2013 / mS93294073
"""

import requests
import re
from bs4 import BeautifulSoup

BASE_URL = "https://tooeasy.onrender.com"

def test_with_correct_credentials():
    """使用正确的用户名和密码测试登录"""
    session = requests.Session()
    
    print("🔍 使用正确凭据测试登录...")
    print("用户名: Schumacherm2013")
    print("密码: mS93294073")
    
    # 1. 访问登录页面获取初始Cookie
    print("\n1. 获取登录页面...")
    response = session.get(f"{BASE_URL}/login")
    print(f"   状态: {response.status_code}")
    print(f"   初始Cookie: {dict(session.cookies)}")
    
    # 2. 使用正确凭据登录
    print("\n2. 使用正确凭据登录...")
    login_data = {
        'username': 'Schumacherm2013',
        'password': 'mS93294073'
    }
    
    response = session.post(f"{BASE_URL}/login", data=login_data)
    print(f"   登录状态: {response.status_code}")
    print(f"   重定向到: {response.url}")
    print(f"   登录后Cookie: {dict(session.cookies)}")
    
    # 3. 检查是否成功登录
    if "student_dashboard" in response.url or "暂无可用作业" in response.text:
        print("✅ 可能登录成功")
        
        # 分析页面内容
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 检查页面标题
        title = soup.find('title')
        if title:
            print(f"   页面标题: {title.text}")
        
        # 检查特定文本
        if "暂无可用作业" in response.text:
            print("   📝 找到'暂无可用作业'提示")
        if "Login" in response.text:
            print("   🔐 找到登录相关文本")
            
        # 检查是否有欢迎消息或用户信息
        welcome_text = soup.find(string=re.compile(r'欢迎|Welcome'))
        if welcome_text:
            print(f"   欢迎消息: {welcome_text}")
    else:
        print("❌ 登录可能失败")
        
        # 检查是否有错误消息
        soup = BeautifulSoup(response.text, 'html.parser')
        error_msg = soup.find(class_=re.compile(r'error|message-error'))
        if error_msg:
            print(f"   错误消息: {error_msg.text}")
    
    # 4. 测试访问学生仪表板
    print("\n3. 测试直接访问学生仪表板...")
    response = session.get(f"{BASE_URL}/student_dashboard")
    print(f"   状态: {response.status_code}")
    print(f"   实际URL: {response.url}")
    
    # 5. 检查页面内容
    if response.status_code == 200:
        if "student_dashboard" in response.url:
            print("✅ 成功访问学生仪表板")
            
            # 分析作业显示情况
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找作业相关元素
            assignments = soup.find_all(class_=re.compile(r'assignment|card|table'))
            print(f"   找到 {len(assignments)} 个可能包含作业的元素")
            
            # 检查特定文本
            if "暂无可用作业" in response.text:
                print("   📝 仪表板显示: 暂无可用作业")
            else:
                print("   🔍 仪表板内容需要进一步分析")
                
            # 保存内容供检查
            with open('schumacher_dashboard.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("   已保存仪表板内容到 schumacher_dashboard.html")
        else:
            print("❌ 被重定向到其他页面")
            print(f"   最终页面: {response.url}")
    
    # 6. 测试其他受保护页面
    print("\n4. 测试其他页面访问权限...")
    test_routes = ['/', '/change_password', '/view_assignment/1']
    
    for route in test_routes:
        try:
            resp = session.get(f"{BASE_URL}{route}")
            status = resp.status_code
            redirected = "是" if resp.url != f"{BASE_URL}{route}" else "否"
            print(f"   {route}: 状态{status}, 重定向{redirected}")
        except Exception as e:
            print(f"   {route}: 错误 - {e}")

if __name__ == "__main__":
    test_with_correct_credentials()