# Test script to verify admin user management functionality
from app import app, db, User
from flask_login import FlaskLoginClient

with app.app_context():
    print("=== Admin Functionality Test ===")
    
    # Create admin user if not exists
    admin = User.query.filter_by(username='adminuser').first()
    if not admin:
        admin = User(
            username='adminuser',
            email='admin@example.com',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Created test admin user: adminuser/admin123")
    
    # Test 1: Verify admin user exists
    admin = User.query.filter_by(username='adminuser').first()
    if admin and admin.role == 'admin':
        print("✅ PASS: Admin user exists with correct role")
    else:
        print("❌ FAIL: Admin user not found or has wrong role")
    
    # Test 2: Verify admin routes are protected
    app.test_client_class = FlaskLoginClient
    with app.test_client() as client:
        # Try accessing admin route as non-admin
        response = client.get('/admin/users', follow_redirects=True)
        if b'Access denied' in response.data:
            print("✅ PASS: Admin route protected from anonymous access")
        else:
            print("❌ FAIL: Admin route accessible without login")
        
        # Login as admin and access route
        client.post('/login', data={
            'username': 'adminuser',
            'password': 'admin123'
        })
        
        response = client.get('/admin/users', follow_redirects=True)
        if b'User Management' in response.data:
            print("✅ PASS: Admin can access user management")
        else:
            print("❌ FAIL: Admin cannot access user management")
    
    print("\nTest accounts available:")
    print("- Admin: username='adminuser', password='admin123'")
    print("- Teacher: username='testteacher', password='password123'")
    print("- Student: username='teststudent', password='password123'")
    print("\nYou can now test the admin functionality!")
