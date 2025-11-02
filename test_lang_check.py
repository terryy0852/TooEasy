import requests

print("Testing tutor dashboard language...")

# Access tutor dashboard with English
response = requests.get('http://127.0.0.1:5000/tutor_dashboard?lang=en')
print(f"Status: {response.status_code}")

html = response.text

# Check if HTML contains lang attribute
if 'lang="en"' in html:
    print("✓ HTML lang attribute set to English")
else:
    print("✗ HTML lang attribute not set to English")
    
# Check what lang attribute is actually set to
import re
lang_match = re.search(r'lang="([^"]*)"', html)
if lang_match:
    print(f"Actual lang attribute: {lang_match.group(1)}")

# Check for Chinese content
chinese_chars = any(ord(c) > 127 for c in html[:500])
if chinese_chars:
    print("✓ Chinese content detected")
else:
    print("✗ No Chinese content detected")

print("\nTest completed!")