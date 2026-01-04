import requests
import re

BASE_URL = 'http://127.0.0.1:5000'

# Get the login page to see the form structure
session = requests.Session()
response = session.get(f'{BASE_URL}/login')
content = response.text

print(f'Login page status: {response.status_code}')
print(f'Session cookies: {dict(session.cookies)}')

# Look for form-related elements
print('\nLooking for form elements...')

# Look for input fields with more specific patterns
username_fields = re.findall(r'<input[^>]*name=["\']username["\'][^>]*>', content)
password_fields = re.findall(r'<input[^>]*name=["\']password["\'][^>]*>', content)
submit_buttons = re.findall(r'<(input|button)[^>]*type=["\']submit["\'][^>]*>', content)

print(f'- Username fields found: {len(username_fields)}')
for field in username_fields:
    print(f'  {field}')

print(f'- Password fields found: {len(password_fields)}')
for field in password_fields:
    print(f'  {field}')

print(f'- Submit buttons found: {len(submit_buttons)}')
for button in submit_buttons:
    print(f'  {button}')

# Look for form action
form_actions = re.findall(r'<form[^>]*action=["\']([^"\']+)["\']', content)
print(f'- Form actions: {form_actions}')

# Look for any error messages
if 'error' in content.lower():
    print('- Error message found in content')
if 'invalid' in content.lower():
    print('- Invalid credentials message found')

# Look for the actual form content
form_match = re.search(r'<form[^>]*>(.*?)</form>', content, re.DOTALL)
if form_match:
    print('\nForm content:')
    print(form_match.group(1)[:1000])

print('\nFirst 2000 characters of login page:')
print(content[:2000])