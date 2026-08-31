from flask import Flask
from flask_babel import Babel, gettext as _
import os

app = Flask(__name__)

# Configure Babel
app.config['BABEL_DEFAULT_LOCALE'] = 'zh_CN'
app.config['BABEL_SUPPORTED_LOCALES'] = ['zh_CN', 'en', 'zh_TW']
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

babel = Babel(app)

# Use the new approach for locale selection in Flask-Babel 4.0.0
# Since we need to test multiple locales in a single script,
# we'll create separate app instances for each test

# For testing multiple locales in a single script,
# we need to manually set the locale context for each test

if __name__ == "__main__":
    # Test Simplified Chinese (default)
    print("\nTesting Simplified Chinese (zh_CN):")
    with app.app_context():
        print(_("作业管理系统"))
        print(_("用户登录"))
        print(_("用户名"))
        print(_("密码"))
        print(_("仪表盘"))
    
    # Test English
    print("\nTesting English (en):")
    os.environ['BABEL_DEFAULT_LOCALE'] = 'en'
    with app.app_context():
        print(_("作业管理系统"))
        print(_("用户登录"))
        print(_("用户名"))
        print(_("密码"))
        print(_("仪表盘"))
    
    # Test Traditional Chinese
    print("\nTesting Traditional Chinese (zh_TW):")
    os.environ['BABEL_DEFAULT_LOCALE'] = 'zh_TW'
    with app.app_context():
        print(_("作业管理系统"))
        print(_("用户登录"))
        print(_("用户名"))
        print(_("密码"))
        print(_("仪表盘"))
        print(_("Invalid username or password"))