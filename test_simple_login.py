#!/usr/bin/env python3
import requests
import re

def test_login():
    """Test login functionality with CSRF token"""
    session = requests.Session()
    
    print("=== SIMPLE LOGIN TEST WITH CSRF ===")
    
    # Get login page
    print("Getting login page...")
    response = session.get('http://127.0.0.1:5000/login')
    print(f"Login page status: {response.status_code}")
    
    if response.status_code != 200:
        print("Failed to get login page")
        return False
    
    # Extract CSRF token
    csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
    if csrf_match:
        csrf_token = csrf_match.group(1)
        print(f"✅ Found CSRF token: {csrf_token[:10]}...")
    else:
        print("❌ No CSRF token found")
        return False
    
    # Attempt login with correct credentials
    print("Attempting login with CSRF token...")
    login_data = {
        'username': 'admin',  # Use correct username
        'password': 'admin123',  # Use correct password
        'csrf_token': csrf_token
    }
    
    response = session.post('http://127.0.0.1:5000/login', data=login_data)
    print(f"Login POST status: {response.status_code}")
    print(f"Final URL: {response.url}")
    
    # Check if login was successful
    if response.status_code == 200 and 'login' not in response.url.lower():
        print("✅ Login successful!")
        
        # Test access to protected pages
        print("Testing access to protected pages...")
        
        # Test dashboard access
        dashboard_response = session.get('http://127.0.0.1:5000/student_dashboard')
        print(f"Dashboard access: {dashboard_response.status_code}")
        
        # Test view submissions access
        submissions_response = session.get('http://127.0.0.1:5000/view_submissions/1')
        print(f"View submissions access: {submissions_response.status_code}")
        
        return True
    else:
        print("❌ Login failed")
        print(f"First 200 characters: {response.text[:200]}")
        return False

if __name__ == '__main__':
    success = test_login()
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Still having issues")