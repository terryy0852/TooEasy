#!/usr/bin/env python3
"""
Comprehensive authentication debug script for production deployment
This script will help identify why login is not working on the production server
"""

import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "https://tooeasy.onrender.com"
TEST_TUTOR = "test_tutor"
TEST_PASSWORD = "Test123!"

def debug_auth_issue():
    print("🔍 Debugging Authentication Issue on Production Server")
    print("=" * 60)
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # 1. Test server accessibility
    print("\n1. Testing server accessibility...")
    try:
        health_response = session.get(f"{BASE_URL}/health")
        print(f"   Health check: {health_response.status_code}")
        
        home_response = session.get(BASE_URL)
        print(f"   Home page: {home_response.status_code}")
        
        if home_response.status_code != 200:
            print("❌ Server is not accessible")
            return
    except Exception as e:
        print(f"❌ Server connection failed: {e}")
        return
    
    # 2. Check login page structure
    print("\n2. Analyzing login page structure...")
    login_page = session.get(f"{BASE_URL}/login")
    login_soup = BeautifulSoup(login_page.text, 'html.parser')
    
    # Check form details
    form = login_soup.find('form')
    if form:
        form_action = form.get('action', '')
        form_method = form.get('method', 'POST').upper()
        print(f"   Form action: {form_action}")
        print(f"   Form method: {form_method}")
        
        # Check for CSRF token
        csrf_input = form.find('input', {'name': 'csrf_token'})
        if csrf_input:
            csrf_value = csrf_input.get('value', '')
            print(f"   CSRF token found: {'Yes' if csrf_value else 'No'}")
        else:
            print("   CSRF token: Not found")
            
        # Check all form inputs
        inputs = form.find_all('input')
        print(f"   Form inputs: {len(inputs)}")
        for inp in inputs:
            name = inp.get('name', 'no-name')
            type_ = inp.get('type', 'text')
            value = inp.get('value', '')
            print(f"     - {name} ({type_}): {value[:20]}...")
    
    # 3. Test login with detailed debugging
    print("\n3. Testing login process...")
    
    # Prepare form data
    form_data = {
        'username': TEST_TUTOR,
        'password': TEST_PASSWORD
    }
    
    # Add CSRF token if found
    if csrf_input and csrf_input.get('value'):
        form_data['csrf_token'] = csrf_input.get('value')
    
    print(f"   Login data: {form_data}")
    
    # Submit login
    login_response = session.post(f"{BASE_URL}/login", data=form_data)
    print(f"   Login response: {login_response.status_code}")
    print(f"   Redirected to: {login_response.url}")
    
    # Check cookies
    cookies = session.cookies.get_dict()
    print(f"   Session cookies: {cookies}")
    
    # 4. Analyze login result
    print("\n4. Analyzing login result...")
    
    if login_response.status_code == 200:
        result_soup = BeautifulSoup(login_response.text, 'html.parser')
        
        # Check if we're still on login page
        title = result_soup.find('title')
        if title and 'login' in title.get_text().lower():
            print("   ❌ Still on login page after login attempt")
            
            # Check for error messages
            errors = result_soup.find_all(class_=['alert-danger', 'error', 'flash-error', 'message-error'])
            if errors:
                for error in errors:
                    print(f"   Error message: {error.get_text(strip=True)}")
            else:
                print("   No error messages found")
                
            # Check for success messages (shouldn't be here if login failed)
            successes = result_soup.find_all(class_=['alert-success', 'success', 'flash-success', 'message-success'])
            if successes:
                for success in successes:
                    print(f"   Success message: {success.get_text(strip=True)}")
        else:
            print("   ✅ Redirected away from login page")
            print(f"   Current page title: {title.get_text() if title else 'No title'}")
    
    # 5. Test dashboard access
    print("\n5. Testing dashboard access...")
    dashboard_response = session.get(f"{BASE_URL}/tutor_dashboard")
    print(f"   Dashboard status: {dashboard_response.status_code}")
    print(f"   Dashboard URL: {dashboard_response.url}")
    
    if dashboard_response.status_code == 200:
        dashboard_soup = BeautifulSoup(dashboard_response.text, 'html.parser')
        title = dashboard_soup.find('title')
        print(f"   Dashboard title: {title.get_text() if title else 'No title'}")
        
        # Check for user-specific content
        user_content = dashboard_soup.find(text=lambda t: TEST_TUTOR in t)
        if user_content:
            print("   ✅ User-specific content found on dashboard")
        else:
            print("   ❌ No user-specific content found")
            
        # Check for assignments
        assignments = dashboard_soup.find_all(text=lambda t: 'assignment' in t.lower() or '作业' in t)
        if assignments:
            print(f"   Found {len(assignments)} assignment-related elements")
        else:
            print("   No assignment-related content found")
    else:
        print("   ❌ Cannot access dashboard")
    
    # 6. Test session persistence
    print("\n6. Testing session persistence...")
    second_dashboard = session.get(f"{BASE_URL}/tutor_dashboard")
    print(f"   Second dashboard request: {second_dashboard.status_code}")
    
    # 7. Check if we can access other protected routes
    print("\n7. Testing other protected routes...")
    protected_routes = [
        '/create_assignment',
        '/student_dashboard',
        '/change_password'
    ]
    
    for route in protected_routes:
        response = session.get(f"{BASE_URL}{route}")
        print(f"   {route}: {response.status_code}")
        if response.status_code == 302 or 'login' in response.url:
            print(f"     ➡️ Redirected to: {response.url}")
    
    print("\n" + "=" * 60)
    print("🔍 Authentication Debug Complete")
    
    # Save detailed information for analysis
    with open('auth_debug_report.txt', 'w', encoding='utf-8') as f:
        f.write("Authentication Debug Report\n")
        f.write("=" * 40 + "\n")
        f.write(f"Base URL: {BASE_URL}\n")
        f.write(f"Login response code: {login_response.status_code}\n")
        f.write(f"Login redirected to: {login_response.url}\n")
        f.write(f"Session cookies: {json.dumps(cookies, indent=2)}\n")
        f.write(f"Dashboard access: {dashboard_response.status_code}\n")
        
        if login_response.status_code == 200:
            f.write("\nLogin page content analysis:\n")
            f.write("-" * 30 + "\n")
            f.write(login_response.text[:1000] + "\n...")

if __name__ == "__main__":
    debug_auth_issue()