#!/usr/bin/env python3
"""
Debug the login page to see what's happening
"""

import requests
import re

def debug_login_page():
    """Debug the login page"""
    
    print("=== DEBUG LOGIN PAGE ===")
    
    # Create session
    session = requests.Session()
    
    # Get login page
    print("Getting login page...")
    response = session.get('http://127.0.0.1:5000/login')
    print(f"Login page status: {response.status_code}")
    
    # Save the full page
    with open('debug_login_page.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    print(f"Page length: {len(response.text)} characters")
    
    # Look for CSRF token
    csrf_token = None
    token_match = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
    if token_match:
        csrf_token = token_match.group(1)
        print(f"✅ Found CSRF token: {csrf_token}")
    else:
        print("❌ CSRF token not found in form")
        # Look for any hidden inputs
        hidden_inputs = re.findall(r'<input[^>]*type="hidden"[^>]*>', response.text)
        if hidden_inputs:
            print("Found hidden inputs:")
            for input_tag in hidden_inputs:
                print(f"  {input_tag}")
        else:
            print("No hidden inputs found")
    
    # Look for form action
    form_action = None
    action_match = re.search(r'<form[^>]*action="([^"]+)"', response.text)
    if action_match:
        form_action = action_match.group(1)
        print(f"Form action: {form_action}")
    
    # Look for any error messages
    if 'error' in response.text.lower():
        print("Found 'error' in page content")
    
    # Look for any login-related content
    if 'login' in response.text.lower():
        print("Found 'login' in page content")
    
    return csrf_token

if __name__ == "__main__":
    debug_login_page()