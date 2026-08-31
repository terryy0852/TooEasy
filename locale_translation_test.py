import os
import sys
import json
from babel.support import Translations

# Test function to simulate _with_locale

def _with_locale(string, locale):
    """Simulate the _with_locale function to test translations with different locales"""
    print(f"[TEST] Testing translation of '{string}' for locale: {locale}")
    
    # Define the translation directory
    trans_dir = 'translations'
    
    # Construct the path to the .mo file
    mo_file_path = os.path.join(trans_dir, locale, 'LC_MESSAGES', 'messages.mo')
    print(f"[TEST] Looking for MO file at: {mo_file_path}")
    
    # Check if the MO file exists
    if not os.path.exists(mo_file_path):
        print(f"[TEST] WARNING: MO file does not exist for locale: {locale}")
        return string  # Return original string if file not found
    
    # Check file size
    file_size = os.path.getsize(mo_file_path)
    print(f"[TEST] MO file size: {file_size} bytes")
    
    # Try to load the translations
    try:
        with open(mo_file_path, 'rb') as f:
            translations = Translations(f)
            print(f"[TEST] Successfully loaded Translations object")
            
            # Inspect the translations object
            print(f"[TEST] Translations object methods: {[method for method in dir(translations) if not method.startswith('_')]}")
            print(f"[TEST] Translations object has gettext: {hasattr(translations, 'gettext')}")
            print(f"[TEST] Translations object has ugettext: {hasattr(translations, 'ugettext')}")
            
            # Try to translate using different methods
            result = None
            
            # Try gettext first
            if hasattr(translations, 'gettext'):
                print(f"[TEST] Trying gettext method")
                result = translations.gettext(string)
                print(f"[TEST] gettext result: '{result}'")
            
            # If gettext didn't work or returned the same string, try ugettext
            if result == string and hasattr(translations, 'ugettext'):
                print(f"[TEST] Trying ugettext method")
                result = translations.ugettext(string)
                print(f"[TEST] ugettext result: '{result}'")
            
            # Return the translated string or the original if translation didn't change
            return result if result != string else string
    except Exception as e:
        print(f"[TEST] ERROR loading translations: {str(e)}")
        import traceback
        traceback.print_exc()
        return string

# Main test function
def main():
    """Main test function to verify translations across all supported locales"""
    print("\n===== STARTING LOCALE TRANSLATION TEST =====\n")
    
    # Define the locales to test
    supported_locales = ['zh_CN', 'en', 'zh_TW']
    
    # Define test strings
    test_strings = ["用户名", "密码", "登录", "作业管理系统"]
    
    # Test each string with each locale
    all_results = {}
    for locale in supported_locales:
        print(f"\n----- Testing locale: {locale} -----")
        locale_results = {}
        
        for string in test_strings:
            translated = _with_locale(string, locale)
            locale_results[string] = translated
            
            # Check if translation actually happened
            if translated != string:
                print(f"[TEST] SUCCESS: '{string}' translated to '{translated}'")
            else:
                print(f"[TEST] WARNING: No translation found for '{string}' in locale {locale}")
        
        all_results[locale] = locale_results
    
    # Print summary of results
    print("\n===== TRANSLATION TEST SUMMARY =====")
    print(json.dumps(all_results, ensure_ascii=False, indent=2))
    
    # Check for specific translation issues we've observed
    print("\n===== TARGETED ISSUE CHECK =====")
    
    # Check if zh_TW translations are working correctly
    if 'zh_TW' in all_results:
        zh_tw_login = all_results['zh_TW'].get('登录', '')
        if zh_tw_login == '登錄':
            print("[TEST] PASSED: zh_TW translation for '登录' is correct ('登錄')")
        else:
            print(f"[TEST] FAILED: zh_TW translation for '登录' should be '登錄' but got '{zh_tw_login}'")
        
        zh_tw_system = all_results['zh_TW'].get('作业管理系统', '')
        if zh_tw_system == '作業管理系統':
            print("[TEST] PASSED: zh_TW translation for '作业管理系统' is correct ('作業管理系統')")
        else:
            print(f"[TEST] FAILED: zh_TW translation for '作业管理系统' should be '作業管理系統' but got '{zh_tw_system}'")
    
    # Check if English translations are working correctly
    if 'en' in all_results:
        en_username = all_results['en'].get('用户名', '')
        if en_username.lower() == 'username':
            print("[TEST] PASSED: en translation for '用户名' is correct ('Username')")
        else:
            print(f"[TEST] FAILED: en translation for '用户名' should be 'Username' but got '{en_username}'")
        
        en_login = all_results['en'].get('登录', '')
        if en_login.lower() == 'login':
            print("[TEST] PASSED: en translation for '登录' is correct ('Login')")
        else:
            print(f"[TEST] FAILED: en translation for '登录' should be 'Login' but got '{en_login}'")
    
    print("\n===== TEST COMPLETED =====")

if __name__ == '__main__':
    main()