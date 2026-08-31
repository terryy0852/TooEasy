#!/usr/bin/env python3
"""
Test script to simulate student login and check assignment visibility
"""

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://tooeasy.onrender.com"

def test_student_login_and_assignment_view():
    """Test student login and check if assignments are visible"""
    session = requests.Session()
    
    print("1. Accessing login page...")
    response = session.get(f"{BASE_URL}/login")
    print(f"   Status: {response.status_code}")
    
    # Try to login as student
    print("2. Attempting student login...")
    login_data = {
        'username': 'test_student',  # or whatever student username you use
        'password': 'test_password'
    }
    
    response = session.post(f"{BASE_URL}/login", data=login_data)
    print(f"   Login status: {response.status_code}")
    print(f"   Redirected to: {response.url}")
    
    # Check if we're on student dashboard
    if "student_dashboard" in response.url or response.status_code == 200:
        print("3. Checking student dashboard for assignments...")
        
        # Parse the dashboard content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for assignment elements
        assignments = soup.find_all('div', class_='assignment')
        assignment_cards = soup.find_all('div', class_='card')
        assignment_tables = soup.find_all('table')
        
        print(f"   Found {len(assignments)} assignment divs")
        print(f"   Found {len(assignment_cards)} assignment cards")
        print(f"   Found {len(assignment_tables)} tables")
        
        # Check for specific assignment-related text
        page_text = response.text.lower()
        has_assignments = 'assignment' in page_text
        has_no_assignments = 'no assignments' in page_text or 'no active assignments' in page_text
        
        print(f"   Page contains 'assignment': {has_assignments}")
        print(f"   Page contains 'no assignments': {has_no_assignments}")
        
        # Save the dashboard content for analysis
        with open('student_dashboard_debug.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("   Saved dashboard content to student_dashboard_debug.html")
        
        # Check if we can access other student pages
        print("4. Testing other student routes...")
        routes_to_test = ['/student_dashboard', '/view_assignment/1', '/change_password']
        
        for route in routes_to_test:
            try:
                resp = session.get(f"{BASE_URL}{route}")
                print(f"   {route}: {resp.status_code} (redirect: {resp.url if resp.url != f'{BASE_URL}{route}' else 'no'})")
            except Exception as e:
                print(f"   {route}: Error - {e}")
                
    else:
        print("❌ Failed to reach student dashboard")
        print(f"   Final URL: {response.url}")
        print(f"   Content snippet: {response.text[:200]}...")

if __name__ == "__main__":
    test_student_login_and_assignment_view()