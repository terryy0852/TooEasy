# Test the url_for function directly with the app context
from app import app

with app.test_request_context():
    print("Testing url_for function...")
    
    try:
        from flask import url_for
        
        # Test different endpoints
        print(f"Login URL: {url_for('login')}")
        print(f"Register URL: {url_for('register')}")
        print(f"Change Password URL: {url_for('change_password')}")
        print(f"Forgot Password URL: {url_for('forgot_password')}")
        print(f"Reset Password URL: {url_for('reset_password', token='test_token')}")
        print(f"Logout URL: {url_for('logout')}")
        
        print("\nAll URLs generated successfully!")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
