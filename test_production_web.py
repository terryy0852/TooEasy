#!/usr/bin/env python3
"""
Test script to verify assignments through the web interface on production
This script will simulate a user logging in and checking assignments
"""

import requests
from bs4 import BeautifulSoup
import sys

# Production deployment URL
BASE_URL = "https://tooeasy.onrender.com"

# Test credentials (use your actual credentials)
TEST_TUTOR = "test_tutor"
TEST_PASSWORD = "test123"

def test_production_web():
    print("🔍 Testing PRODUCTION web deployment...")
    print(f"URL: {BASE_URL}")
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    try:
        # 1. First, check if the site is accessible
        print("\n1. Checking if site is accessible...")
        response = session.get(BASE_URL)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Site is not accessible. Status: {response.status_code}")
            return False
        
        # 2. Extract CSRF token from login page
        print("\n2. Extracting CSRF token...")
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = None
        
        # Look for CSRF token in meta tags or hidden inputs
        for meta in soup.find_all('meta'):
            if meta.get('name') == 'csrf-token':
                csrf_token = meta.get('content')
                break
        
        if not csrf_token:
            # Try hidden input field
            csrf_input = soup.find('input', {'name': 'csrf_token'})
            if csrf_input:
                csrf_token = csrf_input.get('value')
        
        print(f"   CSRF Token: {'Found' if csrf_token else 'Not found'}")
        
        # 3. Attempt login
        print("\n3. Attempting login...")
        login_data = {
            'username': TEST_TUTOR,
            'password': TEST_PASSWORD,
        }
        
        if csrf_token:
            login_data['csrf_token'] = csrf_token
        
        login_response = session.post(f"{BASE_URL}/login", data=login_data)
        print(f"   Login Status: {login_response.status_code}")
        
        # Check if login was successful by checking redirect or content
        if login_response.status_code == 200:
            login_soup = BeautifulSoup(login_response.text, 'html.parser')
            
            # Check for error messages
            error_div = login_soup.find('div', class_='alert-danger')
            if error_div:
                print(f"❌ Login failed: {error_div.get_text(strip=True)}")
                return False
            
            # Check if we're redirected to dashboard
            if 'tutor_dashboard' in login_response.url or 'dashboard' in login_response.url:
                print("✅ Login successful!")
            else:
                print("⚠️  Login may not have succeeded - checking dashboard access...")
        
        # 4. Access tutor dashboard
        print("\n4. Accessing tutor dashboard...")
        dashboard_response = session.get(f"{BASE_URL}/tutor_dashboard")
        print(f"   Dashboard Status: {dashboard_response.status_code}")
        
        if dashboard_response.status_code == 200:
            dashboard_soup = BeautifulSoup(dashboard_response.text, 'html.parser')
            
            # Look for assignments table
            assignments_table = dashboard_soup.find('table')
            
            if assignments_table:
                print("✅ Assignments table found!")
                
                # Count assignment rows (excluding header)
                assignment_rows = assignments_table.find_all('tr')[1:]  # Skip header
                print(f"   Number of assignments found: {len(assignment_rows)}")
                
                # Display assignment details
                for i, row in enumerate(assignment_rows, 1):
                    cols = row.find_all('td')
                    if len(cols) >= 3:  # Should have at least title, students, actions
                        title = cols[0].get_text(strip=True)
                        students = cols[1].get_text(strip=True)
                        print(f"   Assignment {i}: '{title}' - {students} students")
            else:
                print("❌ No assignments table found")
                
                # Check for "no assignments" message
                no_assignments = dashboard_soup.find(text=lambda t: 'no assignments' in t.lower() or '还没有创建任何作业' in t)
                if no_assignments:
                    print("   Message: No assignments found")
                else:
                    print("   Page content may have different structure")
                    
        else:
            print(f"❌ Could not access dashboard. Status: {dashboard_response.status_code}")
        
        # 5. Check session status
        print("\n5. Checking session status...")
        session_response = session.get(f"{BASE_URL}/health")
        print(f"   Health check: {session_response.status_code}")
        
        if session_response.status_code == 200:
            print("✅ Session is active and healthy")
        else:
            print("⚠️  Health check failed")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - site may be down or unreachable")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_production_web()
    if success:
        print("\n🎉 Production web test completed!")
    else:
        print("\n💥 Production web test failed!")
        sys.exit(1)