# Debug script to test login with correct password
from app import app, db, User, login_user
from flask_login import FlaskLoginClient
from werkzeug.security import check_password_hash

with app.app_context():
    print("=== Testing Login with Correct Password ===")
    
    # Get test teacher
    test_teacher = User.query.filter_by(username='testteacher').first()
    if test_teacher:
        print(f"Test teacher found: {test_teacher.username}")
        
        # Test password hash directly
        correct_pwd = 'password123'
        is_valid = check_password_hash(test_teacher.password_hash, correct_pwd)
        print(f"Direct password check for '{correct_pwd}': {'Valid' if is_valid else 'Invalid'}")
        
        # Test Flask-Login authentication
        app.test_client_class = FlaskLoginClient
        with app.test_client() as client:
            # Test login form submission
            response = client.post('/login', data={
                'username': 'testteacher',
                'password': correct_pwd
            }, follow_redirects=True)
            
            print(f"\nLogin POST response status: {response.status_code}")
            print(f"Response data preview: {response.data[:300]}")
            
            # Check if login was successful
            if b'Dashboard' in response.data:
                print("✓ Login successful - Dashboard found in response")
            else:
                print("✗ Login failed - Dashboard not found")
            
            # Try with wrong password
            response_wrong = client.post('/login', data={
                'username': 'testteacher',
                'password': 'wrongpass'
            }, follow_redirects=True)
            
            if b'Invalid username or password' in response_wrong.data:
                print("✓ Correctly rejected wrong password")
            else:
                print("✗ Wrong password was accepted")
    
    print("\n=== Debug Complete ===")
