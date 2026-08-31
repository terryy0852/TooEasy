from flask import Flask
from flask_babel import Babel, gettext as _
from babel import Locale

# Function to create an app with a specific locale

def create_app(locale):
    app = Flask(__name__)
    app.config['BABEL_DEFAULT_LOCALE'] = locale
    app.config['BABEL_SUPPORTED_LOCALES'] = ['zh_CN', 'en', 'zh_TW']
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
    
    # Initialize Babel
    babel = Babel(app)
    
    return app

# Test function for a specific locale
def test_locale(locale_name, display_name):
    print(f"\nTesting {display_name} ({locale_name}):")
    
    # Create app with the specific locale
    app = create_app(locale_name)
    
    # Test core translations
    with app.app_context():
        print(f'{_("作业管理系统")}')
        print(f'{_("用户登录")}')
        print(f'{_("用户名")}')
        print(f'{_("密码")}')
        print(f'{_("仪表盘")}')
        print(f'{_("Invalid username or password")}')

if __name__ == "__main__":
    # Test each supported locale
    test_locale('zh_CN', 'Simplified Chinese')
    test_locale('en', 'English')
    test_locale('zh_TW', 'Traditional Chinese')
    
    # Additional verification
    print("\nTranslation Verification Complete!")
    print("If you don't see proper translations above, check the following:")
    print("1. Make sure the .po files contain correct translations")
    print("2. Verify that the .mo files were successfully compiled")
    print("3. Check that the translations directory structure is correct")