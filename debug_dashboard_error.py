#!/usr/bin/env python3
"""
Debug script to test student_dashboard functionality
"""

import requests
from bs4 import BeautifulSoup

BASE_URL = "http://127.0.0.1:5000"

def debug_student_dashboard():
    print("🔍 Debugging student dashboard issue...")
    
    session = requests.Session()
    
    try:
        # 1. Login first
        print("\n1. Logging in...")
        login_page = session.get(f"{BASE_URL}/login")
        soup = BeautifulSoup(login_page.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'}).get('value', '')
        
        login_data = {
            'username': 'admin',
            'password': 'admin123',
            'csrf_token': csrf_token
        }
        
        login_response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
        print(f"   Login status: {login_response.status_code}")
        
        if login_response.status_code != 302:
            print("   ❌ Login failed")
            return
        
        # 2. Try to access student dashboard directly
        print("\n2. Accessing student dashboard...")
        dashboard_response = session.get(f"{BASE_URL}/student_dashboard")
        print(f"   Dashboard status: {dashboard_response.status_code}")
        print(f"   Dashboard URL: {dashboard_response.url}")
        
        if dashboard_response.status_code == 500:
            print("   ❌ 500 Internal Server Error")
            print(f"   Response content: {dashboard_response.text[:500]}...")
            
            # Save the error page for analysis
            with open('dashboard_error.html', 'w', encoding='utf-8') as f:
                f.write(dashboard_response.text)
            print("   Saved error page to dashboard_error.html")
            
        elif dashboard_response.status_code == 200:
            print("   ✅ Dashboard loaded successfully")
            
            # Check content
            soup = BeautifulSoup(dashboard_response.text, 'html.parser')
            title = soup.find('title')
            if title:
                print(f"   Page title: {title.text}")
            
            # Look for error messages
            flash_messages = soup.find_all('div', class_='flash')
            if flash_messages:
                for msg in flash_messages:
                    print(f"   Flash message: {msg.text.strip()}")
            
        else:
            print(f"   ⚠️  Unexpected status: {dashboard_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_student_dashboard()