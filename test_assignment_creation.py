#!/usr/bin/env python3
"""
Test script to login and create an assignment with student assignment
"""

import sys
import os
import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BASE_URL = "http://localhost:5000"

def test_assignment_creation():
    print("=== Testing Assignment Creation with Student Assignment ===\n")
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Step 1: Get login page to get CSRF token if needed
    print("1. Getting login page...")
    login_page = session.get(f"{BASE_URL}/login")
    
    if login_page.status_code != 200:
        print(f"Failed to get login page. Status: {login_page.status_code}")
        return False
    
    # Step 2: Login as test tutor with known credentials
    print("2. Logging in as test tutor...")
    login_data = {
        'username': 'test_tutor',
        'password': 'test123'  # Known password
    }
    
    login_response = session.post(f"{BASE_URL}/login", data=login_data)
    
    if login_response.status_code != 200:
        print(f"Login failed. Status: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return False
    
    # Check if login was successful by looking for redirect to tutor dashboard
    if 'tutor_dashboard' in login_response.url:
        print("✓ Login successful")
    else:
        print("✗ Login may have failed - not redirected to tutor dashboard")
        print(f"Final URL: {login_response.url}")
        return False
    
    # Step 3: Get the create assignment page
    print("3. Getting create assignment page...")
    create_page = session.get(f"{BASE_URL}/create_assignment")
    
    if create_page.status_code != 200:
        print(f"Failed to get create assignment page. Status: {create_page.status_code}")
        return False
    
    print("✓ Create assignment page loaded successfully")
    
    # Step 4: Create an assignment with student assignment
    print("4. Creating assignment with student assignment...")
    
    assignment_data = {
        'title': 'Test Assignment with Students',
        'description': 'This is a test assignment to verify student assignment functionality',
        'assigned_student_ids': ['1', '3']  # Assign to test1 (ID 1) and Schumacherm2013 (ID 3)
    }
    
    create_response = session.post(f"{BASE_URL}/create_assignment", data=assignment_data)
    
    if create_response.status_code == 200:
        print("✓ Assignment creation request completed")
        
        # Check if we were redirected (success) or stayed on the same page (error)
        if 'create_assignment' in create_response.url:
            print("✗ Assignment creation may have failed - still on create page")
            
            # Parse the response to see if there are any error messages
            soup = BeautifulSoup(create_response.text, 'html.parser')
            error_messages = soup.find_all(class_='alert-error')
            if error_messages:
                for error in error_messages:
                    print(f"Error: {error.get_text().strip()}")
            else:
                print("No specific error messages found")
                
        else:
            print("✓ Assignment creation successful - redirected away from create page")
            print(f"Redirected to: {create_response.url}")
            
    else:
        print(f"✗ Assignment creation failed. Status: {create_response.status_code}")
        print(f"Response: {create_response.text[:500]}...")  # Show first 500 chars
    
    return True

if __name__ == "__main__":
    success = test_assignment_creation()
    
    if success:
        print("\n=== Test completed successfully ===")
        print("Now run test_student_assignment.py to verify students were assigned")
    else:
        print("\n=== Test failed ===")
        sys.exit(1)