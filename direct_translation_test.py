#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Direct test of translation functions
This script tests both direct .mo file loading and our application's translation functions
"""
import os
import sys
from babel.support import Translations
from babel import Locale

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Function to print a decorative separator with title
def print_separator(title):
    """Print a decorative separator with title"""
    print("\n" + "="*60)
    print(f"{title.center(60)}")
    print("="*60)

# Function to load translations directly from .mo files
def test_direct_mo_loading(locale_name, display_name):
    print(f"\nTesting {display_name} ({locale_name}) - Direct .mo file loading:")
    
    # Path to the compiled translations
    mo_file_path = os.path.join('translations', locale_name, 'LC_MESSAGES', 'messages.mo')
    
    if not os.path.exists(mo_file_path):
        print(f"Error: Translation file {mo_file_path} not found!")
        return False
    
    try:
        # Check if the file is empty
        file_size = os.path.getsize(mo_file_path)
        print(f"File size: {file_size} bytes")
        
        if file_size == 0:
            print(f"Error: Translation file {mo_file_path} is empty!")
            return False
            
        # Load the translations
        with open(mo_file_path, 'rb') as f:
            translations = Translations(f)
        
        # Test core translations
        test_strings = [
            "作业管理系统",
            "用户登录",
            "用户名",
            "密码",
            "仪表盘",
            "登录",
            "Invalid username or password"
        ]
        
        success = True
        for string in test_strings:
            translated = translations.ugettext(string)
            print(f"{string} -> {translated}")
            if translated == string and locale_name != 'zh_CN':
                print(f"  WARNING: No translation found for '{string}' in {locale_name}")
                success = False
                
        # Print catalog contents for debugging
        print(f"\nCatalog contains {len(translations._catalog)} entries")
        print(f"Sample entries from catalog: {list(translations._catalog.items())[:5]}")
        
        return success
        
    except Exception as e:
        print(f"Error loading translations: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# Try to import and test the application's translation functions
def test_application_translations():
    print_separator("TESTING APPLICATION TRANSLATION FUNCTIONS")
    
    try:
        # Import the app and translation functions
        from app import app, get_translation_from_file, _
        
        # Test phrases
        phrases = ['用户名', '密码', '登录', '作业管理系统']
        
        # Test with different locales
        locales = [('zh_CN', 'Simplified Chinese'), ('zh_TW', 'Traditional Chinese'), ('en', 'English')]
        
        for locale_name, display_name in locales:
            print(f"\nTesting locale: {display_name} ({locale_name})")
            
            # Test get_translation_from_file
            print("\nTesting get_translation_from_file function:")
            for phrase in phrases:
                translated = get_translation_from_file(phrase, locale_name)
                print(f"  '{phrase}' -> '{translated}'")
                
            # Test monkey-patched _() function
            print("\nTesting monkey-patched _() function:")
            # Temporarily override get_locale function for testing
            if hasattr(app, 'babel') and hasattr(app.babel, 'locale_selector'):
                original_get_locale = app.babel.locale_selector
                try:
                    app.babel.locale_selector = lambda: locale_name
                    for phrase in phrases:
                        translated = _(phrase)
                        print(f"  '{phrase}' -> '{translated}'")
                finally:
                    # Restore original get_locale
                    app.babel.locale_selector = original_get_locale
            else:
                print("  WARNING: Could not override locale selector")
                # Just test the function directly
                for phrase in phrases:
                    translated = _(phrase)
                    print(f"  '{phrase}' -> '{translated}'")
        
    except ImportError as e:
        print(f"Could not import application functions: {e}")
        print("Skipping application translation tests.")
    except Exception as e:
        print(f"Error testing application translations: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Starting translation tests...")
    
    # First test direct .mo file loading
    print_separator("TESTING DIRECT .MO FILE LOADING")
    en_success = test_direct_mo_loading('en', 'English')
    zh_tw_success = test_direct_mo_loading('zh_TW', 'Traditional Chinese')
    zh_cn_success = test_direct_mo_loading('zh_CN', 'Simplified Chinese')
    
    # Then test application translation functions
    test_application_translations()
    
    print("\n" + "="*60)
    print("TRANSLATION TEST SUMMARY".center(60))
    print("="*60)
    print(f"English translations loaded: {'✓' if en_success else '✗'}")
    print(f"Traditional Chinese translations loaded: {'✓' if zh_tw_success else '✗'}")
    print(f"Simplified Chinese translations loaded: {'✓' if zh_cn_success else '✗'}")
    
    print("\nTranslation Test Complete!")
    print("If translations are not showing correctly:")
    print("1. Verify the .po files contain proper translations")
    print("2. Check that the .mo files were successfully compiled")
    print("3. Confirm the directory structure is correct")
    print("4. Verify the translation keys match exactly in the code and .po files")