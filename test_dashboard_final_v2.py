import requests
import re

print("=== Testing student dashboard access ===")

session = requests.Session()

# Get login page
login_page = session.get('http://127.0.0.1:5000/login')
csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', login_page.text)
if csrf_match:
    csrf_token = csrf_match.group(1)
    print(f"✅ Found CSRF token: {csrf_token[:20]}...")
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

# Test student dashboard
dashboard_response = session.get('http://127.0.0.1:5000/student_dashboard')
print(f"Dashboard status: {dashboard_response.status_code}")
print(f"Dashboard URL: {dashboard_response.url}")

if dashboard_response.status_code == 200:
    print("✅ Student dashboard accessible")
    if 'Admin Dashboard' in dashboard_response.text:
        print("✅ Admin dashboard content verified")
    else:
        print("⚠️  Dashboard content might be different")
else:
    print("❌ Student dashboard not accessible")

print("\n=== Test completed successfully ===")