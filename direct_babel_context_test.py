from flask_babel import Babel, gettext as _, get_translations
from babel import Locale
import os
import sys

# Add the current directory to Python path to import app.py
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import the actual app module
try:
    from app import app as original_app, get_locale
    from flask import g, session
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
    print(f"Flask-Babel version: {original_app.config.get('BABEL_VERSION', 'unknown')}")
    
    # Check if the translations directory exists
    translations_path = os.path.abspath(original_app.config.get('BABEL_TRANSLATION_DIRECTORIES', 'translations'))
    print(f"Absolute translations directory path: {translations_path}")
    print(f"Translations directory exists: {os.path.exists(translations_path)}")
    
    # Check if locale directories exist
    for lang in original_app.config.get('BABEL_SUPPORTED_LOCALES', []):
        locale_dir = os.path.join(translations_path, lang, 'LC_MESSAGES')
        mo_file = os.path.join(locale_dir, 'messages.mo')
        print(f"Locale '{lang}' directory exists: {os.path.exists(locale_dir)}")
        print(f"  messages.mo file exists: {os.path.exists(mo_file)}")
        if os.path.exists(mo_file):
            print(f"  messages.mo file size: {os.path.getsize(mo_file)} bytes")

# Function to directly test Babel translations within the Flask context
def test_direct_translations():
    """Test Babel translations directly within the Flask context"""
    print("\n=== Direct Translation Testing ===")
    
    test_phrases = [
        "作业管理系统",
        "登录", 
        "用户名", 
        "密码",
        "记住我"
    ]
    
    # Test each supported locale
    for locale in original_app.config.get('BABEL_SUPPORTED_LOCALES', []):
        print(f"\n=== Testing with locale: {locale} ===")
        
        # Create a request context
        with original_app.test_request_context('/debug_translation'):
            try:
                # Create a Babel Locale object
                babel_locale = Locale.parse(locale)
                print(f"Created Babel Locale object: {babel_locale}")
                
                # Temporarily set the locale in the session
                session['lang'] = locale
                print(f"Set session['lang'] = {locale}")
                
                # Get the locale selector result
                selected_locale = get_locale()
                print(f"get_locale() returns: {selected_locale}")
                
                # Try to get translations
                translations = get_translations()
                print(f"translations object: {translations}")
                
                if translations:
                    # Test each phrase with direct ugettext
                    print("\nDirect ugettext translations:")
                    for phrase in test_phrases:
                        translated = translations.ugettext(phrase)
                        print(f"  '{phrase}' -> '{translated}'")
                else:
                    print("No translations object available")
                    
            except Exception as e:
                print(f"Error during direct translation test: {e}")

# Function to test the debug_translation endpoint

def test_debug_endpoint():
    """Test the /debug_translation endpoint with different locales"""
    print("\n=== Testing /debug_translation Endpoint ===")
    
    test_phrases = ["用户名", "密码", "登录"]
    test_locales = ['zh_CN', 'zh_TW', 'en']
    
    for phrase in test_phrases:
        for locale in test_locales:
            print(f"\nTesting '{phrase}' in locale '{locale}'")
            response = test_client.get(f'/debug_translation/{locale}/{phrase}')
            
            print(f"Response status code: {response.status_code}")
            try:
                # Try to parse JSON response
                data = response.get_json()
                if data:
                    print(f"Original text: {data.get('original_text')}")
                    print(f"Target locale: {data.get('locale')}")
                    print(f"Translated text: {data.get('translated_text')}")
                    print(f"Babel version: {data.get('babel_version')}")
            except Exception as e:
                print(f"Failed to parse JSON response: {e}")
                print(f"Response content: {response.data.decode('utf-8')}")

# Function to check for known Flask-Babel 4.0.0 compatibility issues
def check_compatibility():
    print("\n=== Flask-Babel Compatibility Check ===")
    
    # Check how Babel is initialized
    print(f"Babel instance: {original_app.extensions.get('babel')}")
    
    # Check if the locale_selector is properly registered
    if hasattr(original_app.extensions.get('babel'), 'locale_selector'):
        print("Locale selector is registered")
    else:
        print("Warning: Locale selector not properly registered")
        
    # Try direct API calls that might behave differently in new versions
    try:
        from flask_babel import get_locale as babel_get_locale
        with original_app.test_request_context('/'):
            current_babel_locale = babel_get_locale()
            print(f"flask_babel.get_locale() returns: {current_babel_locale}")
    except Exception as e:
        print(f"Error calling flask_babel.get_locale(): {e}")

# Main function
def main():
    print("\n===== Flask-Babel Direct Context Debugger =====")
    
    # Debug configuration
    debug_babel_config()
    
    # Check for compatibility issues
    check_compatibility()
    
    # Test direct translations within Flask context
    test_direct_translations()
    
    # Test the debug_translation endpoint
    test_debug_endpoint()
    
    print("\n===== Debugger Completed =====")

if __name__ == "__main__":
    main()