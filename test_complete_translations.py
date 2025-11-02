from flask import Flask, render_template_string, g, session
import requests
import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the actual app
try:
    from app import app, get_locale, _
    print("Successfully imported the app module.")
except ImportError as e:
    print(f"Failed to import app module: {e}")
    sys.exit(1)

# Create a test client
test_client = app.test_client()

# Define a simple template for testing
test_template = '''
<!DOCTYPE html>
<html>
<head><title>Translation Test</title></head>
<body>
    <h1>{{ '作业管理系统' | debug_trans }}</h1>
    <p>{{ '登录' | debug_trans }}</p>
    <p>{{ '用户名' | debug_trans }}</p>
    <p>{{ '密码' | debug_trans }}</p>
    <p>{{ '记住我' | debug_trans }}</p>
    <p>Current locale: {{ current_locale }}</p>
</body>
</html>
'''

# Add a test route to the app for direct template testing
@app.route('/test_template')
def test_template_route():
    """Test route to verify template translations"""
    current_locale = get_locale()
    
    # Also test the monkey-patched _() function
    translated_texts = {
        'login': _('登录'),
        'username': _('用户名'),
        'password': _('密码'),
        'remember': _('记住我'),
        'system': _('作业管理系统')
    }
    
    print(f"[TEST] Server-side translations with locale {current_locale}:")
    for key, value in translated_texts.items():
        print(f"  {key}: '{value}'")
    
    # Render the test template
    return render_template_string(test_template, current_locale=current_locale)

# Function to test translations with different locales
def test_translations():
    """Comprehensive test of the translation system"""
    print("\n===== COMPREHENSIVE TRANSLATION TEST =====\n")
    
    # Test phrases
    test_phrases = ["用户名", "密码", "登录", "作业管理系统"]
    
    # Test locales
    test_locales = ['zh_CN', 'zh_TW', 'en']
    
    # 1. Test the debug_translation endpoint
    print("\n=== TESTING DEBUG TRANSLATION ENDPOINT ===")
    for locale in test_locales:
        print(f"\nTesting with locale: {locale}")
        
        # Clear session first
        with test_client.session_transaction() as sess:
            sess.clear()
        
        # Set the locale in the session
        session_response = test_client.get(f'/switch_language/{locale}')
        
        for phrase in test_phrases:
            url = f'/debug_translation/{locale}/{phrase}'
            response = test_client.get(url)
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"  '{phrase}' -> '{data.get('translated_text')}'")
                print(f"  (Method: {data.get('direct_mo_file_result') != phrase and 'Direct .mo file' or 'Fallback'})")
            else:
                print(f"  ✗ Request failed for '{phrase}': {response.status_code}")
    
    # 2. Test the test_template route
    print("\n=== TESTING TEMPLATE TRANSLATIONS ===")
    for locale in test_locales:
        print(f"\nTesting template with locale: {locale}")
        
        # Clear session first
        with test_client.session_transaction() as sess:
            sess.clear()
        
        # Set the locale
        test_client.get(f'/switch_language/{locale}')
        
        # Access the test template route
        response = test_client.get('/test_template')
        content = response.data.decode('utf-8')
        
        if response.status_code == 200:
            print(f"  Template rendered successfully")
            print(f"  Checking for key translations:")
            
            # Check for expected translations
            if locale == 'zh_CN':
                if '作业管理系统' in content: print("    ✓ Found Simplified Chinese system name")
                if '登录' in content: print("    ✓ Found Simplified Chinese login")
            elif locale == 'zh_TW':
                if '作業管理系統' in content: print("    ✓ Found Traditional Chinese system name")
                if '登錄' in content: print("    ✓ Found Traditional Chinese login")
            elif locale == 'en':
                if 'Assignment Management System' in content: print("    ✓ Found English system name")
                if 'Login' in content: print("    ✓ Found English login")
                if 'Username' in content: print("    ✓ Found English username")
                if 'Password' in content: print("    ✓ Found English password")
        else:
            print(f"  ✗ Template request failed: {response.status_code}")
    
    # 3. Test the monkey-patched _() function directly
    print("\n=== TESTING MONKEY-PATCHED _() FUNCTION ===")
    
    with app.test_request_context():
        # Test with different locales
        for locale in test_locales:
            # Set the locale in the session
            session['lang'] = locale
            
            print(f"\nTesting _() with locale: {locale}")
            print(f"  get_locale() returns: {get_locale()}")
            
            for phrase in test_phrases:
                translated = _(phrase)
                print(f"  '{phrase}' -> '{translated}'")
                
                # Verify the translation is correct
                expected = None
                if locale == 'zh_TW' and phrase == '登录':
                    expected = '登錄'
                elif locale == 'zh_TW' and phrase == '作业管理系统':
                    expected = '作業管理系統'
                elif locale == 'en' and phrase == '用户名':
                    expected = 'Username'
                elif locale == 'en' and phrase == '密码':
                    expected = 'Password'
                elif locale == 'en' and phrase == '登录':
                    expected = 'Login'
                elif locale == 'en' and phrase == '作业管理系统':
                    expected = 'Assignment Management System'
                
                if expected and translated == expected:
                    print(f"    ✓ Correct translation")
                elif expected:
                    print(f"    ✗ Incorrect translation. Expected: '{expected}'")

# Run the tests
if __name__ == "__main__":
    try:
        test_translations()
        print("\n===== TEST COMPLETED =====")
    except Exception as e:
        print(f"\n===== TEST FAILED WITH ERROR =====")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()