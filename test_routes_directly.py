# Test Flask routes directly using the Flask test client

import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app
from app import app

def test_routes():
    """Test all main routes directly using the Flask test client"""
    
    with app.test_client() as client:
        print("=== Testing Flask Routes Directly ===")
        
        # Test routes
        routes_to_test = [
            '/health',
            '/',
            '/login',
            '/forgot_password',
            '/reset_password/test-token'  # Test with a dummy token
        ]
        
        for route in routes_to_test:
            try:
                response = client.get(route)
                status_code = response.status_code
                content_length = len(response.data)
                
                print(f"Route: {route}")
                print(f"  Status Code: {status_code}")
                print(f"  Content Length: {content_length} bytes")
                
                # Check if it's a redirect
                if response.location:
                    print(f"  Redirects to: {response.location}")
                    
                # Show first 100 chars if it's a small response
                if content_length < 1000:
                    print(f"  Content Preview: {response.data[:100]!r}...")
                
                print()
            except Exception as e:
                print(f"Error testing {route}: {e}")
                print()

if __name__ == "__main__":
    test_routes()
