#!/usr/bin/env python3
"""Test script to verify assignment access functionality"""

import requests
import sys

def test_assignment_access():
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
        
        if assignment_response.status_code == 200:
            print("Assignment access successful!")
            # Check if there's an iframe in the response
            if 'iframe' in assignment_response.text:
                print("✅ Found iframe in assignment page!")
            else:
                print("❌ No iframe found in assignment page")
        else:
            print(f"Assignment access failed with status: {assignment_response.status_code}")
            if assignment_response.status_code == 500:
                print("Error content preview:")
                print(assignment_response.text[:500])
    else:
        print("Login failed!")
        print(login_response.text[:200])

if __name__ == "__main__":
    test_assignment_access()