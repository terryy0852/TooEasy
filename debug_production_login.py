#!/usr/bin/env python3
"""
Debug script to understand what's happening with login and assignments on production
"""

import requests
from bs4 import BeautifulSoup
import sys

BASE_URL = "https://tooeasy.onrender.com"
TEST_TUTOR = "test_tutor"
TEST_PASSWORD = "test123"

def debug_production():
    print("🔍 Debugging PRODUCTION deployment...")
    
    session = requests.Session()
    
    # 1. Check homepage
    print("\n1. Homepage analysis:")
    response = session.get(BASE_URL)
    print(f"   Status: {response.status_code}")
    print(f"   URL: {response.url}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.find('title')
    if title:
        print(f"   Title: {title.get_text()}")
    
    # 2. Analyze login form
    print("\n2. Login form analysis:")
    login_form = soup.find('form')
    if login_form:
        print(f"   Form action: {login_form.get('action', 'None')}")
        print(f"   Form method: {login_form.get('method', 'None')}")
        
        # Find all input fields
        inputs = login_form.find_all('input')
        print(f"   Input fields: {len(inputs)}")
        for inp in inputs:
            name = inp.get('name', 'no-name')
            type_ = inp.get('type', 'no-type')
            print(f"     - {name} ({type_})")
    else:
        print("   No form found - might already be logged in or different page structure")
    
    # 3. Check if we're already logged in (cookies)
    print(f"\n3. Session cookies: {len(session.cookies)} cookies")
    for cookie in session.cookies:
        print(f"   - {cookie.name}: {cookie.value}")
    
    # 4. Try to access tutor dashboard directly
    print("\n4. Direct dashboard access:")
    dashboard_response = session.get(f"{BASE_URL}/tutor_dashboard")
    print(f"   Status: {dashboard_response.status_code}")
    print(f"   URL: {dashboard_response.url}")
    
    # Check if we got redirected to login
    if "login" in dashboard_response.url:
        print("   ➡️ Redirected to login page")
    else:
        print("   ➡️ Accessed dashboard directly")
        
        dashboard_soup = BeautifulSoup(dashboard_response.text, 'html.parser')
        
        # Look for user info
        user_info = dashboard_soup.find(text=lambda t: 'test_tutor' in t)
        if user_info:
            print("   ✅ User info found on dashboard")
        
        # Look for any assignment-related content
        assignment_content = dashboard_soup.find(text=lambda t: 'assignment' in t.lower() or '作业' in t)
        if assignment_content:
            print("   ✅ Assignment-related content found")
        
        # Save the dashboard HTML for analysis
        with open('dashboard_debug.html', 'w', encoding='utf-8') as f:
            f.write(dashboard_response.text)
        print("   💾 Saved dashboard HTML to 'dashboard_debug.html'")
    
    # 5. Try login with detailed debugging
    print("\n5. Detailed login attempt:")
    
    # Get login page again to ensure fresh state
    login_page = session.get(f"{BASE_URL}/login")
    login_soup = BeautifulSoup(login_page.text, 'html.parser')
    
    # Find the login form
    form = login_soup.find('form')
    if form:
        form_action = form.get('action', '')
        if not form_action.startswith('http'):
            form_action = f"{BASE_URL}{form_action}"
        
        # Prepare form data
        form_data = {}
        for inp in form.find_all('input'):
            name = inp.get('name')
            if name and inp.get('type') != 'submit':
                value = inp.get('value', '')
                if name == 'username':
                    value = TEST_TUTOR
                elif name == 'password':
                    value = TEST_PASSWORD
                form_data[name] = value
        
        print(f"   Form action: {form_action}")
        print(f"   Form data: {form_data}")
        
        # Submit the form
        login_result = session.post(form_action, data=form_data)
        print(f"   Login result: {login_result.status_code}")
        print(f"   Redirected to: {login_result.url}")
        
        # Check for error messages
        result_soup = BeautifulSoup(login_result.text, 'html.parser')
        errors = result_soup.find_all(class_=['alert-danger', 'error', 'flash-error'])
        if errors:
            for error in errors:
                print(f"   ❌ Error: {error.get_text(strip=True)}")
        else:
            print("   ✅ No error messages found")
            
            # Check if we can access dashboard after login
            final_dashboard = session.get(f"{BASE_URL}/tutor_dashboard")
            print(f"   Final dashboard: {final_dashboard.status_code}")
            
            # Save final state for analysis
            with open('final_dashboard.html', 'w', encoding='utf-8') as f:
                f.write(final_dashboard.text)
            print("   💾 Saved final dashboard HTML")
    
    print("\n🔍 Debug completed!")

if __name__ == "__main__":
    debug_production()