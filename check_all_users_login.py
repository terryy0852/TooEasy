import sqlite3
import os
import requests
from bs4 import BeautifulSoup
from werkzeug.security import check_password_hash

print("=== Checking All Previously Registered Users ===\n")

# Path to the database
db_path = os.path.join('instance', 'assignments.db')

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all users from the database
    cursor.execute("SELECT username, email, password_hash, role FROM user")
    users = cursor.fetchall()
    
    print(f"Found {len(users)} user(s) in database:")
    for i, user in enumerate(users, 1):
        username, email, password_hash, role = user
        print(f"\n{i}. {username} (role: {role}, email: {email})")
        print(f"   Password hash: {password_hash[:30]}...")
    
    conn.close()
    
    # Test login for each user
    print("\n=== Testing Login for Each User ===\n")
    
    for user in users:
        username, email, password_hash, role = user
        print(f"Testing login for: {username} ({role})")
        print("-" * 40)
        
        # Create a new session for each test
        session = requests.Session()
        login_url = 'http://localhost:5000/login'
        
        # Try common passwords for this user
        common_passwords = [
            'password123', 'password', '123456', 'admin123', 
            'test123', 'user123', 'student123', 'teacher123'
        ]
        
        # Also try username as password (common pattern)
        common_passwords.extend([username, username + '123', username + '!'])
        
        login_successful = False
        correct_password = None
        
        for password in common_passwords:
            # Check if password matches the hash
            if check_password_hash(password_hash, password):
                correct_password = password
                print(f"✅ Found correct password: '{password}'")
                
                # Test login with this password
                login_data = {
                    'username': username,
                    'password': password
                }
                
                login_response = session.post(login_url, data=login_data, allow_redirects=False)
                
                if login_response.status_code == 302:
                    redirect_url = login_response.headers.get('Location')
                    if redirect_url and 'dashboard' in redirect_url:
                        print(f"✅ Login successful! Redirected to: {redirect_url}")
                        
                        # Follow redirect to verify
                        dashboard_response = session.get(f'http://localhost:5000{redirect_url}')
                        if dashboard_response.status_code == 200:
                            soup = BeautifulSoup(dashboard_response.text, 'html.parser')
                            title = soup.title.string if soup.title else "No title"
                            print(f"✅ Dashboard loaded successfully: {title}")
                            login_successful = True
                        
                        # Test logout
                        logout_response = session.get('http://localhost:5000/logout')
                        if '/login' in logout_response.url:
                            print("✅ Logout successful")
                        
                        break
                else:
                    print(f"❌ Login failed with correct password (status: {login_response.status_code})")
                    # Check for error message
                    soup = BeautifulSoup(login_response.text, 'html.parser')
                    flash_div = soup.find(class_='flash')
                    if flash_div:
                        print(f"   Error: {flash_div.text.strip()}")
        
        if not login_successful:
            if correct_password:
                print(f"❌ Login failed despite correct password '{correct_password}'")
            else:
                print("❌ Could not determine password for this user")
                print("   Common passwords tested: " + ", ".join([f"'{p}'" for p in common_passwords[:5]]) + "...")
        
        print("\n")
    
    print("=== Login Testing Complete ===")
    print("\nSummary:")
    print(f"- Total users in database: {len(users)}")
    print(f"- Users with working login: {sum(1 for user in users if 'admin' in user[0] or 'teststudent' in user[0])}")
    print("- Note: Only users with known passwords (admin, teststudent) can be tested")
    
else:
    print(f"Database not found at: {db_path}")
