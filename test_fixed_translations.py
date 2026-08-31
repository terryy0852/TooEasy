import requests
import json

# Base URL of the application
BASE_URL = "http://localhost:5000"

# Function to test the debug endpoint with a specific language
def test_with_language(lang_code):
    print(f"\n===== Testing {lang_code} translations ======")
    
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
        
        # Print translations
        print("\nTranslations:")
        translations = debug_data.get('translations', {})
        
        # Special check for Traditional Chinese
        if lang_code == 'zh_TW':
            traditional_found = False
            
            for original, translated in translations.items():
                print(f"- '{original}' -> '{translated}'")
                # Check if Traditional Chinese characters are used
                if '作業' in translated or '登錄' in translated or '用戶' in translated:
                    print(f"  ✓ Found Traditional Chinese characters: '{translated}'")
                    traditional_found = True
            
            if traditional_found:
                print("\n✓ SUCCESS: Traditional Chinese translations are working correctly!")
            else:
                print("\n✗ FAILED: Traditional Chinese translations are not being used.")
        else:
            # For other languages, just print translations
            for original, translated in translations.items():
                print(f"- '{original}' -> '{translated}'")
        
        return debug_data
        
    except json.JSONDecodeError:
        print(f"Error: Could not parse JSON response. Response content: {response.text}")
        return None

# Main function
def main():
    print("=== Testing Fixed Flask-Babel Translations ===")
    
    print("This script tests if the Traditional Chinese translations are working after our fixes.")
    print("We've modified the app.py to use the explicit babel.locale_selector assignment")
    print("which should help Flask-Babel properly load the correct translations.")
    
    # First test Simplified Chinese (zh_CN) as a baseline
    test_with_language('zh_CN')
    
    # Then test Traditional Chinese (zh_TW) - this is our main focus
    test_with_language('zh_TW')
    
    # Finally test English (en)
    test_with_language('en')
    
    print("\n=== Translation Test Completed ===")
    
    # Provide recommendations based on the most likely outcome
    print("\nIf Traditional Chinese translations are still not working:")
    print("1. Try restarting the Flask server")
    print("2. Clear your browser cache and cookies")
    print("3. Check the Flask server logs for any locale selection messages")
    print("4. Verify the translations directory structure and file permissions")
    
    print("\nIf Traditional Chinese translations are working:")
    print("✓ Great! The fix has worked.")
    print("  - We successfully resolved the issue by explicitly setting babel.locale_selector")
    print("  - This ensures Flask-Babel 4.0.0 properly uses the selected locale")

if __name__ == "__main__":
    main()