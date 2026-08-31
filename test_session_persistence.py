#!/usr/bin/env python3
"""
测试会话持久性 - 验证15分钟后会话是否仍然有效
"""

import requests
import time
from datetime import datetime

def test_session_persistence():
    print("🔍 测试会话持久性 - 验证15分钟后会话是否仍然有效")
    print("=" * 60)
    
    # 登录信息
    login_url = "https://tooeasy.onrender.com/login"
    dashboard_url = "https://tooeasy.onrender.com/student_dashboard"
    username = "Schumacherm2013"
    password = "123456"  # 请使用实际密码
    
    # 创建会话
    session = requests.Session()
    
    # 步骤1: 登录
    print(f"1. 登录用户: {username}")
    login_data = {
        'username': username,
        'password': password
    }
    
    try:
        response = session.post(login_url, data=login_data, timeout=10)
        if response.status_code == 200:
            print(f"   ✅ 登录成功 - 状态码: {response.status_code}")
            
            # 检查是否重定向到仪表板
            if 'student_dashboard' in response.url:
                print(f"   ✅ 成功重定向到仪表板")
            else:
                print(f"   ⚠ 重定向到: {response.url}")
        else:
            print(f"   ❌ 登录失败 - 状态码: {response.status_code}")
            return
            
    except Exception as e:
        print(f"   ❌ 登录异常: {e}")
        return
    
    # 步骤2: 初始仪表板检查
    print("\n2. 初始仪表板检查")
    try:
        dashboard_response = session.get(dashboard_url, timeout=10)
        if dashboard_response.status_code == 200:
            print(f"   ✅ 仪表板访问成功 - 状态码: {dashboard_response.status_code}")
            
            # 检查作业数量
            content = dashboard_response.text
            if '中文詞句訓練' in content:
                print("   ✅ 检测到中文作业")
            else:
                print("   ⚠ 未检测到中文作业")
                
        else:
            print(f"   ❌ 仪表板访问失败 - 状态码: {dashboard_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ 仪表板检查异常: {e}")
    
    # 步骤3: 等待15分钟并定期检查
    print(f"\n3. 等待15分钟并定期检查会话状态...")
    print(f"   开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    wait_minutes = 15
    check_interval = 60  # 每60秒检查一次
    total_seconds = wait_minutes * 60
    
    for seconds_elapsed in range(0, total_seconds + 1, check_interval):
        if seconds_elapsed > 0:
            minutes_elapsed = seconds_elapsed // 60
            print(f"   ⏰ 已等待 {minutes_elapsed} 分钟...")
        
        # 检查会话状态
        try:
            check_response = session.get(dashboard_url, timeout=10)
            if check_response.status_code == 200:
                if 'login' in check_response.url.lower():
                    print(f"   ❌ 会话已过期 - 被重定向到登录页面")
                    break
                else:
                    print(f"   ✅ 会话仍然有效 - 状态码: {check_response.status_code}")
            else:
                print(f"   ⚠ 会话检查异常 - 状态码: {check_response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 会话检查异常: {e}")
            break
        
        if seconds_elapsed < total_seconds:
            time.sleep(check_interval)
    
    # 最终检查
    print(f"\n4. 最终检查 (等待完成)")
    print(f"   结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        final_response = session.get(dashboard_url, timeout=10)
        if final_response.status_code == 200:
            if 'login' not in final_response.url.lower():
                print("   🎉 测试成功! 会话在15分钟后仍然有效!")
                print("   ✅ 会话持久性配置正常工作")
            else:
                print("   ❌ 测试失败! 会话已过期")
        else:
            print(f"   ❌ 最终检查失败 - 状态码: {final_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ 最终检查异常: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成!")

if __name__ == "__main__":
    test_session_persistence()