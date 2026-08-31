import requests

BASE_URL = 'http://127.0.0.1:5001'

def test_route(url, description, should_contain=None):
    try:
        response = requests.get(url, timeout=10)
        print(f"{description}: Status {response.status_code}")
        if response.status_code == 200:
            if should_contain and should_contain in response.text:
                print(f"   ✓ Contains expected content: '{should_contain}'")
            else:
                print(f"   ✓ Successfully accessed")
            return True
        else:
            print(f"   ✗ Failed: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

print("Testing standalone password reset app...")
print("=" * 50)

# Test all the routes
test_route(f'{BASE_URL}/login', '1. Login page', 'Forgot Password')
test_route(f'{BASE_URL}/forgot_password', '2. Forgot password page', 'email address')
test_route(f'{BASE_URL}/reset_password/test_token', '3. Reset password page (with invalid token)', 'Invalid or expired reset token')

print("\n" + "=" * 50)
print("Testing form submission...")

# Test submitting the forgot password form
try:
    response = requests.post(
        f'{BASE_URL}/forgot_password',
        data={'email': 'test@example.com'},
        timeout=10,
        allow_redirects=True
    )
    print(f"4. Forgot password form submission: Status {response.status_code}")
    if response.status_code == 200 and "reset token" in response.text:
        print("   ✓ Successfully generated reset token")
    else:
        print("   ✗ Failed")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\nAll tests completed!")
