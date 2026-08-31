import requests
import os
import sys
import sqlite3
from bs4 import BeautifulSoup

# Add the project directory to Python path so we can import the app
sys.path.append(os.path.abspath('.'))

login_url = 'http://localhost:5000/login'

print("=== Debugging Complete Login Flow ===\n")

# First, let's create test users if they don't exist
print("1. Creating test users...")

db_path = os.path.join('instance', 'assignments.db')

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create test users
    test_users = [
        ('test_user', 'password123', 'student@example.com', 'student'),
        ('test_teacher', 'password123', 'teacher@example.com', 'teacher'),
        ('test_login', 'password123', 'login@example.com', 'student')
    ]
    
    # Check if users exist first
    cursor.execute("SELECT username FROM user")
    existing_users = [row[0] for row in cursor.fetchall()]
    
    for username, password, email, role in test_users:
        if username not in existing_users:
            # Hash the password (we'll use the same hashing method as in the app)
            from werkzeug.security import generate_password_hash
            hashed_password = generate_password_hash(password)
            
            cursor.execute(
                "INSERT INTO user (username, password, email, role) VALUES (?, ?, ?, ?)",
                (username, hashed_password, email, role)
            )
            print(f"  - Created user: {username} ({role})")
        else:
            print(f"  - User already exists: {username}")
    
    conn.commit()
    conn.close()
    print("Test users created successfully!")
else:
    print(f"Database not found at: {db_path}")
    sys.exit(1)

print("\n2. Testing login with test users...")

# Test cases with correct credentials
test_cases = [
    {'username': 'test_user', 'password': 'password123', 'expected_role': 'student'},
    {'username': 'test_teacher', 'password': 'password123', 'expected_role': 'teacher'},
    {'username': 'test_login', 'password': 'password123', 'expected_role': 'student'}
]

session = requests.Session()

for test_case in test_cases:
    print(f"\nTesting {test_case['username']}/{test_case['password']}...")
    print("=" * 40)
    
    # Clear any existing cookies
    session.cookies.clear()
    
    # Test login
    login_data = {
        'username': test_case['username'],
        'password': test_case['password']
    }
    
    # Send login request
    response = session.post(login_url, data=login_data, allow_redirects=True)
    
    print(f"Status code: {response.status_code}")
    print(f"Final URL: {response.url}")
    
    # Check if we're on dashboard
    if 'dashboard' in response.url:
        print(f"✓ Successfully logged in! Redirected to dashboard.")
        
        # Check page content
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else "No title"
        print(f"Page title: {title}")
        
        # Look for welcome message
        welcome_tag = soup.find('h1')
        if welcome_tag:
            print(f"Welcome message: {welcome_tag.text.strip()}")
        
    else:
        print(f"✗ Login failed. Still on: {response.url}")
        
        # Check for error messages
        error_div = soup.find(class_='error-message')
        if error_div:
            print(f"Error message: {error_div.text.strip()}")
        
        # Print page content snippet
        print("Page content snippet:")
        print(response.text[:500] + "...")

print("\n3. Testing logout functionality...")
print("=" * 40)

# Use the session that just logged in
logout_url = 'http://localhost:5000/logout'
logout_response = session.get(logout_url, allow_redirects=True)

print(f"Logout status: {logout_response.status_code}")
print(f"Final URL: {logout_response.url}")

if '/login' in logout_response.url:
    print("✓ Successfully logged out!")
else:
    print("✗ Logout failed")

print("\n4. Testing direct dashboard access after logout...")
print("=" * 40)

# Try to access dashboard directly after logout
dashboard_url = 'http://localhost:5000/student_dashboard'
dashboard_response = session.get(dashboard_url, allow_redirects=True)

print(f"Direct dashboard access status: {dashboard_response.status_code}")
print(f"Final URL: {dashboard_response.url}")

if '/login' in dashboard_response.url:
    print("✓ Correctly redirected to login page - session properly invalidated")
else:
    print("✗ Still have dashboard access after logout - session issue!")
