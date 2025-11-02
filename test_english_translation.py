import requests

# Test the English translation
BASE_URL = "http://127.0.0.1:5000"

print("Testing English translations...")

# First, switch to English
print("1. Switching to English...")
switch_response = requests.get(f"{BASE_URL}/switch_language/en")
print(f"   Status: {switch_response.status_code}")
print(f"   Redirected to: {switch_response.url}")

# Test the debug endpoint to see current language
print("\n2. Checking current language settings...")
debug_response = requests.get(f"{BASE_URL}/debug_babel")
if debug_response.status_code == 200:
    debug_data = debug_response.json()
    print(f"   Current locale: {debug_data.get('current_locale')}")
    print(f"   Session language: {debug_data.get('session_lang')}")
else:
    print(f"   Debug endpoint failed: {debug_response.status_code}")

# Test the login page to see actual page content
print("\n3. Testing login page content...")
login_response = requests.get(f"{BASE_URL}/login")
if login_response.status_code == 200:
    content = login_response.text
    
    # Check for English translations
    if 'Assignment Management System' in content:
        print("   ✓ Browser tab title is in English")
    else:
        print("   ✗ Browser tab title is NOT in English")
        
    # Check HTML lang attribute
    if 'lang="en"' in content:
        print("   ✓ HTML lang attribute is set to English")
    elif 'lang="zh_CN"' in content:
        print("   ✗ HTML lang attribute is set to Chinese (needs manual ?lang=en parameter)")
    else:
        print("   ? HTML lang attribute not found or different")
else:
    print(f"   Login page failed: {login_response.status_code}")

# Test with explicit language parameter
print("\n4. Testing with explicit language parameter...")
login_en_response = requests.get(f"{BASE_URL}/login?lang=en")
if login_en_response.status_code == 200:
    content = login_en_response.text
    
    if 'lang="en"' in content:
        print("   ✓ HTML lang attribute is set to English with ?lang=en")
    else:
        print("   ✗ HTML lang attribute still not English even with parameter")
else:
    print(f"   Login page with lang parameter failed: {login_en_response.status_code}")

print("\nTest completed!")
print("\nTo see '评分反馈' translation, you need to:")
print("1. Login as a student")
print("2. Go to a submission page where tutor feedback is shown")
print("3. It should show 'Feedback From Your Tutor' instead of '评分反馈'")