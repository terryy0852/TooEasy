#!/usr/bin/env python3
"""
实时监控会话状态 - 每60秒检查一次会话是否仍然有效
"""

import requests
import time
from datetime import datetime

def monitor_session():
    print("🔍 实时监控会话状态")
    print("=" * 50)
    print("监控将每60秒检查一次会话状态")
    print("按 Ctrl+C 停止监控")
    print("=" * 50)
    
    # 登录信息
    login_url = "https://tooeasy.onrender.com/login"
    dashboard_url = "https://toasy.onrender.com/student_dashboard"
    username = "Schumacherm2013"
    password = "123456"  # 请使用实际密码
    
    # 创建会话
    session = requests.Session()
    
    # 登录
    print(f"🔄 登录用户: {username}")
    login_data = {
        'username': username,
        'password': password
    }
    
    try:
        response = session.post(login_url, data=login_data, timeout=10)
        if response.status_code == 200 and 'student_dashboard' in response.url:
            print("✅ 登录成功并重定向到仪表板")
        else:
            print(f"⚠ 登录状态: {response.status_code}, URL: {response.url}")
            return
            
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return
    
    # 开始监控
    check_count = 0
    session_valid = True
    
    try:
        while session_valid:
            check_count += 1
            current_time = datetime.now().strftime('%H:%M:%S')
            
            try:
                # 检查仪表板访问
                response = session.get(dashboard_url, timeout=10)
                
                if response.status_code == 200:
                    if 'login' in response.url.lower():
                        print(f"❌ [{current_time}] 检查 #{check_count}: 会话已过期!")
                        session_valid = False
                    else:
                        # 检查作业是否显示
                        if '中文詞句訓練' in response.text:
                            print(f"✅ [{current_time}] 检查 #{check_count}: 会话有效, 作业显示正常")
                        else:
                            print(f"⚠ [{current_time}] 检查 #{check_count}: 会话有效, 但未检测到作业")
                else:
                    print(f"⚠ [{current_time}] 检查 #{check_count}: 状态码 {response.status_code}")
                    
            except Exception as e:
                print(f"❌ [{current_time}] 检查 #{check_count}: 异常 - {e}")
                session_valid = False
            
            # 等待60秒
            if session_valid:
                time.sleep(60)
                
    except KeyboardInterrupt:
        print("\n⏹️ 监控被用户中断")
    
    print("\n" + "=" * 50)
    print("监控结束")
    
    if not session_valid:
        print("❌ 会话在监控期间过期")
        print("可能原因:")
        print("- 会话持久性配置未生效")
        print("- Render.com平台限制")
        print("- 需要重新部署应用")
    else:
        print("✅ 会话在整个监控期间保持有效")

if __name__ == "__main__":
    monitor_session()