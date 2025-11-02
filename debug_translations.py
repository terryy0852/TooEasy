from flask import Flask
from flask_babel import Babel, gettext
import os
import sys

# Create a minimal Flask app for testing translations
debug_app = Flask(__name__)
debug_app.config['BABEL_DEFAULT_LOCALE'] = 'zh_CN'
debug_app.config['BABEL_SUPPORTED_LOCALES'] = ['zh_CN', 'en', 'zh_TW']
# Explicitly set the translations directory
debug_app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

# Initialize Babel
babel = Babel(debug_app)

# Debug function to check translations
def debug_translation_loading():
    print("===== 调试翻译文件加载 =====")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"应用根目录: {os.path.dirname(os.path.abspath(__file__))}")
    print(f"Python版本: {sys.version}")
    print(f"BABEL_TRANSLATION_DIRECTORIES: {debug_app.config.get('BABEL_TRANSLATION_DIRECTORIES')}")
    
    # Check if translation files exist
    translation_dirs = debug_app.config.get('BABEL_TRANSLATION_DIRECTORIES', 'translations').split(';')
    for dir_path in translation_dirs:
        full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), dir_path)
        print(f"\n检查翻译目录: {full_path}")
        
        # Check for language directories
        if os.path.exists(full_path):
            lang_dirs = [d for d in os.listdir(full_path) if os.path.isdir(os.path.join(full_path, d))]
            print(f"找到的语言目录: {lang_dirs}")
            
            # Check for .po and .mo files in each language directory
            for lang in lang_dirs:
                lc_messages_path = os.path.join(full_path, lang, 'LC_MESSAGES')
                if os.path.exists(lc_messages_path):
                    po_files = [f for f in os.listdir(lc_messages_path) if f.endswith('.po')]
                    mo_files = [f for f in os.listdir(lc_messages_path) if f.endswith('.mo')]
                    print(f"  {lang} 目录中的 .po 文件: {po_files}")
                    print(f"  {lang} 目录中的 .mo 文件: {mo_files}")
                else:
                    print(f"  {lang} 目录中没有 LC_MESSAGES 文件夹")
        else:
            print(f"翻译目录不存在: {full_path}")
    
    # Test translation loading
    print("\n===== 测试翻译加载 =====")
    
    # Test Simplified Chinese
    print("\n测试简体中文翻译:")
    with debug_app.test_request_context(query_string={'lang': 'zh_CN'}):
        babel.locale_selector_func = lambda: 'zh_CN'
        print(f"作业管理系统: {gettext('作业管理系统')}")
        print(f"登录: {gettext('登录')}")
    
    # Test Traditional Chinese
    print("\n测试繁体中文翻译:")
    with debug_app.test_request_context(query_string={'lang': 'zh_TW'}):
        babel.locale_selector_func = lambda: 'zh_TW'
        print(f"作业管理系统: {gettext('作业管理系统')}")
        print(f"登录: {gettext('登录')}")
    
    # Test English
    print("\n测试英文翻译:")
    with debug_app.test_request_context(query_string={'lang': 'en'}):
        babel.locale_selector_func = lambda: 'en'
        print(f"作业管理系统: {gettext('作业管理系统')}")
        print(f"登录: {gettext('登录')}")
    
    print("\n===== 调试完成 =====")
    print("如果所有语言都显示相同内容，则翻译文件未正确加载。")
    print("请检查翻译文件的编译状态和Babel配置。")

if __name__ == "__main__":
    debug_translation_loading()