import requests
from bs4 import BeautifulSoup
import time

# Base URL of the Flask application
BASE_URL = "http://127.0.0.1:5000"

# Test function to verify language switching flow
def test_language_switching_flow():
    """Test the complete language switching flow and verify translations"""
    print("===== TESTING LANGUAGE SWITCHING FLOW =====")
    
    # Supported locales to test
    locales = ['en', 'zh_TW', 'zh_CN']
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # First, clear any existing session by visiting the home page
    print(f"\nClearing session by visiting home page: {BASE_URL}/")
    session.get(BASE_URL + '/', timeout=5)
    
    # For each locale, test the complete flow
    for locale in locales:
        print(f"\n===== Testing language flow for: {locale} =====")
        
        # Step 1: Switch language using the dedicated route
        print(f"1. Switching language via /switch_language/{locale}")
        switch_url = f"{BASE_URL}/switch_language/{locale}"
        switch_response = session.get(switch_url, timeout=5, allow_redirects=True)
        print(f"   Status code: {switch_response.status_code}")
        print(f"   Final URL: {switch_response.url}")
        
        # Wait a moment to ensure the session is updated
        time.sleep(1)
        
        # Step 2: Visit the login page directly to check translations
        print(f"2. Visiting login page to check translations")
        login_url = f"{BASE_URL}/login"
        login_response = session.get(login_url, timeout=5)
        print(f"   Status code: {login_response.status_code}")
        
        # Parse the login page to check translations
        soup = BeautifulSoup(login_response.text, 'html.parser')
        
        # Check for key translated elements
        print(f"3. Checking translations on the login page:")
        
        # Check the title
        title = soup.title.string if soup.title else "No title"
        print(f"   Title: {title}")
        
        # Check h2 heading (should be 'User Login' in English, etc.)
        h2_heading = soup.find('h2').text.strip() if soup.find('h2') else "No h2 heading"
        print(f"   Heading: {h2_heading}")
        
        # Check username label
        username_label = ""
        for label in soup.find_all('label'):
            if 'username' in label.get('for', '').lower() or '用户名' in label.text:
                username_label = label.text.strip()
                break
        print(f"   Username label: {username_label}")
        
        # Check password label
        password_label = ""
        for label in soup.find_all('label'):
            if 'password' in label.get('for', '').lower() or '密码' in label.text:
                password_label = label.text.strip()
                break
        print(f"   Password label: {password_label}")
        
        # Check login button
        login_button = ""
        for button in soup.find_all('button', type='submit'):
            login_button = button.text.strip()
            break
        print(f"   Login button: {login_button}")
        
        # Check if translations are as expected
        expected_translations = {
            'en': {
                'title_contains': 'Login',
                'heading': 'User Login',
                'username': 'Username',
                'password': 'Password',
                'login': 'Login'
            },
            'zh_TW': {
                'title_contains': '登錄',
                'heading': '用戶登錄',
                'username': '用戶名',
                'password': '密碼',
                'login': '登錄'
            },
            'zh_CN': {
                'title_contains': '登录',
                'heading': '用户登录',
                'username': '用户名',
                'password': '密码',
                'login': '登录'
            }
        }
        
        expected = expected_translations.get(locale, {})
        print(f"4. Verifying translations against expected values:")
        print(f"   Title contains '{expected.get('title_contains')}': {'✓' if expected.get('title_contains') in title else '✗'}")
        print(f"   Heading is '{expected.get('heading')}': {'✓' if h2_heading == expected.get('heading') else '✗'}")
        print(f"   Username label is '{expected.get('username')}': {'✓' if username_label == expected.get('username') else '✗'}")
        print(f"   Password label is '{expected.get('password')}': {'✓' if password_label == expected.get('password') else '✗'}")
        print(f"   Login button is '{expected.get('login')}': {'✓' if login_button == expected.get('login') else '✗'}")
        
        # Step 5: Check the debug_babel endpoint
        print(f"5. Checking debug_babel endpoint for detailed info")
        debug_url = f"{BASE_URL}/debug_babel"
        debug_response = session.get(debug_url, timeout=5)
        print(f"   Status code: {debug_response.status_code}")
        
        if debug_response.status_code == 200:
            debug_data = debug_response.json()
            print(f"   Session language: {debug_data.get('session_lang')}")
            print(f"   Current locale: {debug_data.get('current_locale')}")
            print(f"   Monkey patched: {debug_data.get('monkey_patched')}")
            print(f"   With locale available: {debug_data.get('with_locale_available')}")
            
            # Print translations for this locale from debug data
            print(f"   Translations for {locale} from debug endpoint:")
            locale_translations = debug_data.get('multi_locale_translations', {}).get(locale, {})
            for original, translated in locale_translations.items():
                print(f"     '{original}' -> '{translated}'")
        
        print(f"===== Completed testing for: {locale} =====")
        
    print("\n===== LANGUAGE FLOW TEST COMPLETE =====")
    print("Check the Flask server logs for detailed debug information")

# Main function
def main():
    print(f"Testing language switching flow for Flask application at {BASE_URL}")
    print("Make sure the Flask server is running with debug mode enabled")
    
    # Run the language switching flow test
    test_language_switching_flow()

if __name__ == "__main__":
    main()