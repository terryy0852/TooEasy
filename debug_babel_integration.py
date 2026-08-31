from flask import Flask, request, session
from flask_babel import Babel, gettext as _
import os
import sys

# Add the current directory to Python path to import app.py
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import the actual app module
try:
    from app import app as original_app, get_locale
    print("Successfully imported app module.")
except ImportError as e:
    print(f"Failed to import app module: {e}")
    sys.exit(1)

# Create a test client for the Flask application
test_client = original_app.test_client()

# Function to debug Babel configuration
def debug_babel_config():
    print("\n=== Flask-Babel Configuration ===")
    print(f"BABEL_DEFAULT_LOCALE: {original_app.config.get('BABEL_DEFAULT_LOCALE')}")
    print(f"BABEL_SUPPORTED_LOCALES: {original_app.config.get('BABEL_SUPPORTED_LOCALES')}")
    print(f"BABEL_TRANSLATION_DIRECTORIES: {original_app.config.get('BABEL_TRANSLATION_DIRECTORIES')}")
    print(f"Current application root path: {original_app.root_path}")
    
    # Check if the translations directory exists
    translations_path = os.path.join(original_app.root_path, original_app.config.get('BABEL_TRANSLATION_DIRECTORIES', 'translations'))
    print(f"Translations directory path: {translations_path}")
    print(f"Translations directory exists: {os.path.exists(translations_path)}")
    
    # Check if locale directories exist
    for lang in original_app.config.get('BABEL_SUPPORTED_LOCALES', []):
        locale_dir = os.path.join(translations_path, lang, 'LC_MESSAGES')
        mo_file = os.path.join(locale_dir, 'messages.mo')
        print(f"Locale '{lang}' directory exists: {os.path.exists(locale_dir)}")
        print(f"  messages.mo file exists: {os.path.exists(mo_file)}")

# Function to test locale selection
def test_locale_selection():
    print("\n=== Testing Locale Selection ===")
    
    # Test with different lang parameters
    test_langs = ['zh_CN', 'zh_TW', 'en', 'invalid']
    
    for lang in test_langs:
        with original_app.test_request_context(f'/login?lang={lang}'):
            # Clear session first to isolate the test
            session.clear()
            
            # Get locale using the application's get_locale function
            selected_locale = get_locale()
            
            # Print the results
            print(f"Requested lang: '{lang}', Selected locale: '{selected_locale}'")
            print(f"Session after locale selection: {dict(session)}")
    
    # Test session persistence
    print("\n=== Testing Session Persistence ===")
    with original_app.test_request_context('/login'):
        # Set session directly
        session['lang'] = 'zh_TW'
        selected_locale = get_locale()
        print(f"With session lang='zh_TW', Selected locale: '{selected_locale}'")

# Function to test translations through Flask test client
def test_web_translations():
    print("\n=== Testing Web Translations ===")
    
    test_langs = ['zh_CN', 'zh_TW', 'en']
    
    for lang in test_langs:
        print(f"\nTesting translations with language: {lang}")
        
        # Clear session first
        with test_client.session_transaction() as sess:
            sess.clear()
            
        # Make a request with the lang parameter
        response = test_client.get(f'/login?lang={lang}')
        content = response.data.decode('utf-8')
        
        print(f"Response status code: {response.status_code}")
        
        # Check for key translation strings
        print("Key phrases in response:")
        if "作业管理系统" in content:
            print("- Found Simplified Chinese: 作业管理系统")
        if "作業管理系統" in content:
            print("- Found Traditional Chinese: 作業管理系統")
        if "Assignment Management System" in content:
            print("- Found English: Assignment Management System")
        if "登录" in content:
            print("- Found Simplified Chinese: 登录")
        if "登錄" in content:
            print("- Found Traditional Chinese: 登錄")
        if "Login" in content:
            print("- Found English: Login")
        
        # Check session after request
        with test_client.session_transaction() as sess:
            print(f"Session lang after request: {sess.get('lang')}")

# Main function
def main():
    print("\n===== Flask-Babel Integration Debugger =====")
    
    # Debug configuration
    debug_babel_config()
    
    # Test locale selection logic
    test_locale_selection()
    
    # Test web translations
    test_web_translations()
    
    print("\n===== Debugger Completed =====")

if __name__ == "__main__":
    main()