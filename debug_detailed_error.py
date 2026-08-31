#!/usr/bin/env python3
"""Debug script to capture detailed assignment access error"""

import requests
import json

def debug_detailed_error():
    # Test login
    session = requests.Session()
    login_data = {
        'username': 'teststudent',
        'password': 'password123'
    }

    print("Testing login...")
    login_response = session.post('http://127.0.0.1:5000/login', data=login_data)
    print(f"Login status: {login_response.status_code}")

    if login_response.status_code == 200:
        print("Login successful!")
        
        # Test accessing assignment 1
        print("Testing assignment access...")
        assignment_response = session.get('http://127.0.0.1:5000/view_assignment/1')
        print(f"Assignment access status: {assignment_response.status_code}")
        
        if assignment_response.status_code == 500:
            print("\n=== FULL ERROR RESPONSE ===")
            print(f"Headers: {dict(assignment_response.headers)}")
            print(f"Content length: {len(assignment_response.text)}")
            print(f"Full response:\n{assignment_response.text}")
            
            # Also try to get any server logs by checking if there's an app.log
            print("\n=== CHECKING FOR APP.LOG ===")
            try:
                with open('app.log', 'r') as f:
                    print("Found app.log:")
                    print(f.read())
            except FileNotFoundError:
                print("No app.log file found")
                
            # Try to access a simple page to see if server is still responsive
            print("\n=== TESTING SERVER RESPONSIVENESS ===")
            try:
                test_response = session.get('http://127.0.0.1:5000/login')
                print(f"Login page status: {test_response.status_code}")
            except Exception as e:
                print(f"Server error: {e}")
        else:
            print(f"Assignment access status: {assignment_response.status_code}")
            if assignment_response.status_code == 200:
                print("✅ Assignment access successful!")
                if 'iframe' in assignment_response.text:
                    print("✅ Found iframe in assignment page!")
                else:
                    print("❌ No iframe found in assignment page")
            else:
                print("Response preview:", assignment_response.text[:200])
    else:
        print("Login failed!")
        print(login_response.text[:200])

if __name__ == "__main__":
    debug_detailed_error()