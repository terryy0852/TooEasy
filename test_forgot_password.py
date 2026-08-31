import requests

BASE_URL = 'http://127.0.0.1:5000'

try:
    print("Testing forgot_password route...")
    response = requests.get(f'{BASE_URL}/forgot_password', timeout=10)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        print("✓ Forgot password page is accessible!")
        print(f"Response length: {len(response.text)} bytes")
        print("\nPage content (first 300 chars):")
        print(response.text[:300])
    else:
        print(f"✗ Error: Status code {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
except requests.exceptions.RequestException as e:
    print(f"✗ Request error: {e}")
    import traceback
    traceback.print_exc()
