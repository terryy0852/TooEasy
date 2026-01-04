#!/usr/bin/env python3
"""
Final test script to verify the View Submissions fix is working
"""

import requests
import re
import time

def test_view_submissions_final():
    """Test the view submissions functionality with proper CSRF handling"""
    
    print("=== FINAL TEST OF VIEW SUBMISSIONS FIX ===")
    
    # Create session
    session = requests.Session()
    
    # Step 1: Get login page and extract any CSRF token
    print("Getting login page...")
    login_page = session.get('http://127.0.0.1:5000/login')
    print(f"Login page status: {login_page.status_code}")
    
    if login_page.status_code != 200:
        print("❌ Failed to get login page")
        return False
    
    # Look for CSRF token in the form
    csrf_token = None
    if 'csrf_token' in login_page.text:
        # Try to extract CSRF token
        match = re.search(r'name="csrf_token" value="([^"]+)"', login_page.text)
        if match:
            csrf_token = match.group(1)
            print(f"Found CSRF token: {csrf_token[:10]}...")
    
    # Step 2: Prepare login data
    login_data = {
        'username': 'tutor1',
        'password': '123456'
    }
    
    if csrf_token:
        login_data['csrf_token'] = csrf_token
    
    # Step 3: Submit login
    print("Submitting login...")
    response = session.post('http://127.0.0.1:5000/login', data=login_data, allow_redirects=False)
    print(f"Login POST status: {response.status_code}")
    
    # Check if login was successful (should redirect)
    if response.status_code in [302, 303]:
        print("✅ Login successful (redirect detected)")
        
        # Follow the redirect manually
        redirect_url = response.headers.get('Location', '/student_dashboard')
        if not redirect_url.startswith('http'):
            redirect_url = 'http://127.0.0.1:5000' + redirect_url
        
        print(f"Following redirect to: {redirect_url}")
        dashboard_response = session.get(redirect_url)
        print(f"Dashboard status: {dashboard_response.status_code}")
        
        # Verify we're logged in
        if 'tutor1' in dashboard_response.text or 'Dashboard' in dashboard_response.text:
            print("✅ Successfully logged in and accessed dashboard")
            
            # Step 4: Test view submissions
            print(f"\nTesting view_submissions/1...")
            response = session.get('http://127.0.0.1:5000/view_submissions/1')
            print(f"View submissions status: {response.status_code}")
            
            # Save response for analysis
            with open('view_submissions_final_test.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            # Check content
            if 'Assignment not found' in response.text:
                print("❌ ERROR: Assignment not found message still appears")
                print("The fix is NOT working correctly!")
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
                    title_match = re.search(r'<title>([^<]+)</title>', response.text)
                    if title_match:
                        print(f"Page title: {title_match.group(1)}")
                
                # Check if it's still showing login page
                if 'Login' in response.text and 'password' in response.text.lower():
                    print("❌ Still showing login page - authentication failed")
                    return False
                else:
                    print("? Response content unclear - check view_submissions_final_test.html")
                    return False
        else:
            print("❌ Dashboard access failed - not properly logged in")
            print("First 200 characters of dashboard:")
            print(dashboard_response.text[:200])
            return False
            
    elif response.status_code == 200:
        print("❌ Login failed - still on login page")
        print("First 200 characters of response:")
        print(response.text[:200])
        return False
    else:
        print(f"❌ Unexpected login response status: {response.status_code}")
        return False

if __name__ == "__main__":
    success = test_view_submissions_final()
    if success:
        print("\n🎉 VIEW SUBMISSIONS FIX IS WORKING CORRECTLY!")
        print("The 'Assignment not found' error has been resolved.")
    else:
        print("\n❌ VIEW SUBMISSIONS FIX NEEDS MORE WORK")