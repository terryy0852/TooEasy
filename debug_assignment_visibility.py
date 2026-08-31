#!/usr/bin/env python3
"""
调试脚本：检查为什么学生看不到作业
1. 模拟学生登录
2. 检查仪表板内容
3. 分析作业分配逻辑
"""

import requests
from bs4 import BeautifulSoup
import re

BASE_URL = "https://tooeasy.onrender.com"

def debug_student_assignment_visibility():
    """调试学生作业可见性问题"""
    session = requests.Session()
    
    print("🔍 开始调试学生作业可见性问题...")
    
    # 1. 登录
    print("\n1. 尝试学生登录...")
    login_data = {
        'username': 'test_student',
        'password': 'test_password'
    }
    
    response = session.post(f"{BASE_URL}/login", data=login_data)
    print(f"   登录状态: {response.status_code}")
    print(f"   重定向到: {response.url}")
    
    # 检查是否真的登录成功
    if "student_dashboard" in response.url or "暂无可用作业" in response.text:
        print("✅ 登录成功 - 检测到学生仪表板或'暂无可用作业'提示")
        
        # 2. 分析仪表板内容
        print("\n2. 分析仪表板内容...")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找特定的中文提示
        no_assignments_text = soup.find(string=re.compile(r'暂无可用作业'))
        if no_assignments_text:
            print("   📝 找到提示: '暂无可用作业'")
            # 查看上下文
            parent_element = no_assignments_text.parent
            print(f"   提示所在元素: {parent_element.name}")
            print(f"   完整提示内容: {str(parent_element)[:100]}...")
        
        # 检查是否有作业相关的元素但被隐藏
        assignment_elements = soup.find_all(class_=re.compile(r'assignment|作业|task'))
        print(f"   找到 {len(assignment_elements)} 个作业相关元素")
        
        for i, elem in enumerate(assignment_elements[:3]):  # 只显示前3个
            print(f"   元素 {i+1}: {elem.name} class='{elem.get('class', [])}'")
        
        # 3. 检查页面标题和结构
        title = soup.find('title')
        if title:
            print(f"   页面标题: {title.text}")
        
        # 4. 检查导航栏 - 确认用户角色
        nav_links = soup.find_all('a', href=True)
        student_links = [link for link in nav_links if 'student' in link['href']]
        tutor_links = [link for link in nav_links if 'tutor' in link['href']]
        
        print(f"   学生相关链接: {len(student_links)} 个")
        print(f"   导师相关链接: {len(tutor_links)} 个")
        
        # 5. 保存详细内容供分析
        with open('student_dashboard_detailed.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("   已保存详细HTML内容到 student_dashboard_detailed.html")
        
    else:
        print("❌ 登录可能未成功")
        print(f"   页面内容摘要: {response.text[:200]}...")

    # 6. 尝试访问其他页面确认认证状态
    print("\n3. 测试其他受保护页面...")
    test_routes = ['/student_dashboard', '/view_assignment/1', '/change_password']
    
    for route in test_routes:
        try:
            resp = session.get(f"{BASE_URL}{route}")
            status = resp.status_code
            redirected = "是" if resp.url != f"{BASE_URL}{route}" else "否"
            print(f"   {route}: 状态{status}, 重定向{redirected}")
        except Exception as e:
            print(f"   {route}: 错误 - {e}")

if __name__ == "__main__":
    debug_student_assignment_visibility()