import requests
import json

# Base URL of the Flask application
BASE_URL = "http://127.0.0.1:5000"

# Test function to call the debug_babel endpoint
def test_debug_babel_endpoint():
    """Test the debug_babel endpoint directly to get detailed translation debugging"""
    print("===== DEBUG BABEL ENDPOINT TEST =====")
    
    # URL for the debug_babel endpoint
    debug_url = f"{BASE_URL}/debug_babel"
    
    try:
        # Make a GET request to the debug_babel endpoint
        print(f"Making request to: {debug_url}")
        response = requests.get(debug_url, timeout=10)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            
            # Print key information from the response
            print(f"\nCurrent locale: {data.get('current_locale')}")
            print(f"Session language: {data.get('session_lang')}")
            print(f"Monkey patched: {data.get('monkey_patched')}")
            print(f"With locale available: {data.get('with_locale_available')}")
            
            # Print translations for the current locale
            print("\nTranslations for current locale:")
            current_translations = data.get('current_translations', {})
            for original, translated in current_translations.items():
                print(f"  '{original}' -> '{translated}'")
                # Highlight if translation didn't change
                if original == translated:
                    print(f"  WARNING: No translation for '{original}'")
            
            # Print translations for all locales
            print("\nTranslations for all supported locales:")
            multi_locale = data.get('multi_locale_translations', {})
            for locale, translations in multi_locale.items():
                print(f"\n  {locale}:")
                for original, translated in translations.items():
                    print(f"    '{original}' -> '{translated}'")
                    # Highlight if translation didn't change
                    if original == translated:
                        print(f"    WARNING: No translation for '{original}' in {locale}")
            
            # Check translation file status
            print("\nTranslation file status:")
            file_status = data.get('babel_config', {}).get('translations_file_status', {})
            for locale, status in file_status.items():
                print(f"\n  {locale}:")
                print(f"    Path: {status.get('path')}")
                print(f"    Exists: {status.get('exists')}")
                print(f"    Size: {status.get('size_bytes')} bytes")
                print(f"    Readable: {status.get('readable')}")
                
            return True
        else:
            print(f"Error accessing debug_babel endpoint: Status code {response.status_code}")
            print(f"Response content: {response.text}")
            return False
    except Exception as e:
        print(f"Exception when accessing debug_babel endpoint: {str(e)}")
        return False

# Test function to try the debug_translation endpoint
def test_debug_translation_endpoint():
    """Test the debug_translation endpoint with specific locale and text"""
    print("\n===== DEBUG TRANSLATION ENDPOINT TEST =====")
    
    # Test cases with different locales and texts
    test_cases = [
        ('zh_CN', '登录'),
        ('en', '登录'),
        ('zh_TW', '登录'),
        ('zh_CN', '作业管理系统'),
        ('en', '作业管理系统'),
        ('zh_TW', '作业管理系统'),
        ('zh_CN', '用户名'),
        ('en', '用户名'),
        ('zh_TW', '用户名')
    ]
    
    for locale, text in test_cases:
        try:
            # Construct the URL for the debug_translation endpoint
            debug_url = f"{BASE_URL}/debug_translation/{locale}/{text}"
            print(f"\nMaking request to: {debug_url}")
            
            # Make the GET request
            response = requests.get(debug_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"  Original: '{text}'")
                print(f"  Translated: '{data.get('translated_text')}'")
                print(f"  Locale: {data.get('locale')}")
                print(f"  Method used: {data.get('method_used')}")
                print(f"  MO file found: {data.get('mo_file_found')}")
            else:
                print(f"  Error: Status code {response.status_code}")
        except Exception as e:
            print(f"  Exception: {str(e)}")

# Main function
def main():
    """Main function to run all debug endpoint tests"""
    print(f"Testing Flask application debug endpoints at {BASE_URL}")
    print("Make sure the Flask server is running with debug mode enabled")
    
    # Test the main debug_babel endpoint
    debug_babel_success = test_debug_babel_endpoint()
    
    if debug_babel_success:
        # Then test the specific debug_translation endpoint
        test_debug_translation_endpoint()
    
    print("\n===== DEBUG TEST COMPLETE =====")
    print("Check the Flask server logs for detailed debug information from the monkey-patched gettext function")

if __name__ == "__main__":
    main()