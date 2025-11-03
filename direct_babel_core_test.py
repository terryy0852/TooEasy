#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Directly test Babel core API with translation files to bypass Flask-Babel"""

import os
import sys
from babel.support import Translations
from babel import Locale

# Set paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TRANSLATIONS_DIR = os.path.join(BASE_DIR, 'translations')

# Test phrases
test_phrases = [
    '作业管理系统',
    '登录',
    '用户登录',
    '用户名',
    '密码'
]

# Locales to test
locales = ['zh_CN', 'zh_TW', 'en']

# Function to load translations directly

def load_translations(locale_code):
    """Load translations directly using Babel's core API"""
    try:
        # Create locale object
        locale = Locale.parse(locale_code)
        print(f"Loading translations for locale: {locale}")
        print(f"Locale display name: {locale.display_name}")
        
        # Path to the .mo file
        mo_file_path = os.path.join(TRANSLATIONS_DIR, locale_code, 'LC_MESSAGES', 'messages.mo')
        print(f"Looking for .mo file at: {mo_file_path}")
        
        # Check if file exists
        if not os.path.exists(mo_file_path):
            print(f"[ERROR] .mo file not found at {mo_file_path}")
            
            # Try alternative path formats
            alt_path_1 = os.path.join(TRANSLATIONS_DIR, locale.language, 'LC_MESSAGES', 'messages.mo')
            alt_path_2 = os.path.join(TRANSLATIONS_DIR, f'{locale.language}_{locale.territory}', 'LC_MESSAGES', 'messages.mo')
            
            print(f"Looking for alternative paths: {alt_path_1}, {alt_path_2}")
            return None
        
        # Check file size
        file_size = os.path.getsize(mo_file_path)
        print(f".mo file size: {file_size} bytes")
        
        # Load translations
        with open(mo_file_path, 'rb') as f:
            translations = Translations(f)
        
        print(f"Successfully loaded translations")
        return translations
    except Exception as e:
        print(f"[ERROR] Failed to load translations: {e}")
        return None

# Function to test translations
def test_translations(translations, locale_code):
    """Test translations for a given locale"""
    if not translations:
        print(f"[ERROR] No translations loaded for {locale_code}")
        return False
    
    all_success = True
    for phrase in test_phrases:
        try:
            # Try translating
            translated = translations.ugettext(phrase)
            
            # Print results
            print(f"Original: '{phrase}' -> Translated: '{translated}'")
            
            # Check if translation is different from original (except for default locale)
            if locale_code != 'zh_CN' and translated == phrase:
                print(f"[WARNING] Translation for '{phrase}' is the same as original in locale {locale_code}")
                all_success = False
            
            # For zh_TW, check if it contains Traditional Chinese characters
            if locale_code == 'zh_TW':
                # Check for common Traditional Chinese characters
                has_traditional = any(char in '作業管理系統登錄使用者名稱密' for char in translated)
                if not has_traditional:
                    print(f"[WARNING] Translation for '{phrase}' does not appear to be Traditional Chinese: '{translated}'")
                    all_success = False
        except Exception as e:
            print(f"[ERROR] Failed to translate '{phrase}': {e}")
            all_success = False
    
    return all_success

# Main function
def main():
    print("Direct Babel Core API Translation Test")
    print("=" * 60)
    
    # Check if translations directory exists
    if not os.path.exists(TRANSLATIONS_DIR):
        print(f"[ERROR] Translations directory not found at {TRANSLATIONS_DIR}")
        sys.exit(1)
    
    print(f"Using translations directory: {TRANSLATIONS_DIR}")
    
    # List all files in translations directory for debugging
    print("\nFiles in translations directory:")
    for root, dirs, files in os.walk(TRANSLATIONS_DIR):
        level = root.replace(TRANSLATIONS_DIR, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 4 * (level + 1)
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            print(f'{subindent}{file} ({file_size} bytes)')
    
    # Test each locale
    results = {}
    for locale_code in locales:
        print(f"\n" + "=" * 60)
        print(f"Testing locale: {locale_code}")
        
        # Load translations
        translations = load_translations(locale_code)
        
        # Test translations
        success = test_translations(translations, locale_code)
        results[locale_code] = success
    
    # Print summary
    print(f"\n" + "=" * 60)
    print("Translation Test Summary:")
    
    all_success = True
    for locale_code, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{locale_code}: {status}")
        if not success:
            all_success = False
    
    # Recommendations
    print(f"\n" + "=" * 60)
    if all_success:
        print("All translations tests passed!")
        print("\nThis confirms that your .mo files are correctly formatted and contain the expected translations.")
        print("The issue is likely with how Flask-Babel is configured to load these translations.")
        print("\nRecommended actions:")
        print("1. Check Flask-Babel's configuration in app.py")
        print("2. Verify the BABEL_TRANSLATION_DIRECTORIES path is correct")
        print("3. Check how the locale_selector function is implemented")
        print("4. Consider using this direct Babel API approach in your application")
    else:
        print("Some translation tests failed.")
        print("\nRecommended actions:")
        print("1. Verify your .po files are correctly translated")
        print("2. Recompile your .po files to .mo using:")
        print("   pybabel compile -d translations -l zh_TW")
        print("   pybabel compile -d translations -l en")
        print("3. Check that your .mo files are in the correct directory structure")
        print("4. Ensure your .mo files contain the expected translations")
    
    sys.exit(0 if all_success else 1)

if __name__ == "__main__":
    main()