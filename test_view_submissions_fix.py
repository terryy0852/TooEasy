#!/usr/bin/env python3
"""
Test script to verify the View Submissions fix
"""

import requests
import sqlite3
import time

def test_view_submissions_fix():
    """Test the view submissions functionality after the fix"""
    
    print("=== TESTING VIEW SUBMISSIONS FIX ===")
    
    # Create session
    session = requests.Session()
    
    # Check what assignments exist
    print("\nChecking database for assignments...")
    conn = sqlite3.connect('instance/assignments.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, description, is_active FROM assignment')
    assignments = cursor.fetchall()
    print(f"Available assignments: {assignments}")
    conn.close()
    
    if not assignments:
        print("❌ No assignments found in database")
        return False
    
    # Test with assignment ID 1 (S2_荷塘月色)
    assignment_id = 1
    
    # Login as teacher
    print(f"\nLogging in as tutor1...")
    login_data = {
        'username': 'tutor1',
        'password': '123456'
    }
    
    # First, get the login page to obtain any CSRF token if needed
    login_page = session.get('http://127.0.0.1:5000/login')
    print(f"Login page status: {login_page.status_code}")
    
    # Submit login form
    response = session.post('http://127.0.0.1:5000/login', data=login_data)
    print(f"Login POST status: {response.status_code}")
    
    # Check if login was successful by looking for redirect
    if response.status_code in [200, 302]:
        print("✅ Login appears successful")
        
        # Access dashboard to verify session
        dashboard_response = session.get('http://127.0.0.1:5000/student_dashboard')
        print(f"Dashboard access: {dashboard_response.status_code}")
        
        if 'tutor1' in dashboard_response.text or 'Dashboard' in dashboard_response.text:
            print("✅ Session verified - can access dashboard")
            
            # Now test view submissions
            print(f"\nTesting view_submissions/{assignment_id}...")
            response = session.get(f'http://127.0.0.1:5000/view_submissions/{assignment_id}')
            print(f"View submissions status: {response.status_code}")
            
            # Save response for analysis
            with open('view_submissions_test.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            # Check for the specific error message
            if 'Assignment not found' in response.text:
                print("❌ ERROR: Assignment not found message still appears")
                print("This means the fix did not work correctly!")
                
                # Show context around error
                lines = response.text.split('\n')
                for i, line in enumerate(lines):
                    if 'Assignment not found' in line:
                        print(f"Error at line {i+1}: {line.strip()}")
                        start = max(0, i-3)
                        end = min(len(lines), i+4)
                        print("\nContext:")
                        for j in range(start, end):
                            print(f"{j+1}: {lines[j].strip()}")
                        break
                return False
                
            elif 'View Submissions' in response.text:
                print("✅ SUCCESS: View submissions page loads correctly")
                
                # Check for assignment details
                if 'S2_荷塘月色' in response.text:
                    print("✅ Assignment title found in content")
                else:
                    print("❌ Assignment title not found in content")
                    
                # Check for submissions table
                if 'Student Submissions' in response.text:
                    print("✅ Submissions table found")
                elif 'No submissions yet' in response.text:
                    print("✅ No submissions message found (expected)")
                else:
                    print("? Submissions section unclear")
                    
                return True
                
            else:
                print("? Unclear result - checking page content...")
                print(f"Response length: {len(response.text)} characters")
                
                # Check page title
                if '<title>' in response.text:
                    title_start = response.text.find('<title>') + 7
                    title_end = response.text.find('</title>')
                    title = response.text[title_start:title_end]
                    print(f"Page title: {title}")
                
                # Check if it's a login page
                if 'Login' in response.text and 'password' in response.text.lower():
                    print("❌ Response is a login page - session not maintained")
                else:
                    print("? Response content unclear - check view_submissions_test.html")
                
                return False
        else:
            print("❌ Dashboard access failed - session issue")
            print("First 200 characters of dashboard response:")
            print(dashboard_response.text[:200])
            return False
    else:
        print(f"❌ Login failed with status {response.status_code}")
        return False

if __name__ == "__main__":
    success = test_view_submissions_fix()
    if success:
        print("\n🎉 VIEW SUBMISSIONS FIX IS WORKING!")
    else:
        print("\n❌ VIEW SUBMISSIONS FIX NEEDS MORE WORK")