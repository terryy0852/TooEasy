from flask import Flask
from flask_babel import Babel, gettext as _
import os

# Function to create a test app with a specific locale selector
def create_test_app(locale_to_use):
    app = Flask(__name__)
    app.config['BABEL_DEFAULT_LOCALE'] = 'zh_CN'
    app.config['BABEL_SUPPORTED_LOCALES'] = ['zh_CN', 'en', 'zh_TW', 'zh_Hant']
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
    
    # Create a locale selector that always returns the specified locale
    def locale_selector():
        return locale_to_use
    
    # Initialize Babel with the custom locale selector
    Babel(app, locale_selector=locale_selector)
    
    return app

# Function to test translations with different locales
def test_translations():
    print("\n===== Testing Alternative Locale Codes =====")
    
    # List of locales to test, including alternative Traditional Chinese codes
    locales = ['zh_CN', 'en', 'zh_TW', 'zh_Hant']
    
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

# Function to check if we need to create symlink for zh_Hant

def check_and_create_symlink():
    print("\n===== Checking Traditional Chinese Locale Setup =====")
    
    # Paths
    translations_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'translations')
    zh_tw_dir = os.path.join(translations_dir, 'zh_TW', 'LC_MESSAGES')
    zh_hant_dir = os.path.join(translations_dir, 'zh_Hant', 'LC_MESSAGES')
    
    print(f"zh_TW directory: {zh_tw_dir}")
    print(f"zh_TW directory exists: {os.path.exists(zh_tw_dir)}")
    print(f"zh_Hant directory: {zh_hant_dir}")
    print(f"zh_Hant directory exists: {os.path.exists(zh_hant_dir)}")
    
    # If zh_Hant doesn't exist but zh_TW does, create a symlink
    if os.path.exists(zh_tw_dir) and not os.path.exists(zh_hant_dir):
        print("\nCreating symlink from zh_TW to zh_Hant...")
        try:
            # Create parent directories if needed
            os.makedirs(os.path.dirname(zh_hant_dir), exist_ok=True)
            
            # Create a symbolic link (Windows requires admin privileges for symlinks, so we'll copy instead)
            # Copy the MO file instead of symlinking for better compatibility
            zh_tw_mo = os.path.join(zh_tw_dir, 'messages.mo')
            zh_hant_mo = os.path.join(zh_hant_dir, 'messages.mo')
            
            if os.path.exists(zh_tw_mo):
                import shutil
                shutil.copy2(zh_tw_mo, zh_hant_mo)
                print(f"Copied {zh_tw_mo} to {zh_hant_mo}")
            else:
                print(f"Error: {zh_tw_mo} does not exist")
        except Exception as e:
            print(f"Error creating symlink or copying file: {e}")

# Main function
def main():
    # Check and create symlink if needed
    check_and_create_symlink()
    
    # Test translations
    test_translations()
    
    print("\n===== Test Completed =====")

if __name__ == "__main__":
    main()