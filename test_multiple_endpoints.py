import requests
import re

print("=== Testing multiple endpoints ===")

session = requests.Session()

# Get login page
login_page = session.get('http://127.0.0.1:5000/login')
csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', login_page.text)
csrf_token = csrf_match.group(1)

# Login
session.post('http://127.0.0.1:5000/login', data={
    'csrf_token': csrf_token,
    'username': 'admin',
    'password': 'admin123'
})

# Test various endpoints
endpoints = [
    '/view_submissions/1',
    '/view_submissions/2',
    '/view_submissions/3',
    '/view_submissions/999',  # Non-existent assignment
]

for endpoint in endpoints:
    print(f"\n=== Testing {endpoint} ===")
    response = session.get(f'http://127.0.0.1:5000{endpoint}')
    print(f"Status: {response.status_code}")
    print(f"URL: {response.url}")
    
    if response.status_code == 500:
        print('❌ 500 Error')
    elif response.status_code == 404:
        print('❌ 404 Not Found')
    else:
        print('✅ Success')
        # Check if it contains expected content
        if 'submissions' in response.text.lower():
            print('Contains submissions content')
        else:
            print('Response preview:')
            print(response.text[:200])

print("\n=== All tests completed ===")