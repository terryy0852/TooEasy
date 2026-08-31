import requests
from bs4 import BeautifulSoup
import sys

BASE_URL = 'http://127.0.0.1:5000'

def main():
    # Create a session to persist cookies
    session = requests.Session()
    
    # Step 1: Register a new admin user
    print("1. Registering new admin user...")
    register_data = {
        'username': 'testadmin',
        'email': 'testadmin@example.com',
        'password': 'testadmin123',
        'role': 'admin'
    }
    
    register_response = session.post(f'{BASE_URL}/register', data=register_data)
    print(f"   Status code: {register_response.status_code}")
    print(f"   Response: {register_response.text[:200]}...")
    
    # Step 2: Log in with the new admin user
    print("\n2. Logging in as admin...")
    login_data = {
        'username': 'testadmin',
        'password': 'testadmin123'
    }
    
    try:
        login_response = session.post(f'{BASE_URL}/login', data=login_data, allow_redirects=True)
        print(f"   Status code: {login_response.status_code}")
        print(f"   Final URL: {login_response.url}")
        print(f"   Response length: {len(login_response.text)} bytes")
        
        # Check if we got an internal server error
        if login_response.status_code == 500:
            print("   ❌ INTERNAL SERVER ERROR!")
            print(f"   Error details: {login_response.text}")
        elif 'student_dashboard' in login_response.url:
            print("   ✓ Successfully logged in and redirected to dashboard")
            
            # Check the dashboard content
            soup = BeautifulSoup(login_response.text, 'html.parser')
            title = soup.find('title')
            if title:
                print(f"   Dashboard title: {title.text}")
            
            # Check if admin options are present
            admin_section = soup.find(class_='admin-section')
            if admin_section:
                print("   ✓ Admin section found on dashboard")
                manage_users_link = admin_section.find('a', href=lambda h: h and 'admin_users' in h)
                if manage_users_link:
                    print("   ✓ 'Manage Users' link found")
            
        else:
            print("   ? Unexpected redirect or response")
            print(f"   Response snippet: {login_response.text[:300]}...")
            
    except Exception as e:
        print(f"   Error during login: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()