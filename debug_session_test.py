import requests
import re

# Test session and language handling
session = requests.Session()

print("1. Testing language switch...")
response = session.get('http://127.0.0.1:5000/switch_language/en')
print(f"Switch language status: {response.status_code}")

print("\n2. Testing debug endpoint to check session language...")
response = session.get('http://127.0.0.1:5000/debug_babel')
print(f"Debug endpoint status: {response.status_code}")
if response.status_code == 200:
    debug_data = response.json()
    print(f"Current locale: {debug_data.get('current_locale')}")
    print(f"Session lang: {debug_data.get('session_lang')}")
    print(f"Request args: {debug_data.get('request_args')}")

print("\n3. Testing tutor dashboard with session...")
response = session.get('http://127.0.0.1:5000/tutor_dashboard')
print(f"Tutor dashboard status: {response.status_code}")

# Check HTML lang attribute
lang_match = re.search(r'<html lang="([^"]+)"', response.text)
if lang_match:
    print(f"HTML lang attribute: {lang_match.group(1)}")
else:
    print("HTML lang attribute not found")

# Check for Chinese content
chinese_chars = re.search(r'[\u4e00-\u9fff]', response.text[:500])
if chinese_chars:
    print("✓ Chinese content detected")
else:
    print("✗ No Chinese content detected")