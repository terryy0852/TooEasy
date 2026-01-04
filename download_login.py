import requests

# Download the login page
url = 'http://127.0.0.1:5001/login'
try:
    response = requests.get(url)
    response.raise_for_status()
    
    # Save the content to a file for inspection
    with open('login_page.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    # Check if our dark mode override is present
    dark_mode_override = 'Browser dark mode override - stronger version'
    if dark_mode_override in response.text:
        print('✓ Dark mode override is present in the page')
    else:
        print('✗ Dark mode override is NOT present in the page')
    
    print(f'Page saved to login_page.html (size: {len(response.text)} bytes)')
    
except Exception as e:
    print(f'Error downloading page: {e}')
