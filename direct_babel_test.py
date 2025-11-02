from flask import Flask
from flask_babel import Babel, gettext as _
import os

# Function to create a test app with a specific locale selector
def create_test_app(locale_to_use):
    app = Flask(__name__)
    app.config['BABEL_DEFAULT_LOCALE'] = 'zh_CN'
    app.config['BABEL_SUPPORTED_LOCALES'] = ['zh_CN', 'en', 'zh_TW']
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
    
    # Create a locale selector that always returns the specified locale
    def locale_selector():
        return locale_to_use
    
    # Initialize Babel with the custom locale selector
    Babel(app, locale_selector=locale_selector)
    
    return app

# Function to test translations with different locales
def test_translations():
    print("\n===== Direct Babel Translation Test =====")
    
    # List of locales to test
    locales = ['zh_CN', 'en', 'zh_TW']
    
    # Key phrases to test
    test_phrases = [
        "作业管理系统",
        "用户登录",
        "用户名",
        "密码",
        "登录"
    ]
    
    # Test each locale
    for locale in locales:
        print(f"\nTesting translations with locale: {locale}")
        
        # Create a new app instance with the specific locale selector
        test_app = create_test_app(locale)
        
        # Use a test request context
        with test_app.test_request_context():
            # Test each phrase
            for phrase in test_phrases:
                translated = _(phrase)
                print(f"  '{phrase}' -> '{translated}'")

# Function to check Babel configuration
def check_babel_config():
    print("\n===== Flask-Babel Configuration Check =====")
    
    # Create a temporary test app for configuration checking
    temp_app = Flask(__name__)
    temp_app.config['BABEL_DEFAULT_LOCALE'] = 'zh_CN'
    temp_app.config['BABEL_SUPPORTED_LOCALES'] = ['zh_CN', 'en', 'zh_TW']
    temp_app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
    
    # Print configuration
    print(f"BABEL_DEFAULT_LOCALE: {temp_app.config.get('BABEL_DEFAULT_LOCALE')}")
    print(f"BABEL_SUPPORTED_LOCALES: {temp_app.config.get('BABEL_SUPPORTED_LOCALES')}")
    print(f"BABEL_TRANSLATION_DIRECTORIES: {temp_app.config.get('BABEL_TRANSLATION_DIRECTORIES')}")
    
    # Check if the translations directory exists
    translations_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                    temp_app.config.get('BABEL_TRANSLATION_DIRECTORIES', 'translations'))
    print(f"Translations directory path: {translations_path}")
    print(f"Translations directory exists: {os.path.exists(translations_path)}")
    
    # Check if locale directories exist
    for lang in temp_app.config.get('BABEL_SUPPORTED_LOCALES', []):
        locale_dir = os.path.join(translations_path, lang, 'LC_MESSAGES')
        mo_file = os.path.join(locale_dir, 'messages.mo')
        print(f"Locale '{lang}' directory exists: {os.path.exists(locale_dir)}")
        print(f"  messages.mo file exists: {os.path.exists(mo_file)}")
        if os.path.exists(mo_file):
            print(f"  messages.mo file size: {os.path.getsize(mo_file)} bytes")
    
    return temp_app

# Main function
def main():
    # Check configuration first
    temp_app = check_babel_config()
    
    # Test translations
    test_translations()
    
    print("\n===== Test Completed =====")

if __name__ == "__main__":
    main()