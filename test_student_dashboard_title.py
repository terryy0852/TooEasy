import requests

# Test the student dashboard title translation
BASE_URL = "http://127.0.0.1:5000"

print("Testing student dashboard title translation...")

# First, switch to English
print("1. Switching to English...")
switch_response = requests.get(f"{BASE_URL}/switch_language/en")
print(f"   Status: {switch_response.status_code}")

# Test the student dashboard page
print("\n2. Testing student dashboard page...")
student_response = requests.get(f"{BASE_URL}/student_dashboard?lang=en")
if student_response.status_code == 200:
    content = student_response.text
    
    # Check if the English title appears
    if 'Student Dashboard - Assignment Management System' in content:
        print("   ✓ Student dashboard title is correctly translated to English")
    elif '学生仪表盘 - 作业管理系统' in content:
        print("   ✗ Student dashboard title is still in Chinese")
    else:
        print("   ? Title not found or different format")
        
    # Check HTML title tag
    if '<title>Student Dashboard - Assignment Management System</title>' in content:
        print("   ✓ HTML title tag is correctly set to English")
    else:
        print("   ✗ HTML title tag is not in English")
        
    # Check HTML lang attribute
    if 'lang="en"' in content:
        print("   ✓ HTML lang attribute is set to English")
    else:
        print("   ✗ HTML lang attribute is not set to English")
else:
    print(f"   Student dashboard page failed: {student_response.status_code}")

print("\nTest completed!")
print("\nIf the title is still in Chinese, try:")
print("1. Hard refresh your browser (Ctrl+F5)")
print("2. Clear browser cache")
print("3. Use incognito/private browsing mode")