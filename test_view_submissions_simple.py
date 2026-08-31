import requests
import re

print("=== Testing view_submissions endpoint ===")

session = requests.Session()

# Get login page
login_page = session.get('http://127.0.0.1:5000/login')
print(f"Login page status: {login_page.status_code}")

# Extract CSRF token
csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', login_page.text)
if csrf_match:
    csrf_token = csrf_match.group(1)
    print(f"Found CSRF token: {csrf_token[:20]}...")
else:
    print("❌ CSRF token not found")
    exit(1)

# Login
login_response = session.post('http://127.0.0.1:5000/login', data={
    'csrf_token': csrf_token,
    'username': 'admin',
    'password': 'admin123'
})
print(f"Login POST status: {login_response.status_code}")
print(f"Login final URL: {login_response.url}")

# Test view_submissions
print("\n=== Testing view_submissions/1 ===")
response = session.get('http://127.0.0.1:5000/view_submissions/1')
print(f"Status: {response.status_code}")
print(f"URL: {response.url}")

if response.status_code == 500:
    print('❌ 500 Error - Full Response:')
    print(response.text)
else:
    print('✅ Success - Response preview:')
    print(response.text[:500])
    print("...")

print("\n=== Test completed ===")