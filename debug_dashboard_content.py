import requests
import re

BASE_URL = 'http://127.0.0.1:5000'

# Test login with correct credentials
session = requests.Session()
login_data = {'username': 'teststudent', 'password': 'test123'}

print('Testing login with teststudent/test123...')
response = session.post(f'{BASE_URL}/login', data=login_data, allow_redirects=False)

# Follow redirect to dashboard
location = response.headers.get('Location')
if location:
    redirect_response = session.get(f'{BASE_URL}{location}' if location.startswith('/') else location)
    
    # Get dashboard content
    content = redirect_response.text
    print('Dashboard content preview (first 1000 chars):')
    print(content[:1000])
    
    # Look for assignment-related content
    if 'assignment' in content.lower():
        print('\n✅ Assignment keyword found!')
        
        # Look for card elements or assignment containers
        cards = re.findall(r'<div[^>]*class=["\'][^"\']*card["\'][^>]*>', content)
        print('Found {} card elements'.format(len(cards)))
        
        # Look for any titles
        all_titles = re.findall(r'<h[1-6][^>]*>([^<]+)</h[1-6]>', content)
        print('All titles found: {}'.format(all_titles))
        
        # Look for assignment-specific patterns
        assignment_titles = re.findall(r'<h[35][^>]*>([^<]*assignment[^<]*)</h[35]>', content, re.IGNORECASE)
        print('Assignment-related titles: {}'.format(assignment_titles))
        
        # Look for assignment cards specifically
        assignment_cards = re.findall(r'<div[^>]*class=["\'][^"\']*assignment[^"\']*["\'][^>]*>(.*?)</div>', content, re.DOTALL)
        print('Found {} assignment cards'.format(len(assignment_cards)))
        
    else:
        print('\n❌ No assignment keyword found')
        
    # Check if there's a "no assignments" message
    if 'no assignments' in content.lower():
        print('Found "no assignments" message')
        
else:
    print('❌ No redirect location found')