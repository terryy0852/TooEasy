#!/usr/bin/env python3
"""
Test script to verify if login credentials work on production
"""

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://tooeasy.onrender.com"

def test_login_credentials():
    print("🔐 Testing login credentials on production...")
    
    # Test different credential combinations
    test_cases = [
        {"username": "test_tutor", "password": "test123"},
        {"username": "test_tutor", "password": "wrongpassword"},
        {"username": "nonexistent", "password": "test123"},
    ]
    
    for i, credentials in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {credentials['username']} / {credentials['password']}")
        
        session = requests.Session()
        
        # Get login page
        login_page = session.get(f"{BASE_URL}/login")
        soup = BeautifulSoup(login_page.text, 'html.parser')
        
        # Find the form
        form = soup.find('form')
        if not form:
            print("   ❌ No form found")
            continue
            
        # Prepare form data
        form_data = {}
        for inp in form.find_all('input'):
            name = inp.get('name')
            if name and inp.get('type') != 'submit':
                value = inp.get('value', '')
                if name == 'username':
                    value = credentials['username']
                elif name == 'password':
                    value = credentials['password']
                form_data[name] = value
        
        # Submit the form
        form_action = form.get('action', '')
        if not form_action.startswith('http'):
            form_action = f"{BASE_URL}{form_action}"
        
        response = session.post(form_action, data=form_data)
        
        # Check result
        result_soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for error messages
        errors = result_soup.find_all(class_=['alert-danger', 'error', 'flash-error'])
        if errors:
            for error in errors:
                error_text = error.get_text(strip=True)
                print(f"   ❌ Login failed: {error_text}")
        else:
            # Check if we got redirected to dashboard
            if "dashboard" in response.url or "tutor_dashboard" in response.url:
                print(f"   ✅ Login successful! Redirected to: {response.url}")
                
                # Check if we can access protected pages
                protected_response = session.get(f"{BASE_URL}/tutor_dashboard")
                if protected_response.status_code == 200:
                    print(f"   ✅ Access to tutor dashboard: {protected_response.status_code}")
                else:
                    print(f"   ❌ Cannot access tutor dashboard: {protected_response.status_code}")
                    
            else:
                print(f"   ⚠️  No error but not redirected to dashboard. Current URL: {response.url}")
                
                # Check if we're still on login page
                title = result_soup.find('title')
                if title and 'login' in title.get_text().lower():
                    print("   ❌ Still on login page - credentials may be wrong")
                else:
                    print("   ℹ️  On different page - might be successful")

if __name__ == "__main__":
    test_login_credentials()