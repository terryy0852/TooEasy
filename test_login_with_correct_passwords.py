import requests
import os
import sys
from bs4 import BeautifulSoup

print("=== Testing Login with Correct Passwords ===\n")

# Test cases with correct credentials
test_cases = [
    {'username': 'admin', 'password': 'admin123', 'role': 'admin'},
    {'username': 'teststudent', 'password': 'password123', 'role': 'student'}
]

for test_case in test_cases:
    print(f"Testing {test_case['username']} ({test_case['role']})...")
    print("=" * 50)
    
    # Create a new session for each test
    session = requests.Session()
    login_url = 'http://localhost:5000/login'
    
    # Step 1: Access login page
    print("1. Accessing login page...")
    response = session.get(login_url)
    print(f"   Status: {response.status_code}")
    
    # Step 2: Attempt login
    print("2. Attempting login...")
    login_data = {
        'username': test_case['username'],
        'password': test_case['password']
    }
    
    login_response = session.post(login_url, data=login_data, allow_redirects=False)
    print(f"   Login POST status: {login_response.status_code}")
    print(f"   Redirect location: {login_response.headers.get('Location', 'None')}")
    
    # Step 3: Check if login was successful (302 redirect)
    if login_response.status_code == 302:
        redirect_url = login_response.headers.get('Location')
        if redirect_url:
            print(f"3. Following redirect to: {redirect_url}")
            dashboard_response = session.get(f'http://localhost:5000{redirect_url}')
            print(f"   Dashboard status: {dashboard_response.status_code}")
            print(f"   Final URL: {dashboard_response.url}")
            
            # Check page content
            soup = BeautifulSoup(dashboard_response.text, 'html.parser')
            title = soup.title.string if soup.title else "No title"
            print(f"   Page title: {title}")
            
            # Look for welcome message
            welcome_h1 = soup.find('h1')
            if welcome_h1:
                print(f"   Welcome message: {welcome_h1.text.strip()}")
            
            # Check for specific content
            if 'Welcome' in dashboard_response.text or 'Dashboard' in dashboard_response.text:
                print("   ✅ Dashboard content found - login successful!")
            else:
                print("   ❌ No dashboard content found")
                
            # Check for error messages
            error_div = soup.find(class_='error')
            if error_div:
                print(f"   Error message: {error_div.text.strip()}")
        
        # Step 4: Test direct dashboard access
        print("4. Testing direct dashboard access...")
        direct_response = session.get('http://localhost:5000/student_dashboard')
        print(f"   Direct access status: {direct_response.status_code}")
        print(f"   Final URL: {direct_response.url}")
        
        if direct_response.status_code == 200 and 'dashboard' in direct_response.url:
            print("   ✅ Direct dashboard access successful!")
        else:
            print("   ❌ Direct dashboard access failed")
            
        # Step 5: Test logout
        print("5. Testing logout...")
        logout_response = session.get('http://localhost:5000/logout')
        print(f"   Logout status: {logout_response.status_code}")
        print(f"   Final URL: {logout_response.url}")
        
        if '/login' in logout_response.url:
            print("   ✅ Logout successful!")
        else:
            print("   ❌ Logout failed")
            
    else:
        # Login failed - check for error messages
        print("3. Login failed - checking response...")
        soup = BeautifulSoup(login_response.text, 'html.parser')
        
        # Check for flash messages
        flash_div = soup.find(class_='flash')
        if flash_div:
            print(f"   Flash message: {flash_div.text.strip()}")
        
        # Check for error messages
        error_div = soup.find(class_='error')
        if error_div:
            print(f"   Error message: {error_div.text.strip()}")
        
        print("   Page content snippet:")
        print(login_response.text[:300] + "...")
    
    print("\n" + "=" * 50 + "\n")

print("=== Testing complete ===")