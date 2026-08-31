#!/usr/bin/env python3
import requests
import re
import sys

def test_login():
    session = requests.Session()
    
    # Get login page
    print("=== Getting login page ===")
    response = session.get('http://127.0.0.1:5000/login')
    print(f'Login page status: {response.status_code}')
    
    # Extract CSRF token
    csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
    if csrf_match:
        csrf_token = csrf_match.group(1)
        print(f'Found CSRF token: {csrf_token[:30]}...')
    else:
        print('No CSRF token found in page')
        # Look for other CSRF patterns
        csrf_match = re.search(r'csrf_token', response.text)
        if csrf_match:
            print('Found csrf_token in page but could not extract value')
        else:
            print('No csrf_token references found in page')
        csrf_token = None
    
    # Try login with correct credentials
    print("\n=== Attempting login with admin/admin123 ===")
    login_data = {
        'username': 'admin',
        'password': 'admin123',
        'csrf_token': csrf_token
    }
    
    response = session.post('http://127.0.0.1:5000/login', data=login_data)
    print(f'Login POST status: {response.status_code}')
    print(f'Final URL: {response.url}')
    print(f'Response length: {len(response.text)}')
    
    # Check response content
    if response.status_code == 500:
        print('Server error - check server logs')
    elif response.status_code == 400:
        print('Bad request - likely CSRF issue')
    
    # Check if we're still on login page
    if 'login' in response.url.lower():
        print('Still on login page - login failed')
        # Look for error messages
        if 'Invalid' in response.text:
            print('Found invalid credentials message')
        if 'error' in response.text.lower():
            print('Found error in response')
        if 'CSRF' in response.text:
            print('Found CSRF error in response')
    else:
        print('Login appears successful - redirected away from login page')
        # Check if we can access a protected page
        dashboard_response = session.get('http://127.0.0.1:5000/student_dashboard')
        print(f'Dashboard access: {dashboard_response.status_code}')
        if dashboard_response.status_code == 200:
            print('Successfully accessed dashboard')
    
    # Check page title
    title_match = re.search(r'<title>([^<]+)</title>', response.text)
    if title_match:
        print(f'Page title: {title_match.group(1).strip()}')
    
    return response.status_code == 200 and 'login' not in response.url.lower()

if __name__ == '__main__':
    success = test_login()
    sys.exit(0 if success else 1)