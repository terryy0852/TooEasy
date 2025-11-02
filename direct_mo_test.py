#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to directly test MO file translations"""

import os
from babel.support import Translations

# Test function to directly verify MO file functionality
def test_mo_files_directly():
    """Directly test translations from MO files"""
    print("===== DIRECT MO FILE TEST =====")
    
    # Define test strings and locales
    test_strings = ['作业管理系统', '用户名', '密码', '登录']
    test_locales = ['en', 'zh_TW', 'zh_CN']
    
    # Get absolute path to translations directory
    translations_dir = os.path.abspath('translations')
    print(f"Using translations directory: {translations_dir}")
    
    # Test each locale
    for locale in test_locales:
        print(f"\n===== Testing locale: {locale} =====")
        
        # Construct the path to the MO file
        mo_file_path = os.path.join(translations_dir, locale, 'LC_MESSAGES', 'messages.mo')
        print(f"Looking for MO file at: {mo_file_path}")
        
        # Check if the file exists
        if not os.path.exists(mo_file_path):
            print(f"ERROR: MO file not found at {mo_file_path}")
            continue
        
        # Get file size for info
        file_size = os.path.getsize(mo_file_path)
        print(f"Found MO file (size: {file_size} bytes)")
        
        try:
            # Load the MO file directly
            with open(mo_file_path, 'rb') as f:
                translations = Translations(f)
                
            # Test each string
            for string in test_strings:
                # Try both gettext and ugettext
                gettext_result = translations.gettext(string)
                ugettext_result = getattr(translations, 'ugettext', lambda x: x)(string)
                
                # Use the first non-empty result
                result = gettext_result if gettext_result != string else ugettext_result
                
                print(f"'{string}' -> '{result}' (gettext: '{gettext_result}', ugettext: '{ugettext_result}')")
        except Exception as e:
            print(f"ERROR loading or using MO file: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print(f"\n===== DIRECT MO FILE TEST COMPLETE =====")

if __name__ == "__main__":
    test_mo_files_directly()