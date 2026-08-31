import requests
import json

# Base URL of the application
BASE_URL = "http://localhost:5000"

# Function to test the debug endpoint with a specific language
def test_debug_with_language(lang_code):
    print(f"\n===== Testing debug endpoint with {lang_code} language ======")
    
    # Create a session to persist cookies
    session = requests.Session()
    
    # First, visit the switch_language route to set the language
    switch_url = f"{BASE_URL}/switch_language/{lang_code}"
    print(f"Switching language to {lang_code} at: {switch_url}")
    switch_response = session.get(switch_url)
    print(f"Switch response status: {switch_response.status_code}")
    
    # After switching, visit the debug endpoint
    debug_url = f"{BASE_URL}/debug_babel"
    print(f"Visiting debug endpoint at: {debug_url}")
    response = session.get(debug_url)
    print(f"Debug endpoint response status: {response.status_code}")
    
    # Try to parse the JSON response
    try:
        debug_data = response.json()
        
        # Print key debug information
        print(f"Current locale: {debug_data.get('current_locale', 'not set')}")
        print(f"Session language: {debug_data.get('session_lang', 'not set')}")
        
        # Print Babel configuration
        print("\nBabel configuration:")
        babel_config = debug_data.get('babel_config', {})
        print(f"- Default locale: {babel_config.get('default_locale', 'not set')}")
        print(f"- Supported locales: {babel_config.get('supported_locales', [])}")
        print(f"- Translation directories: {babel_config.get('translation_directories', 'not set')}")
        
        # Print translations
        print("\nTranslations:")
        translations = debug_data.get('translations', {})
        for original, translated in translations.items():
            print(f"- '{original}' -> '{translated}'")
            # Check if Traditional Chinese is being used when expected
            if lang_code == 'zh_TW' and original in ['作业管理系统', '登录', '用户登录', '用户名', '密码']:
                # Traditional Chinese characters have different Unicode values
                # Check if translated text contains Traditional Chinese characters
                if '作業' in translated or '登錄' in translated or '用戶' in translated:
                    print(f"  ✓ Found Traditional Chinese characters in translation")
                else:
                    print(f"  ✗ No Traditional Chinese characters found in translation")
        
        # Print request information (optional)
        # print("\nRequest information:")
        # request_info = debug_data.get('request_info', {})
        # print(f"- Args: {request_info.get('args', {})}")
        
        return debug_data
    except json.JSONDecodeError:
        print(f"Error: Could not parse JSON response. Response content: {response.text}")
        return None

# Main function
def main():
    print("=== Testing Flask-Babel Debug Endpoint ===")
    
    # Test each language
    for lang in ['zh_CN', 'zh_TW', 'en']:
        test_debug_with_language(lang)
    
    print("\n=== Debug Endpoint Tests Completed ===")
    print("If Traditional Chinese translations still aren't working, possible issues:")
    print("1. The .mo file for zh_TW may not be properly compiled or loaded")
    print("2. There might be an issue with how Flask-Babel is detecting the locale")
    print("3. The translations in the .po file might not be correctly mapped to the source strings")

if __name__ == "__main__":
    main()