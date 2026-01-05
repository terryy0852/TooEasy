#!/usr/bin/env python3
"""
Test script to verify login functionality on local server
"""

import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "http://127.0.0.1:5000"

def test_local_login():
    print("🔐 Testing local login functionality...")
    
    session = requests.Session()
    
    try:
        # 1. Get login page
        print("\n1. Getting login page...")
        response = session.get(f"{BASE_URL}/login")
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Failed to get login page: {response.status_code}")
            return False
        
        # 2. Parse login form
        print("\n2. Parsing login form...")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check for CSRF token
        csrf_token = soup.find('input', {'name': 'csrf_token'})
        if csrf_token:
            csrf_value = csrf_token.get('value', '')
            print(f"   CSRF Token found: {csrf_value[:10]}...")
        else:
            print("   ⚠️  No CSRF token found in form")
            csrf_value = ""
        
        # 3. Test with common credentials
        print("\n3. Testing login with sample credentials...")
        
        # Try to login with admin credentials
        login_data = {
            'username': 'admin',
            'password': 'admin123',
            'csrf_token': csrf_value
        }
        
        print(f"   Trying: {login_data['username']} / {login_data['password']}")
        
        response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
        print(f"   Login response: {response.status_code}")
        print(f"   Response headers: {dict(response.headers)}")
        
        if response.status_code == 302:  # Redirect after successful login
            location = response.headers.get('Location', '')
            print(f"   ✅ Redirected to: {location}")
            
            # 4. Try to access dashboard
            print("\n4. Accessing dashboard...")
            dashboard_response = session.get(f"{BASE_URL}{location}")
            print(f"   Dashboard status: {dashboard_response.status_code}")
            
            if dashboard_response.status_code == 200:
                print("   ✅ Successfully accessed dashboard")
                return True
            else:
                print(f"   ❌ Failed to access dashboard: {dashboard_response.status_code}")
                return False
        
        elif response.status_code == 200:
            # Check for error messages
            error_soup = BeautifulSoup(response.text, 'html.parser')
            flash_messages = error_soup.find_all('div', class_='flash')
            if flash_messages:
                for msg in flash_messages:
                    print(f"   Flash message: {msg.text.strip()}")
            
            print("   ❌ Login failed - no redirect")
            return False
        else:
            print(f"   ❌ Unexpected status code: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def test_database_connection():
    print("\n🔍 Testing database connection...")
    try:
        # Simple test to see if database is accessible
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Health check: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Server status: {data.get('status', 'unknown')}")
            return True
        else:
            print("   ❌ Health check failed")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Local Login Test Suite")
    print("=" * 60)
    
    # Test database connection first
    db_ok = test_database_connection()
    if not db_ok:
        print("\n❌ Database connection issues detected")
    
    # Test login
    login_ok = test_local_login()
    
    print("\n" + "=" * 60)
    if login_ok:
        print("✅ Login test PASSED")
    else:
        print("❌ Login test FAILED")
    print("=" * 60)