import requests
from bs4 import BeautifulSoup
import sys
import os

# Define URLs
BASE_URL = "http://127.0.0.1:5000"
TEST_PAGE_URL = f"{BASE_URL}/test_translations"
SWITCH_LANG_URL = f"{BASE_URL}/switch_language/"

# Define test phrases and expected characters
TEST_PHRASES = {
    'system': '作业管理系统',  # Simplified Chinese
    'system_tw': '作業管理系統',  # Traditional Chinese
    'login': '登录',         # Simplified Chinese
    'login_tw': '登錄',      # Traditional Chinese
    'username': '用户名',    # Simplified Chinese
    'username_tw': '使用者名稱', # Traditional Chinese (possible alternative)
    'password': '密码',      # Simplified Chinese
    'password_tw': '密碼'    # Traditional Chinese
}

# Function to test translations for a specific language
def test_language(lang):
    print(f"\n=== Testing {lang} translations ===")
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Switch language
    switch_response = session.get(f"{SWITCH_LANG_URL}{lang}")
    if switch_response.status_code != 200:
        print(f"[ERROR] Failed to switch language to {lang}. Status code: {switch_response.status_code}")
        return False
    
    # Visit test page with language parameter
    test_response = session.get(f"{TEST_PAGE_URL}?lang={lang}")
    if test_response.status_code != 200:
        print(f"[ERROR] Failed to access test page for {lang}. Status code: {test_response.status_code}")
        return False
    
    # Parse HTML
    soup = BeautifulSoup(test_response.text, 'html.parser')
    
    # Check HTML language attribute
    html_lang = soup.html.get('lang', '')
    print(f"HTML language attribute: {html_lang}")
    
    # Extract all translated text sections
    standard_translations = []
    debug_translations = []
    
    # Find all translation test divs
    translation_tests = soup.find_all(class_='translation-test')
    for i, test in enumerate(translation_tests):
        original = test.find(class_='original-text').get_text(strip=True)
        translated = test.find(class_='translated-text').get_text(strip=True)
        
        if i < 5:  # First 5 are standard translations
            standard_translations.append((original, translated))
            print(f"Standard: '{original}' -> '{translated}'")
        else:  # Next 5 are debug translations
            debug_translations.append((original, translated))
            print(f"Debug: '{original}' -> '{translated}'")
    
    # Check for Traditional Chinese characters if testing zh_TW
    success = True
    if lang == 'zh_TW':
        print("\nChecking for Traditional Chinese characters in zh_TW translations:")
        # Check system name
        system_trans = next((t for o, t in standard_translations if o == TEST_PHRASES['system']), '')
        if TEST_PHRASES['system_tw'] in system_trans:
            print(f"✓ Found Traditional Chinese for 'system': '{system_trans}'")
        else:
            print(f"✗ Did not find Traditional Chinese for 'system': '{system_trans}'")
            success = False
        
        # Check login
        login_trans = next((t for o, t in standard_translations if o == TEST_PHRASES['login']), '')
        if TEST_PHRASES['login_tw'] in login_trans:
            print(f"✓ Found Traditional Chinese for 'login': '{login_trans}'")
        else:
            print(f"✗ Did not find Traditional Chinese for 'login': '{login_trans}'")
            success = False
    
    # Check for English if testing en locale
    elif lang == 'en':
        print("\nChecking for English translations in en locale:")
        has_english = False
        for original, translated in standard_translations:
            if any(char.isalpha() for char in translated) and translated != original:
                has_english = True
                print(f"✓ Found English-like translation: '{original}' -> '{translated}'")
                break
        if not has_english:
            print("✗ No English translations detected, still showing Chinese characters")
            success = False
    
    # Also check debug translations
    if lang == 'zh_TW':
        print("\nChecking debug_trans filter output for Traditional Chinese:")
        system_debug = next((t for o, t in debug_translations if o == TEST_PHRASES['system']), '')
        login_debug = next((t for o, t in debug_translations if o == TEST_PHRASES['login']), '')
        
        print(f"Debug filter system: '{system_debug}'")
        print(f"Debug filter login: '{login_debug}'")
        
        if TEST_PHRASES['system_tw'] in system_debug:
            print("✓ Found Traditional Chinese in debug_trans for 'system'")
        else:
            print("✗ Did not find Traditional Chinese in debug_trans for 'system'")
            success = False
    
    return success

# Main function
def main():
    print("Testing web translations with enhanced debug filter")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code != 200:
            print(f"[ERROR] Server is running but returned status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("[ERROR] Server not running. Please start the Flask server first with 'python app.py'")
        sys.exit(1)
    
    # Test all languages
    results = {
        'zh_CN': test_language('zh_CN'),
        'zh_TW': test_language('zh_TW'),
        'en': test_language('en')
    }
    
    # Print summary
    print("\n" + "=" * 50)
    print("Translation Test Summary:")
    for lang, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{lang}: {status}")
    
    # Check if any tests failed
    if not all(results.values()):
        print("\nSome translation tests failed.")
        print("\nRecommended actions:")
        print("1. Check server logs for [BABEL DEBUG] messages")
        print("2. Verify that .mo files are correctly compiled and loaded")
        print("3. Check if the debug_trans filter is correctly registered in app.py")
        print("4. Ensure Babel is properly configured with correct locale paths")
        print("5. Try clearing your browser cache or using a private browsing session")
        sys.exit(1)
    else:
        print("\nAll translation tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()