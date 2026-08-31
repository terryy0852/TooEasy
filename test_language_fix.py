import requests

# Test the language switching functionality
BASE_URL = "http://127.0.0.1:5000"

print("Testing language switching functionality...")

# Test 1: Switch to English
print("\n1. Switching to English...")
switch_response = requests.get(f"{BASE_URL}/switch_language/en")
print(f"   Status: {switch_response.status_code}")
print(f"   Response: {switch_response.text[:200]}...")

# Test 2: Check if language is set in session
print("\n2. Checking session language...")
session_response = requests.get(f"{BASE_URL}/debug_babel")
if session_response.status_code == 200:
    print(f"   Session language: {session_response.text}")
else:
    print(f"   Debug endpoint failed: {session_response.status_code}")

# Test 3: Try to access tutor dashboard with English
print("\n3. Testing tutor dashboard with English...")
tutor_response = requests.get(f"{BASE_URL}/tutor_dashboard?lang=en")
print(f"   Status: {tutor_response.status_code}")

if tutor_response.status_code == 200:
    content = tutor_response.text
    
    # Check for English content
    if 'Teacher Dashboard' in content or 'tutor_dashboard' in content:
        print("   ✓ Tutor dashboard accessible")
    else:
        print("   ? Tutor dashboard content unclear")
    
    # Check HTML lang attribute
    if 'lang="en"' in content:
        print("   ✓ HTML lang attribute set to English")
    else:
        print("   ✗ HTML lang attribute not set to English")
        
    # Check for Chinese content (should not be present if English is working)
    if '教师仪表盘' in content:
        print("   ✗ Still showing Chinese content")
    else:
        print("   ✓ No Chinese content detected")
else:
    print(f"   Tutor dashboard failed: {tutor_response.status_code}")

print("\nTest completed!")