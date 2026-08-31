import requests
from bs4 import BeautifulSoup
import json

# Base URL of the application
BASE_URL = "http://localhost:5000"

# Test phrases to check translations
TEST_PHRASES = {
    "zh_CN": {
        "expected": "作业管理系统",
        "test_in": "Assignment Management System"
    },
    "zh_TW": {
        "expected": "作業管理系統",
        "test_in": "Assignment Management System"
    },
    "en": {
        "expected": "Assignment Management System",
        "test_in": "作业管理系统"
    }
}

# Function to test translations by visiting the login page

def test_login_page_translations(lang_code):
    print(f"\n===== Testing {lang_code} translations on login page ======")
    
    # Create a session to persist cookies
    session = requests.Session()
    
    # First, visit the switch_language route to set the language
    switch_url = f"{BASE_URL}/switch_language/{lang_code}"
    print(f"Switching language to {lang_code} at: {switch_url}")
    switch_response = session.get(switch_url)
    print(f"Switch response status: {switch_response.status_code}")
    
    # After switching, visit the login page
    login_url = f"{BASE_URL}/login"
    print(f"Visiting login page at: {login_url}")
    response = session.get(login_url)
    print(f"Login page response status: {response.status_code}")
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Check the html lang attribute
    html_lang = soup.html.get('lang', 'not set')
    print(f"HTML lang attribute: {html_lang}")
    
    # Find the main title
    title_element = soup.find('h1')
    if title_element:
        title_text = title_element.text.strip()
        print(f"Page title: '{title_text}'")
        expected = TEST_PHRASES.get(lang_code, {}).get("expected", "")
        if expected and title_text == expected:
            print(f"✓ Title translation is correct for {lang_code}")
        else:
            print(f"✗ Title translation is incorrect for {lang_code}. Expected: '{expected}', Got: '{title_text}'")
    else:
        print("Could not find title element")
    
    # Check for common translated elements
    print("\nLooking for key translated elements:")
    
    # Check if any of the test phrases appear in the page
    for phrase_lang, phrase_info in TEST_PHRASES.items():
        if phrase_info["expected"] in response.text:
            print(f"Found '{phrase_info['expected']}' ({phrase_lang}) in page content")
    
    # Print cookies for debugging
    print("\nSession cookies:")
    for cookie in session.cookies:
        print(f"- {cookie.name}: {cookie.value}")
    
    return response.text

# Function to directly call the login endpoint with different language parameters

def test_language_parameters():
    print("\n===== Testing direct language parameters ======")
    
    # Test each language directly via URL parameter
    for lang in ['zh_CN', 'zh_TW', 'en']:
        url = f"{BASE_URL}/login?lang={lang}"
        print(f"\nVisiting {url}")
        response = requests.get(url)
        
        # Check for key phrases
        soup = BeautifulSoup(response.text, 'html.parser')
        title_element = soup.find('h1')
        title_text = title_element.text.strip() if title_element else "No title found"
        
        print(f"Response status: {response.status_code}")
        print(f"HTML lang attribute: {soup.html.get('lang', 'not set')}")
        print(f"Page title: '{title_text}'")
        
        # Check if any of the test phrases appear in the page
        print("Found phrases:")
        for phrase_lang, phrase_info in TEST_PHRASES.items():
            if phrase_info["expected"] in response.text:
                print(f"- '{phrase_info['expected']}' ({phrase_lang})")

# Function to create a debug endpoint in the application

def create_debug_endpoint_script():
    debug_endpoint_code = """
from flask import Flask, request, jsonify, session
from flask_babel import get_locale, gettext as _

# Assuming app and babel are already initialized

@app.route('/debug_babel')
def debug_babel():
    # Get current locale information
    current_locale = str(get_locale())
    
    # Get session information
    session_lang = session.get('lang', 'not set')
    
    # Test some translations directly
    translations = {
        '作业管理系统': _('作业管理系统'),
        '登录': _('登录'),
        '用户登录': _('用户登录'),
        '用户名': _('用户名'),
        '密码': _('密码')
    }
    
    # Get request information
    request_info = {
        'args': dict(request.args),
        'cookies': dict(request.cookies),
        'headers': dict(request.headers)
    }
    
    # Get babel configuration
    babel_config = {
        'default_locale': app.config.get('BABEL_DEFAULT_LOCALE', 'not set'),
        'supported_locales': app.config.get('BABEL_SUPPORTED_LOCALES', []),
        'translation_directories': app.config.get('BABEL_TRANSLATION_DIRECTORIES', 'not set')
    }
    
    # Return all debug information as JSON
    return jsonify({
        'current_locale': current_locale,
        'session_lang': session_lang,
        'translations': translations,
        'request_info': request_info,
        'babel_config': babel_config
    })
"""
    
    with open('debug_endpoint.py', 'w', encoding='utf-8') as f:
        f.write(debug_endpoint_code)
    
    print("\nDebug endpoint script created: 'debug_endpoint.py'")
    print("You can add this code to your app.py to enable a /debug_babel endpoint for detailed Babel debugging.")

# Main function
def main():
    print("=== Flask-Babel Web Translation Debugger ===")
    
    # Test each language
    for lang in ['zh_CN', 'zh_TW', 'en']:
        test_login_page_translations(lang)
    
    # Test direct URL parameters
    test_language_parameters()
    
    # Create debug endpoint script
    create_debug_endpoint_script()
    
    print("\n=== Debug Completed ===")
    print("If Traditional Chinese translations still aren't working, consider:")
    print("1. Adding the /debug_babel endpoint to app.py and checking its output")
    print("2. Verifying that the get_locale() function in app.py is correctly implemented")
    print("3. Checking that the zh_TW .mo file contains the correct translations and is being loaded")

if __name__ == "__main__":
    main()