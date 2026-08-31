import requests
from bs4 import BeautifulSoup

# Base URL of the application
BASE_URL = 'http://127.0.0.1:5000'

def test_admin_registration_and_login():
    print("=== Testing Admin Registration and Login ===")
    
    # Register a new admin user
    print("1. Registering new admin user...")
    register_data = {
        'username': 'testadminfinal',
        'email': 'testadminfinal@example.com',
        'password': 'testadmin123',
        'role': 'admin'
    }
    register_response = requests.post(f'{BASE_URL}/register', data=register_data)
    print(f"   Status code: {register_response.status_code}")
    
    if register_response.status_code == 200:
        print("   ✓ Registration successful")
    else:
        print(f"   ✗ Registration failed: {register_response.status_code}")
        return False
    
    # Login with the new admin user
    print("2. Logging in as admin...")
    login_data = {
        'username': 'testadminfinal',
        'password': 'testadmin123'
    }
    login_response = requests.post(f'{BASE_URL}/login', data=login_data, allow_redirects=True)
    print(f"   Status code: {login_response.status_code}")
    print(f"   Final URL: {login_response.url}")
    
    if login_response.status_code == 200 and '/student_dashboard' in login_response.url:
        print("   ✓ Login successful and redirected to dashboard")
    else:
        print(f"   ✗ Login failed or incorrect redirect: {login_response.status_code} - {login_response.url}")
        return False
    
    # Check if admin dashboard is accessible
    print("3. Verifying admin dashboard content...")
    soup = BeautifulSoup(login_response.content, 'html.parser')
    
    # Check for admin dashboard title
    title = soup.find('h1')
    if title and 'Admin Dashboard' in title.text:
        print("   ✓ Admin dashboard title found")
    else:
        print("   ✗ Admin dashboard title not found")
        return False
    
    # Check for admin section
    admin_section = soup.find('div', class_='admin-section')
    if admin_section:
        print("   ✓ Admin section found on dashboard")
    else:
        print("   ✗ Admin section not found")
        return False
    
    print("\n🎉 All tests passed! The fix is working correctly.")
    return True

if __name__ == "__main__":
    test_admin_registration_and_login()