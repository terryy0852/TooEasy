import requests
import json

# Test phrases to translate
test_phrases = ["用户名", "密码", "登录", "作业管理系统"]

# Test locales
test_locales = ['zh_CN', 'zh_TW', 'en']

# Base URL for the debug endpoint
BASE_URL = "http://127.0.0.1:5000"

# Function to test the debug_translation endpoint
def test_debug_translation():
    print("===== Testing Enhanced Debug Translation Endpoint =====\n")
    
    for phrase in test_phrases:
        print(f"\n===== Testing translation for: '{phrase}' =====")
        
        for locale in test_locales:
            # Construct the URL for the debug endpoint
            url = f"{BASE_URL}/debug_translation/{locale}/{phrase}"
            print(f"\nTesting URL: {url}")
            
            try:
                # Make the request to the debug endpoint
                response = requests.get(url)
                
                # Check if the request was successful
                if response.status_code == 200:
                    # Parse the JSON response
                    result = response.json()
                    
                    # Print the results
                    print(f"  Target locale: {result.get('target_locale')}")
                    print(f"  Original text: {result.get('original_text')}")
                    print(f"  Translated text: {result.get('translated_text')}")
                    print(f"  get_translations result: {result.get('get_translations_result')}")
                    print(f"  Direct .mo file result: {result.get('direct_mo_file_result')}")
                    print(f"  Session locale: {result.get('session_locale')}")
                    print(f"  Babel version: {result.get('babel_version')}")
                    
                    # Check if the translation is different from the original
                    if result.get('translated_text') != phrase:
                        print("  ✓ Translation successful!")
                    else:
                        print("  ✗ Translation did not change the text")
                        
                else:
                    print(f"  ✗ Request failed with status code: {response.status_code}")
                    print(f"  Response content: {response.text}")
                    
            except Exception as e:
                print(f"  ✗ Error: {e}")

# Function to test the babel_config endpoint
def test_babel_config():
    print("\n===== Testing Babel Configuration Endpoint =====")
    
    try:
        response = requests.get(f"{BASE_URL}/babel_config")
        
        if response.status_code == 200:
            config = response.json()
            print("Babel Configuration:")
            for key, value in config.items():
                print(f"  {key}: {value}")
        else:
            print(f"Request failed with status code: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

# Main function
def main():
    # Test the babel_config endpoint first
    test_babel_config()
    
    # Then test the debug_translation endpoint
    test_debug_translation()
    
    print("\n===== Test Completed =====")

if __name__ == "__main__":
    main()