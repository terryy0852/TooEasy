#!/usr/bin/env python3
"""Debug script to capture detailed assignment access error"""

import requests
import json

def debug_assignment_error():
    # Test login
    session = requests.Session()
    login_data = {
        'username': 'teststudent1',
        'password': 'password123'
    }

    print("Testing login...")
    login_response = session.post('http://127.0.0.1:5000/login', data=login_data)
    print(f"Login status: {login_response.status_code}")

    if login_response.status_code == 200:
        print("Login successful!")
        
        # Test accessing assignment 1
        print("Testing assignment access...")
        assignment_response = session.get('http://127.0.0.1:5000/assignment/1')
        print(f"Assignment access status: {assignment_response.status_code}")
        
        if assignment_response.status_code == 500:
            print("\n=== FULL ERROR RESPONSE ===")
            print(f"Headers: {dict(assignment_response.headers)}")
            print(f"Content length: {len(assignment_response.text)}")
            print(f"Full response:\n{assignment_response.text}")
            
            # Also try to get any server logs
            print("\n=== CHECKING FOR APP.LOG ===")
            try:
                with open('app.log', 'r') as f:
                    print("Found app.log:")
                    print(f.read())
            except FileNotFoundError:
                print("No app.log file found")
        else:
            print(f"Assignment access status: {assignment_response.status_code}")
            print("Response preview:", assignment_response.text[:200])
    else:
        print("Login failed!")
        print(login_response.text[:200])

if __name__ == "__main__":
    debug_assignment_error()