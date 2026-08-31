import requests
from bs4 import BeautifulSoup

login_url = 'http://localhost:5000/login'

print("=== Debugging Failed Login ===\n")

# Test with incorrect credentials
test_cases = [
    {'username': 'test_user', 'password': 'wrongpass'},
    {'username': 'test_login', 'password': 'wrongpass'}
]

for test_case in test_cases:
    print(f"Testing with: {test_case['username']}/{test_case['password']}")
    print("=" * 40)
    
    # Send login request
    response = requests.post(login_url, data=test_case)
    print(f"Status code: {response.status_code}")
    
    # Parse the response
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Check for error messages
    error_div = soup.find(class_='error-message')
    if error_div:
        print(f"Error message: {error_div.text.strip()}")
    
    # Check if we're still on login page
    if '/login' in response.url:
        print("Still on login page - login failed")
    
    print()

# Let's also verify if these users exist in the database
print("=== Checking User Existence in Database ===")
print("Running query to check test users...")

import sqlite3
import os

# Path to the database
db_path = os.path.join('instance', 'assignments.db')

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if users exist
    cursor.execute("SELECT username, role FROM user WHERE username IN ('test_user', 'test_login')")
    users = cursor.fetchall()
    
    if users:
        print("Users found in database:")
        for user in users:
            print(f"  - {user[0]} (role: {user[1]})")
    else:
        print("No test users found in database.")
    
    # List all users to see what's there
    print("\nAll users in database:")
    cursor.execute("SELECT username, role, email FROM user")
    all_users = cursor.fetchall()
    for user in all_users:
        print(f"  - {user[0]} (role: {user[1]}, email: {user[2]})")
    
    conn.close()
else:
    print(f"Database not found at: {db_path}")
