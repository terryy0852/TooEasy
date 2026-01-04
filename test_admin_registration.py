import requests
import time

# Test script to reproduce admin registration and login error
BASE_URL = 'http://127.0.0.1:5000'

print("=== Testing Admin Registration and Login ===")

# Register a new admin user
try:
    register_data = {
        'username': 'newadminuser',
        'email': 'newadmin@example.com',
        'password': 'newadmin123',
        'role': 'admin'
    }
    
    print("1. Registering new admin user...")
    register_response = requests.post(f'{BASE_URL}/register', data=register_data)
    print(f"   Status code: {register_response.status_code}")
    print(f"   Response: {register_response.text[:200]}...")
    
    if register_response.status_code == 200:
        # Login with the new admin user
        print("\n2. Logging in with new admin user...")
        login_data = {
            'username': 'newadminuser',
            'password': 'newadmin123'
        }
        
        login_response = requests.post(f'{BASE_URL}/login', data=login_data, allow_redirects=True)
        print(f"   Status code: {login_response.status_code}")
        print(f"   Response URL: {login_response.url}")
        print(f"   Response content: {login_response.text[:300]}...")
    
except Exception as e:
    print(f"Error: {e}")

print("\nCheck the Flask debug server logs for detailed error information.")