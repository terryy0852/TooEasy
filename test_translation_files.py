from flask import Flask
from flask_babel import Babel, gettext
import os

# Create a minimal Flask app for testing translations
test_app = Flask(__name__)
test_app.config['BABEL_DEFAULT_LOCALE'] = 'zh_CN'
test_app.config['BABEL_SUPPORTED_LOCALES'] = ['zh_CN', 'en', 'zh_TW']

# Initialize Babel
babel = Babel(test_app)

# Test function to check translations
def test_translations():
    print("===== 测试翻译文件有效性 =====")
    
    # Test Simplified Chinese
    print("\n测试简体中文翻译:")
    with test_app.test_request_context(query_string={'lang': 'zh_CN'}):
        babel.locale_selector_func = lambda: 'zh_CN'
        print(f"作业管理系统: {gettext('作业管理系统')}")
        print(f"登录: {gettext('登录')}")
        print(f"注册: {gettext('注册')}")
    
    # Test Traditional Chinese
    print("\n测试繁体中文翻译:")
    with test_app.test_request_context(query_string={'lang': 'zh_TW'}):
        babel.locale_selector_func = lambda: 'zh_TW'
        print(f"作业管理系统: {gettext('作业管理系统')}")
        print(f"登录: {gettext('登录')}")
        print(f"注册: {gettext('注册')}")
    
    # Test English
    print("\n测试英文翻译:")
    with test_app.test_request_context(query_string={'lang': 'en'}):
        babel.locale_selector_func = lambda: 'en'
        print(f"作业管理系统: {gettext('作业管理系统')}")
        print(f"登录: {gettext('登录')}")
        print(f"注册: {gettext('注册')}")
    
    print("\n===== 测试完成 =====")
    print("如果所有语言都能正确显示翻译，则翻译文件有效。")
    print("如果繁体中文显示与简体中文相同，则可能是翻译文件未正确加载或编译。")

if __name__ == "__main__":
    # Ensure we're in the correct directory to load translations
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    test_translations()