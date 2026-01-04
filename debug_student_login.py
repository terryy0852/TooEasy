import requests
from bs4 import BeautifulSoup

# Create a session object to persist cookies
session = requests.Session()

login_url = 'http://localhost:5000/login'
dashboard_url = 'http://localhost:5000/student_dashboard'

print("=== Debugging Student Login ===\n")

# Try with student user
student_users = [
    {'username': 'test_user', 'password': 'password123'},
    {'username': 'test_login', 'password': 'password123'}
]

for user in student_users:
    print(f"Testing with user: {user['username']}")
    print("=" * 50)
    
    # Step 1: Reset session
    session = requests.Session()
    
    # Step 2: Login
    response = session.post(login_url, data=user, allow_redirects=False)
    print(f"1. Login POST status: {response.status_code}")
    print(f"   Location: {response.headers.get('Location')}")
    print(f"   Cookies: {session.cookies.get_dict()}")
    
    # Step 3: Follow redirect
    if response.status_code == 302:
        redirect_url = response.headers.get('Location')
        if not redirect_url.startswith('http'):
            redirect_url = f'http://localhost:5000{redirect_url}'
        
        response = session.get(redirect_url)
        print(f"\n2. Dashboard GET status: {response.status_code}")
        print(f"   Final URL: {response.url}")
        
        # Check for errors
        if 'Server Error' in response.text:
            print("\n❌ ERROR: Server Error encountered!")
            soup = BeautifulSoup(response.text, 'html.parser')
            error_element = soup.find(class_='error-message')
            error_msg = error_element.text.strip() if error_element else 'No specific error message'
            print(f"   Error message: {error_msg}")
            break
        elif 'Student Dashboard' in response.text or 'Dashboard' in response.text:
            print("\n✅ SUCCESS: Dashboard loaded successfully!")
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.text.strip() if soup.title else 'No title'
            print(f"   Page title: {title}")
        else:
            print("\n⚠️  WARNING: Unexpected content received")
            print(f"   Response snippet: {response.text[:200]}...")
    
    print()
