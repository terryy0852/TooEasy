import requests
import os
import sys
from bs4 import BeautifulSoup

print("=== Debugging Authentication Flow ===\n")

# Test the complete login flow
login_url = 'http://localhost:5000/login'

# Create a session to maintain cookies
session = requests.Session()

print("1. Testing login page access...")
response = session.get(login_url)
print(f"   Status: {response.status_code}")
print(f"   URL: {response.url}")

# Check if we're already logged in
if 'dashboard' in response.url:
    print("   Already logged in! Testing logout first...")
    logout_response = session.get('http://localhost:5000/logout')
    print(f"   Logout status: {logout_response.status_code}")
    
    # Try login page again
    response = session.get(login_url)
    print(f"   Login page after logout: {response.status_code}")

print("\n2. Testing login with admin credentials...")
login_data = {
    'username': 'admin',
    'password': 'admin'
}

# Send login request
login_response = session.post(login_url, data=login_data, allow_redirects=False)
print(f"   Login POST status: {login_response.status_code}")
print(f"   Redirect location: {login_response.headers.get('Location', 'None')}")

# Check cookies
print(f"   Session cookies: {session.cookies.get_dict()}")

# Follow redirect if present
if login_response.status_code == 302:
    redirect_url = login_response.headers.get('Location')
    if redirect_url:
        print(f"\n3. Following redirect to: {redirect_url}")
        dashboard_response = session.get(f'http://localhost:5000{redirect_url}')
        print(f"   Dashboard status: {dashboard_response.status_code}")
        print(f"   Final URL: {dashboard_response.url}")
        
        # Check page content
        soup = BeautifulSoup(dashboard_response.text, 'html.parser')
        title = soup.title.string if soup.title else "No title"
        print(f"   Page title: {title}")
        
        # Look for error messages
        error_div = soup.find(class_='error')
        if error_div:
            print(f"   Error message: {error_div.text.strip()}")
        
        # Look for welcome message
        welcome_h1 = soup.find('h1')
        if welcome_h1:
            print(f"   Welcome message: {welcome_h1.text.strip()}")
        
        # Check for specific content that indicates successful login
        if 'Welcome' in dashboard_response.text or 'Dashboard' in dashboard_response.text:
            print("   ✓ Dashboard content found - login successful!")
        else:
            print("   ✗ No dashboard content found")
            print("   Page content snippet:")
            print(dashboard_response.text[:500] + "...")
else:
    print("\n3. No redirect - checking response content...")
    soup = BeautifulSoup(login_response.text, 'html.parser')
    
    # Check for error messages
    error_div = soup.find(class_='error')
    if error_div:
        print(f"   Error message: {error_div.text.strip()}")
    
    # Check for flash messages
    flash_div = soup.find(class_='flash')
    if flash_div:
        print(f"   Flash message: {flash_div.text.strip()}")
    
    print("   Page content snippet:")
    print(login_response.text[:500] + "...")

print("\n4. Testing direct dashboard access...")
dashboard_response = session.get('http://localhost:5000/student_dashboard')
print(f"   Direct dashboard status: {dashboard_response.status_code}")
print(f"   Final URL: {dashboard_response.url}")

if dashboard_response.status_code == 200:
    print("   ✓ Direct dashboard access successful!")
else:
    print("   ✗ Direct dashboard access failed")

print("\n=== Debugging complete ===")