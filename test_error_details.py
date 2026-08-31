import requests
import re

print("=== Testing view_submissions/2 to see error details ===")

session = requests.Session()

# Login
login_page = session.get('http://127.0.0.1:5000/login')
csrf_token = re.search(r'name="csrf_token" value="([^"]+)"', login_page.text).group(1)
session.post('http://127.0.0.1:5000/login', data={
    'csrf_token': csrf_token,
    'username': 'admin',
    'password': 'admin123'
})

# Test view_submissions/2
response = session.get('http://127.0.0.1:5000/view_submissions/2')
print(f"Status: {response.status_code}")
print(f"URL: {response.url}")
print(f"Response length: {len(response.text)}")
print("Full response:")
print(response.text)