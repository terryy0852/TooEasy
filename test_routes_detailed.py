import requests

BASE_URL = 'http://127.0.0.1:5000'

def test_route(route, expected_status=200, description=''):
    print(f"\nTesting {route}...")
    if description:
        print(f"   {description}")
    
    try:
        response = requests.get(route, timeout=5)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == expected_status:
            print(f"   ✓ Status matches expected: {expected_status}")
            return True
        elif response.status_code in [302, 303]:
            print(f"   ✓ Redirected to: {response.headers.get('Location', 'Unknown')}")
            return True
        else:
            print(f"   ✗ Status mismatch: got {response.status_code}, expected {expected_status}")
            return False
    
    except requests.exceptions.ConnectionError:
        print(f"   ✗ Connection error - server may not be running")
        return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def main():
    print("Testing Password Management Routes")
    print("=" * 50)
    
    # Test all password-related routes
    test_route(f"{BASE_URL}/login", 200, "Login page with Forgot Password link")
    test_route(f"{BASE_URL}/forgot_password", 200, "Forgot Password page")
    test_route(f"{BASE_URL}/reset_password/test_token", 302, "Reset Password page (should redirect with invalid token)")
    test_route(f"{BASE_URL}/change_password", 302, "Change Password page (requires login)")
    
    # Test dashboard routes for comparison
    test_route(f"{BASE_URL}/student_dashboard", 302, "Student Dashboard (requires login)")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    main()
