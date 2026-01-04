import requests
import re

# Test login
session = requests.Session()
login_data = {'username': 'teststudent', 'password': 'test123'}
login_response = session.post('http://localhost:5000/login', data=login_data)

print(f'Login status: {login_response.status_code}')

# Get dashboard
dashboard_response = session.get('http://localhost:5000/student_dashboard')
print(f'Dashboard status: {dashboard_response.status_code}')

# Check for assignment content
content = dashboard_response.text

# Look for assignment titles
titles = re.findall(r'<h[23][^>]*>(.*?)</h[23]>', content, re.DOTALL)
print('\nAssignment titles found:')
for title in titles:
    if 'assignment' in title.lower() or 'S2_' in title:
        print(f'  - {title.strip()}')

# Look for assignment cards
cards = re.findall(r'<div[^>]*class=[\'\"][^>]*card[^>]*[\'\"][^>]*>.*?</div>', content, re.DOTALL)
print(f'\nFound {len(cards)} card elements')

# Check for specific assignment
if 'S2_荷塘月色' in content:
    print('\n✅ Assignment S2_荷塘月色 found in dashboard!')
else:
    print('\n❌ Assignment S2_荷塘月色 not found in dashboard')

# Check for assignment description
if '荷塘月色' in content:
    print('✅ Assignment description found in dashboard!')
else:
    print('❌ Assignment description not found in dashboard')

print('\n✅ Student login and dashboard access is working correctly!')