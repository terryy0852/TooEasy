import requests
import re

# Test to find untranslated Chinese content on tutor dashboard
session = requests.Session()

print("Switching to English...")
response = session.get('http://127.0.0.1:5000/switch_language/en')
print(f"Switch language status: {response.status_code}")

print("\nAccessing tutor dashboard...")
response = session.get('http://127.0.0.1:5000/tutor_dashboard')
print(f"Tutor dashboard status: {response.status_code}")

print("\n=== SEARCHING FOR UNTRANSLATED CHINESE CONTENT ===")

# Find all Chinese characters in the response
chinese_matches = re.findall(r'[\u4e00-\u9fff]+', response.text)

if chinese_matches:
    print(f"Found {len(chinese_matches)} Chinese text occurrences:")
    unique_chinese = list(set(chinese_matches))
    print(f"Unique Chinese phrases: {unique_chinese}")
    
    # Get context around the Chinese text
    print("\n=== CONTEXT AROUND CHINESE TEXT ===")
    for chinese_text in unique_chinese:
        # Find the Chinese text with some context
        pattern = re.compile(f'.{{0,20}}{re.escape(chinese_text)}.{{0,20}}')
        context_matches = pattern.findall(response.text)
        
        for match in context_matches[:3]:  # Show first 3 occurrences
            print(f"Context: '{match.strip()}'")
            
            # Check if this might be in a translation tag
            if '{{' in match and '}}' in match:
                print("  ^ This appears to be inside a template tag")
            else:
                print("  ^ This appears to be hardcoded content")
else:
    print("No Chinese characters found in the response!")

print("\n=== CHECKING HTML STRUCTURE ===")
# Look for common untranslated elements
patterns_to_check = [
    r'<title[^>]*>(.*?)</title>',
    r'<h1[^>]*>(.*?)</h1>',
    r'<h2[^>]*>(.*?)</h2>',
    r'<h3[^>]*>(.*?)</h3>',
    r'<p[^>]*>(.*?)</p>',
    r'<a[^>]*>(.*?)</a>',
    r'<button[^>]*>(.*?)</button>',
    r'placeholder="([^"]*)"',
    r'alt="([^"]*)"'
]

for pattern in patterns_to_check:
    matches = re.findall(pattern, response.text, re.IGNORECASE)
    chinese_in_matches = [m for m in matches if re.search(r'[\u4e00-\u9fff]', m)]
    
    if chinese_in_matches:
        print(f"Found Chinese in {pattern}: {chinese_in_matches}")