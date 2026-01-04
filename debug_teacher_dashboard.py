#!/usr/bin/env python3
"""Debug script to test teacher dashboard access and capture detailed errors"""

import requests
import sqlite3

def debug_teacher_dashboard():
    # Test login as teacher
    session = requests.Session()
    login_data = {
        'username': 'testteacher',
        'password': 'password123'
    }

    print("=== TESTING TEACHER LOGIN ===")
    login_response = session.post('http://127.0.0.1:5000/login', data=login_data)
    print(f"Login status: {login_response.status_code}")

    if login_response.status_code != 200:
        print("❌ Teacher login failed!")
        print(f"Response: {login_response.text[:500]}")
        return False

    print("✅ Teacher login successful!")
    
    # Check if teacher user exists and has correct role
    print("\n=== CHECKING TEACHER USER IN DATABASE ===")
    conn = sqlite3.connect('instance/assignments.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, role FROM user WHERE username = ?", ('testteacher',))
    teacher = cursor.fetchone()
    if teacher:
        print(f"Teacher found: ID {teacher[0]}, username {teacher[1]}, role {teacher[2]}")
    else:
        print("❌ Teacher user not found in database")
        conn.close()
        return False
    
    conn.close()
    
    # Test teacher dashboard access
    print(f"\n=== TESTING TEACHER DASHBOARD ACCESS ===")
    dashboard_response = session.get('http://127.0.0.1:5000/teacher/dashboard')
    print(f"Dashboard status: {dashboard_response.status_code}")
    
    if dashboard_response.status_code == 200:
        print("✅ Teacher dashboard accessible!")
        print(f"Content length: {len(dashboard_response.text)}")
        
        # Check if dashboard contains expected content
        if 'Teacher Dashboard' in dashboard_response.text:
            print("✅ Teacher Dashboard title found")
        else:
            print("❌ Teacher Dashboard title not found")
            
        if 'Assignments' in dashboard_response.text:
            print("✅ Assignments section found")
        else:
            print("❌ Assignments section not found")
            
        return True
    else:
        print("❌ Teacher dashboard access failed!")
        print(f"Response headers: {dict(dashboard_response.headers)}")
        print(f"Response content (first 1000 chars): {dashboard_response.text[:1000]}")
        
        # Check if it's a redirect
        if dashboard_response.status_code in [301, 302, 303, 307, 308]:
            print(f"ℹ️  Redirected to: {dashboard_response.headers.get('Location', 'Unknown')}")
        
        return False

if __name__ == "__main__":
    success = debug_teacher_dashboard()
    if success:
        print("\n🎉 Teacher dashboard is working correctly!")
    else:
        print("\n❌ Teacher dashboard has issues. Check the server logs for detailed error information.")