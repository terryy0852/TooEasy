#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Simple script to directly test the monkey-patched gettext functions"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the app to get the monkey-patched functions
from app import app
import builtins

# Test function to verify monkey patch functionality
def test_monkey_patch():
    """Test the monkey-patched gettext functions directly"""
    print("===== TESTING MONKEY PATCHED GETTEXT FUNCTIONS =====")
    
    # Check if the monkey patch has been applied
    print(f"\n1. Checking if monkey patch is applied:")
    print(f"   builtins.__dict__['_'] exists: {'_' in builtins.__dict__}")
    print(f"   builtins.__dict__['_with_locale'] exists: {'_with_locale' in builtins.__dict__}")
    
    # Define test strings and locales
    test_strings = ['作业管理系统', '用户名', '密码', '登录']
    test_locales = ['en', 'zh_TW', 'zh_CN']
    
    # Test the _with_locale function directly
    print(f"\n2. Testing _with_locale function directly:")
    for locale in test_locales:
        print(f"\n   Testing locale: {locale}")
        for string in test_strings:
            if '_with_locale' in builtins.__dict__:
                # Use the monkey-patched _with_locale function directly
                result = builtins.__dict__['_with_locale'](string, locale)
                print(f"   '{string}' -> '{result}'")
            else:
                print(f"   ERROR: _with_locale function not found in builtins")
                break
    
    # Test the _ function directly with Flask test context
    print(f"\n3. Testing _ function with Flask test context:")
    with app.test_request_context():
        from flask import session
        
        # Test each locale
        for locale in test_locales:
            print(f"\n   Testing _() with session language: {locale}")
            # Set the session language
            session['lang'] = locale
            
            for string in test_strings:
                if '_' in builtins.__dict__:
                    # Use the monkey-patched _ function
                    result = builtins.__dict__['_'](string)
                    print(f"   '{string}' -> '{result}'")
                else:
                    print(f"   ERROR: _ function not found in builtins")
                    break
    
    print(f"\n===== MONKEY PATCH TEST COMPLETE =====")

if __name__ == "__main__":
    test_monkey_patch()