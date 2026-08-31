#!/usr/bin/env python3
"""
Manual login test script to help diagnose login issues
"""

import requests
from urllib.parse import urljoin

# Test the login functionality manually
def test_login_manual():
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    print("=== Manual Login Test ===")
    print("Testing login with different credentials...")
    print()
    
    # Test credentials
    test_cases = [
        ("admin", "admin123", "admin"),
        ("teststudent", "password123", "student"),
        ("test_user", "password123", "student"),
    ]
    
    for username, password, role in test_cases:
        print(f"Testing: {username} ({role})")
        print(f"Password: {password}")
        
        # Get login page first
        try:
            login_page = session.get(urljoin(base_url, "/login"))
            print(f"  Login page status: {login_page.status_code}")
            
            # Attempt login
            login_data = {
                "username": username,
                "password": password
            }
            
            login_response = session.post(urljoin(base_url, "/login"), 
                                         data=login_data, 
                                         allow_redirects=False)
            
            print(f"  Login POST status: {login_response.status_code}")
            
            if login_response.status_code == 302:
                redirect_location = login_response.headers.get('Location', '')
                print(f"  Redirect location: {redirect_location}")
                
                # Follow redirect
                dashboard_response = session.get(urljoin(base_url, redirect_location))
                print(f"  Dashboard status: {dashboard_response.status_code}")
                
                if dashboard_response.status_code == 200:
                    # Check if we're actually logged in
                    if "Admin Dashboard" in dashboard_response.text or "Student Dashboard" in dashboard_response.text:
                        print(f"  ✅ SUCCESS: Logged in as {username}")
                    else:
                        print(f"  ❌ FAILED: Not properly logged in")
                        print(f"  Page content preview: {dashboard_response.text[:200]}...")
                else:
                    print(f"  ❌ FAILED: Could not access dashboard")
            else:
                print(f"  ❌ FAILED: No redirect after login")
                print(f"  Response content: {login_response.text[:200]}...")
                
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
        
        print("-" * 50)
        
        # Clear session for next test
        session = requests.Session()

if __name__ == "__main__":
    test_login_manual()