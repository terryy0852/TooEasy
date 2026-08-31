import requests
import re

# Test the updated view_submissions page
BASE_URL = "http://127.0.0.1:5000"

# Login as admin
login_data = {
    'username': 'admin',
    'password': 'admin123'
}

session = requests.Session()

# Get login page to extract CSRF token
login_page = session.get(f"{BASE_URL}/login")
csrf_token = re.search(r'name="csrf_token" value="([^"]+)"', login_page.text).group(1)
login_data['csrf_token'] = csrf_token

# Login
login_response = session.post(f"{BASE_URL}/login", data=login_data)
print(f"Login status: {login_response.status_code}")

# Test view_submissions for assignment 1
response = session.get(f"{BASE_URL}/view_submissions/1")
print(f"View submissions status: {response.status_code}")

if response.status_code == 200:
    print("✅ View submissions page loaded successfully!")
    
    # Check if the page contains the new modal functionality
    if 'showSubmissionModal' in response.text:
        print("✅ Modal functionality found!")
    else:
        print("❌ Modal functionality not found")
    
    if 'submission-iframe' in response.text:
        print("✅ Iframe for HTML content found!")
    else:
        print("❌ Iframe for HTML content not found")
        
    if 'View Answer' in response.text:
        print("✅ 'View Answer' button found!")
    else:
        print("❌ 'View Answer' button not found")
        
    # Save the response for manual inspection
    with open('view_submissions_final.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print("📄 HTML saved to view_submissions_final.html for inspection")
else:
    print(f"❌ Failed to load view submissions page: {response.status_code}")
    print(response.text[:500])