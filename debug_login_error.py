import requests
from bs4 import BeautifulSoup

# Test login functionality
login_url = 'http://localhost:5000/login'

print("Testing login page access...")
# Test GET request to login page
response = requests.get(login_url)
print(f"GET status code: {response.status_code}")
print(f"Response headers: {dict(response.headers)}")

# Check if we can see the login form
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    login_form = soup.find('form')
    print(f"Login form found: {login_form is not None}")
    if login_form:
        print(f"Form action: {login_form.get('action')}")
        print(f"Form method: {login_form.get('method')}")

print("\nTesting login with admin credentials...")
# Test POST request with login credentials
data = {
    'username': 'admin',
    'password': 'admin123'
}

response = requests.post(login_url, data=data, allow_redirects=False)
print(f"POST status code: {response.status_code}")
print(f"Response headers: {dict(response.headers)}")
print(f"Location header: {response.headers.get('Location')}")

if response.status_code == 302:
    # Follow the redirect
    redirect_url = response.headers.get('Location')
    if redirect_url:
        print(f"\nFollowing redirect to: {redirect_url}")
        # Fix: Handle relative URLs by combining with base URL
        if not redirect_url.startswith('http'):
            redirect_url = f'http://localhost:5000{redirect_url}'
        dashboard_response = requests.get(redirect_url)
        print(f"Dashboard status code: {dashboard_response.status_code}")
        
        # Check if we got an error page
        if 'Server Error' in dashboard_response.text:
            print("ERROR: Server Error page received")
            # Print the full error page for debugging
            print("\nError page content:")
            print(dashboard_response.text[:2000])  # Print first 2000 chars
        else:
            print("SUCCESS: Dashboard loaded without error")
            soup = BeautifulSoup(dashboard_response.text, 'html.parser')
            print(f"Page title: {soup.title.text if soup.title else 'No title'}")
