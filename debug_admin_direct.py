# Direct test script to debug admin functionality without running the server
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Assignment, Submission
from flask_login import login_user, current_user

print("=== Debugging Admin Functionality ===")

with app.app_context():
    # Test 1: Check if database is accessible
    print("\n1. Testing database connection...")
    try:
        users = User.query.all()
        print(f"   ✓ Database accessible, found {len(users)} users")
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Create a test admin user
    print("\n2. Creating test admin user...")
    test_admin = User.query.filter_by(username='debugadmin').first()
    if not test_admin:
        test_admin = User(username='debugadmin', email='debugadmin@example.com', role='admin')
        test_admin.set_password('debugpass')
        try:
            db.session.add(test_admin)
            db.session.commit()
            print("   ✓ Test admin user created")
        except Exception as e:
            print(f"   ❌ Error creating admin user: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("   ✓ Test admin user already exists")
    
    # Test 3: Try to load user and access admin functionality
    print("\n3. Testing admin user functionality...")
    try:
        # Simulate login
        with app.test_request_context():
            login_user(test_admin)
            
            # Test admin_users route functionality
            print("   Testing admin_users functionality...")
            users = User.query.all()
            print(f"   ✓ Found {len(users)} users via admin query")
            
            # Test admin_edit_user functionality
            print("   Testing admin_edit_user functionality...")
            if users:
                user_to_edit = users[0]
                print(f"   ✓ Found user to edit: {user_to_edit.username}")
            
            # Test admin_delete_user functionality (without actually deleting)
            print("   Testing admin_delete_user functionality...")
            if len(users) > 1:
                user_to_delete = users[1]
                print(f"   ✓ Found user to delete (not actually deleting): {user_to_delete.username}")
            
    except Exception as e:
        print(f"   ❌ Error in admin functionality: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Check templates
    print("\n4. Checking template files...")
    templates_to_check = ['student_dashboard.html', 'admin_users.html', 'admin_edit_user.html']
    for template in templates_to_check:
        template_path = f'templates/{template}'
        if os.path.exists(template_path):
            print(f"   ✓ {template} exists")
        else:
            print(f"   ❌ {template} not found")

print("\n=== Debug Complete ===")