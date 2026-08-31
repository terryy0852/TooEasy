import requests
from bs4 import BeautifulSoup

# Create a session object to persist cookies
session = requests.Session()

login_url = 'http://localhost:5000/login'
dashboard_url = 'http://localhost:5000/student_dashboard'

print("=== Debugging Login and Session Issue ===\n")

# Step 1: Check login page
print("1. Accessing login page...")
response = session.get(login_url)
print(f"   Status code: {response.status_code}")
print(f"   Cookies after GET: {session.cookies.get_dict()}")

# Step 2: Attempt login
print("\n2. Attempting login with admin credentials...")
data = {
    'username': 'admin',
    'password': 'admin123'
}
response = session.post(login_url, data=data, allow_redirects=False)
print(f"   Status code: {response.status_code}")
print(f"   Location header: {response.headers.get('Location')}")
print(f"   Cookies after login POST: {session.cookies.get_dict()}")

# Step 3: Follow redirect if any
if response.status_code == 302:
    redirect_url = response.headers.get('Location')
    if not redirect_url.startswith('http'):
        redirect_url = f'http://localhost:5000{redirect_url}'
    
    print(f"\n3. Following redirect to: {redirect_url}")
    response = session.get(redirect_url)
    print(f"   Status code: {response.status_code}")
    print(f"   Final URL: {response.url}")
    
    # Check if we got the error page
    if 'Server Error' in response.text:
        print("\n❌ ERROR: Server Error page received!")
        # Look for error details in the response
        soup = BeautifulSoup(response.text, 'html.parser')
        error_msg = soup.find('p').text.strip() if soup.find('p') else 'No specific error message'
        print(f"   Error message: {error_msg}")
        
        # Print more context around the error
        print("\n   Response content (first 500 chars):")
        print(response.text[:500])
        
    elif '/login' in response.url and 'next=' in response.url:
        print("\n❌ ISSUE: Redirected back to login page - session not maintained!")
        print(f"   Full URL: {response.url}")
        
    else:
        print("\n✅ SUCCESS: Dashboard loaded!")
        print(f"   Page title: {BeautifulSoup(response.text, 'html.parser').title.text if BeautifulSoup(response.text, 'html.parser').title else 'No title'}")
        
        # Check what's in the dashboard
        soup = BeautifulSoup(response.text, 'html.parser')
        welcome_msg = soup.find('h2')
        if welcome_msg:
            print(f"   Welcome message: {welcome_msg.text.strip()}")
