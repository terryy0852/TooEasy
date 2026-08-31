import requests
import sys

# Define the base URL
BASE_URL = "http://127.0.0.1:5000"

# Function to test translations by language

def test_language(lang_code):
    print(f"\nTesting translations with language code: {lang_code}")
    # Test login page
    login_url = f"{BASE_URL}/login?lang={lang_code}"
    try:
        response = requests.get(login_url)
        if response.status_code == 200:
            content = response.text
            # Print relevant portions of the content for verification
            print(f"Login page status code: {response.status_code}")
            # Check for specific translation strings
            print("Key phrases in response:")
            if "作业管理系统" in content:
                print("- Found Simplified Chinese: 作业管理系统")
            if "作業管理系統" in content:
                print("- Found Traditional Chinese: 作業管理系統")
            if "Assignment Management System" in content:
                print("- Found English: Assignment Management System")
            if "登录" in content:
                print("- Found Simplified Chinese: 登录")
            if "登錄" in content:
                print("- Found Traditional Chinese: 登錄")
            if "Login" in content:
                print("- Found English: Login")
        else:
            print(f"Failed to access login page. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error accessing login page: {e}")

# Run tests
if __name__ == "__main__":
    print("Testing web interface translations...")
    print("====================================")
    
    # Test default language (should be zh_CN)
    print("\n--- Testing default language ---")
    test_language("")
    
    # Test Simplified Chinese
    print("\n--- Testing Simplified Chinese (zh_CN) ---")
    test_language("zh_CN")
    
    # Test Traditional Chinese
    print("\n--- Testing Traditional Chinese (zh_TW) ---")
    test_language("zh_TW")
    
    # Test English
    print("\n--- Testing English (en) ---")
    test_language("en")
    
    print("\n====================================")
    print("Translation test completed.")