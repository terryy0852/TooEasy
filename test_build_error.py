import requests
import sys

BASE_URL = 'http://127.0.0.1:5000'

try:
    # Try to access login page which should trigger the BuildError
    response = requests.get(f'{BASE_URL}/login', timeout=10)
    print(f"Status code: {response.status_code}")
    print(f"Response length: {len(response.text)} bytes")
    
    # Check if it's an HTML response
    if 'text/html' in response.headers.get('Content-Type', ''):
        print("\nResponse (first 500 chars):")
        print(response.text[:500])
        print("\n...")
        print("Response (last 500 chars):")
        print(response.text[-500:])
    else:
        print("\nResponse content:")
        print(response.text)
        
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
    sys.exit(1)
