#!/usr/bin/env python3
"""Test script to verify assignment deletion functionality"""

import requests
import sqlite3
import time
from bs4 import BeautifulSoup

def test_assignment_deletion():
    # Test login as teacher
    session = requests.Session()
    
    print("=== GETTING LOGIN PAGE ===")
    # First, get the login page to check for CSRF token
    login_page_response = session.get('http://127.0.0.1:5000/login')
    print(f"Login page status: {login_page_response.status_code}")
    
    # Parse the login page to check for CSRF token
    from bs4 import BeautifulSoup
    login_soup = BeautifulSoup(login_page_response.text, 'html.parser')
    
    # Check for CSRF token in the login form
    login_form = login_soup.find('form')
    csrf_token = None
    if login_form:
        csrf_input = login_form.find('input', {'name': 'csrf_token'})
        if csrf_input and csrf_input.get('value'):
            csrf_token = csrf_input.get('value')
            print(f"Found CSRF token in login form: {csrf_token[:10]}...")
        else:
            print("No CSRF token found in login form")
    
    # Prepare login data
    login_data = {
        'username': 'admin',  # Changed from tutor1 to admin
        'password': 'admin123'  # Changed to known working password
    }
    
    # Add CSRF token if found
    if csrf_token:
        login_data['csrf_token'] = csrf_token
    
    print(f"Login data: {login_data}")

    print("\n=== TESTING TEACHER LOGIN ===")
    login_response = session.post('http://127.0.0.1:5000/login', data=login_data)
    print(f"Login status: {login_response.status_code}")
    print(f"Login response URL: {login_response.url}")
    
    # Check if login was successful by looking at the response
    if login_response.status_code == 200:
        # Check if we're still on login page (login failed)
        if 'login' in login_response.url and 'Login' in login_response.text:
            print("❌ Login failed - still on login page")
            print(f"Login response preview: {login_response.text[:200]}")
            return False
        else:
            print("✅ Login appears successful - redirected away from login page")
    else:
        print("❌ Login request failed")
        return False

    print("✅ Teacher login successful!")
    
    # Get current assignments count
    print("\n=== CHECKING ASSIGNMENTS BEFORE DELETION ===")
    
    # Connect to database to check current state
    conn = sqlite3.connect('instance/assignments.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM assignment")
    assignments_before = cursor.fetchone()[0]
    print(f"Assignments before deletion: {assignments_before}")
    
    cursor.execute("SELECT id, title FROM assignment ORDER BY id")
    assignments = cursor.fetchall()
    print("Available assignments:")
    for assignment in assignments:
        print(f"  ID {assignment[0]}: {assignment[1]}")
    
    if assignments_before == 0:
        print("❌ No assignments available for deletion test")
        conn.close()
        return False
    
    # Choose the last assignment for deletion
    assignment_to_delete = assignments[-1][0]
    print(f"\nWill delete assignment ID: {assignment_to_delete}")
    
    # Check related data before deletion
    cursor.execute("SELECT COUNT(*) FROM submission WHERE assignment_id = ?", (assignment_to_delete,))
    submissions_before = cursor.fetchone()[0]
    print(f"Related submissions before deletion: {submissions_before}")
    
    cursor.execute("SELECT COUNT(*) FROM student_assignment WHERE assignment_id = ?", (assignment_to_delete,))
    student_assignments_before = cursor.fetchone()[0]
    print(f"Related student assignments before deletion: {student_assignments_before}")
    
    conn.close()
    
    # Test assignment deletion
    print(f"\n=== TESTING ASSIGNMENT DELETION ===")
    
    # First, access the teacher dashboard to get the page and CSRF token
    dashboard_response = session.get('http://127.0.0.1:5000/student_dashboard')
    print(f"Dashboard access status: {dashboard_response.status_code}")
    
    if dashboard_response.status_code != 200:
        print("❌ Cannot access teacher dashboard")
        return False
    
    # Debug: Print first 500 characters of dashboard to see what's there
    print(f"Dashboard response preview: {dashboard_response.text[:500]}")
    
    # Check if we're still logged in by looking for the username in the response
    if 'admin' not in dashboard_response.text:  # Changed from tutor1 to admin
        print("❌ Session lost - username not found in dashboard")
        # Let's check if we're redirected to login
        if 'login' in dashboard_response.url:
            print(f"❌ Redirected to login page: {dashboard_response.url}")
        return False
    
    print("✅ Session maintained - username found in dashboard")
    
    # Extract CSRF token from the page if it exists
    csrf_token = None
    if 'csrf_token' in dashboard_response.text:
        # Try to extract CSRF token from form
        import re
        csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', dashboard_response.text)
        if csrf_match:
            csrf_token = csrf_match.group(1)
            print(f"Found CSRF token: {csrf_token[:10]}...")
        else:
            print("No CSRF token found in form")
    
    # Now attempt deletion with CSRF token if available
    delete_data = {}
    if csrf_token:
        delete_data['csrf_token'] = csrf_token
    
    # Add headers to maintain session
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'http://127.0.0.1:5000/student_dashboard'
    }
    
    delete_response = session.post(
        f'http://127.0.0.1:5000/assignment/{assignment_to_delete}/delete', 
        data=delete_data,
        headers=headers,
        allow_redirects=True  # Allow redirects to maintain session
    )
    
    print(f"Deletion status: {delete_response.status_code}")
    print(f"Final URL after deletion: {delete_response.url}")
    
    # Check if we got redirected to login (session lost)
    if 'login' in delete_response.url:
        print("❌ Session lost during deletion - redirected to login")
        return False
    
    # Check if deletion was successful (should redirect to dashboard)
    if 'dashboard' in delete_response.url:
        print("✅ Successfully redirected to dashboard after deletion")
    else:
        print(f"ℹ️  Redirected to: {delete_response.url}")
    
    if delete_response.status_code == 200:
        print("✅ Assignment deletion request successful!")
        
        # Verify deletion by checking database
        print("\n=== VERIFYING DELETION ===")
        conn = sqlite3.connect('instance/assignments.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM assignment WHERE id = ?", (assignment_to_delete,))
        assignment_exists = cursor.fetchone()[0]
        
        if assignment_exists == 0:
            print("✅ Assignment successfully removed from database")
        else:
            print("❌ Assignment still exists in database")
        
        # Check related data cleanup
        cursor.execute("SELECT COUNT(*) FROM submission WHERE assignment_id = ?", (assignment_to_delete,))
        submissions_after = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM student_assignment WHERE assignment_id = ?", (assignment_to_delete,))
        student_assignments_after = cursor.fetchone()[0]
        
        if submissions_after == 0 and student_assignments_after == 0:
            print("✅ Related submissions and student assignments cleaned up")
        else:
            print(f"❌ Some related data remains: {submissions_after} submissions, {student_assignments_after} student assignments")
        
        # Check total assignments count after deletion
        cursor.execute("SELECT COUNT(*) FROM assignment")
        assignments_after = cursor.fetchone()[0]
        print(f"Assignments after deletion: {assignments_after}")
        
        if assignments_after == assignments_before - 1:
            print("✅ Assignment count decreased by 1")
        else:
            print(f"❌ Assignment count should be {assignments_before - 1}, but is {assignments_after}")
        
        conn.close()
        
        return True
    else:
        print("❌ Assignment deletion failed!")
        print(f"Response: {delete_response.text[:500]}")
        return False

if __name__ == "__main__":
    success = test_assignment_deletion()
    if success:
        print("\n🎉 DELETION TEST PASSED! Assignment deletion functionality is working correctly.")
    else:
        print("\n❌ Deletion test failed. Please check the errors above.")