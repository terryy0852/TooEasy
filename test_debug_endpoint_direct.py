import requests
import json
import sys
import os

# Define URLs
BASE_URL = "http://127.0.0.1:5000"

# Test phrases
TEST_PHRASES = {
    '作业管理系统': 'system',
    '登录': 'login',
    '用户登录': 'user_login',
    '用户名': 'username',
    '密码': 'password'
}

# Expected Traditional Chinese translations (as confirmed in verify_mo_file.py)
EXPECTED_TRAD_CHINESE = {
    '作业管理系统': '作業管理系統',
    '登录': '登錄',
    '用户登录': '使用者登錄',  # Or similar Traditional Chinese translation
    '用户名': '使用者名稱',  # Or similar
    '密码': '密碼'
}

# Function to test a specific translation

def test_translation(locale, text):
    """Test translation for a specific locale and text"""
    # Format the URL with locale and text
    url = f"{BASE_URL}/debug_translation/{locale}/{requests.utils.quote(text)}"
    
    try:
        # Make the request
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"[ERROR] Request failed with status code: {response.status_code}")
            print(f"URL: {url}")
            return None, False
        
        # Parse JSON response
        data = response.json()
        return data, True
    except Exception as e:
        print(f"[ERROR] Exception during request: {e}")
        print(f"URL: {url}")
        return None, False

# Function to analyze translation result
def analyze_translation(data, expected_text=None):
    """Analyze and print translation result"""
    original = data.get('original_text', '')
    locale = data.get('locale', '')
    translated = data.get('translated_text', '')
    config = data.get('config', {})
    babel_version = data.get('babel_version', 'unknown')
    
    print(f"\nTesting '{original}' in locale '{locale}':")
    print(f"Original text: '{original}'")
    print(f"Translated text: '{translated}'")
    print(f"Flask-Babel version: {babel_version}")
    print(f"Default locale: {config.get('default_locale', 'unknown')}")
    print(f"Supported locales: {config.get('supported_locales', 'unknown')}")
    print(f"Translation dirs: {config.get('translation_dirs', 'unknown')}")
    print(f"Current get_locale(): {config.get('current_get_locale', 'unknown')}")
    
    # Check if translation matches expected
    success = True
    if expected_text:
        if translated == expected_text:
            print(f"✓ Translation matches expected: '{expected_text}'")
        else:
            print(f"✗ Translation does not match expected: '{expected_text}'")
            success = False
    
    # For zh_TW, check if translated text contains Traditional Chinese characters
    if locale == 'zh_TW':
        has_traditional = any(char in '作業管理系統登錄使用者名稱密' for char in translated)
        if has_traditional:
            print(f"✓ Translation contains Traditional Chinese characters")
        else:
            print(f"✗ Translation does not contain Traditional Chinese characters")
            success = False
    
    return success

# Main function
def main():
    print("Direct Translation Endpoint Test")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code != 200:
            print(f"[ERROR] Server is running but returned status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("[ERROR] Server not running. Please start the Flask server first with 'python app.py'")
        sys.exit(1)
    
    # Test all languages and phrases
    results = []
    
    # Test Simplified Chinese (zh_CN)
    print("\n=== Testing zh_CN Translations ===")
    for text, _ in TEST_PHRASES.items():
        data, success = test_translation('zh_CN', text)
        if success:
            # For zh_CN, we expect the text to remain unchanged
            result = analyze_translation(data, text)
            results.append(result)
    
    # Test Traditional Chinese (zh_TW)
    print("\n=== Testing zh_TW Translations ===")
    for text, key in TEST_PHRASES.items():
        data, success = test_translation('zh_TW', text)
        if success:
            # For zh_TW, we expect Traditional Chinese characters
            expected = EXPECTED_TRAD_CHINESE.get(text, text)
            result = analyze_translation(data, expected)
            results.append(result)
    
    # Test English (en)
    print("\n=== Testing en Translations ===")
    for text, _ in TEST_PHRASES.items():
        data, success = test_translation('en', text)
        if success:
            # For en, we just check if it's different from the original Chinese text
            result = analyze_translation(data)
            results.append(result)
    
    # Print summary
    print("\n" + "=" * 50)
    print("Translation Test Summary:")
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r)
    
    print(f"Total tests: {total_tests}")
    print(f"Passed tests: {passed_tests}")
    print(f"Failed tests: {total_tests - passed_tests}")
    
    # Check if any tests failed
    if passed_tests != total_tests:
        print("\nSome translation tests failed.")
        print("\nRecommended actions:")
        print("1. Check server logs for [BABEL DEBUG] messages")
        print("2. Verify that .mo files are correctly compiled and loaded")
        print("3. Ensure Babel is properly configured with correct locale paths")
        print("4. Check Flask-Babel version compatibility")
        print("5. Try using the direct Babel API instead of Flask-Babel's template functions")
        sys.exit(1)
    else:
        print("\nAll translation tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()