import requests

BASE_URL = 'http://127.0.0.1:5000'

def test_routes():
    print("Testing password management routes...")
    print("=" * 50)
    
    # Test login page
    print("\n1. Testing login page...")
    response = requests.get(f"{BASE_URL}/login")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✓ Login page accessible")
        if 'Forgot Password?' in response.text:
            print("   ✓ 'Forgot Password?' link found on login page")
        else:
            print("   ✗ 'Forgot Password?' link NOT found")
    
    # Test forgot_password page
    print("\n2. Testing forgot_password page...")
    response = requests.get(f"{BASE_URL}/forgot_password")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✓ Forgot password page accessible")
        if 'Forgot Password' in response.text:
            print("   ✓ Forgot password form found")
    
    # Test change_password page (requires login, should redirect)
    print("\n3. Testing change_password page...")
    response = requests.get(f"{BASE_URL}/change_password")
    print(f"   Status: {response.status_code}")
    print(f"   Redirect location: {response.headers.get('Location', 'None')}")
    if response.status_code in [302, 303]:
        print("   ✓ Change password page redirects as expected (login required)")
    
    print("\n" + "=" * 50)
    print("All tests completed!")

if __name__ == "__main__":
    test_routes()
