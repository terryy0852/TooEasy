import requests
from bs4 import BeautifulSoup

# Test login functionality
def test_login():
    # Test GET request to login page
    print("Testing GET request to login page...")
    response = requests.get('http://localhost:5000/login')
    print(f"GET response status: {response.status_code}")
    
    if response.status_code == 200:
        print("✓ Login page accessible")
        
        # Test POST request with correct credentials
        print("\nTesting POST request with correct credentials...")
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        response = requests.post('http://localhost:5000/login', data=login_data, allow_redirects=True)
        print(f"POST response status: {response.status_code}")
        print(f"POST response URL: {response.url}")
        
        if response.status_code == 200 and 'dashboard' in response.url:
            print("✓ Login successful, redirected to dashboard")
            
            # Parse the dashboard page to check if it loads correctly
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else 'No title'
            print(f"Dashboard page title: {title}")
            
            # Check for welcome message
            welcome_message = soup.find(string=lambda text: "Welcome" in text if text else False)
            if welcome_message:
                print(f"✓ Welcome message found: {welcome_message.strip()}")
            else:
                print("✗ Welcome message not found")
                
        else:
            print("✗ Login failed or not redirected to dashboard")
            print("Response content snippet:")
            print(response.text[:500])
    else:
        print("✗ Login page not accessible")

if __name__ == "__main__":
    test_login()