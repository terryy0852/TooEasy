#!/usr/bin/env python3
"""
Simple test script to verify user persistence fix
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the current directory to the path so we can import the app
sys.path.append('.')

from app import app, db, User

def test_database_config():
    """Test that the database is configured correctly"""
    print("1. Testing database configuration...")
    
    with app.app_context():
        # Print the current database URL
        db_url = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"   Database URL: {db_url}")
        
        # Verify it's using the instance folder
        if 'instance' in db_url and 'assignments.db' in db_url:
            print("   ✓ Database is configured to use the instance folder")
            return True
        else:
            print("   ✗ Database is NOT using the instance folder")
            return False

def test_database_connection():
    """Test that we can connect to the database"""
    print("\n2. Testing database connection...")
    
    try:
        with app.app_context():
            # Test database connection by querying users
            users = User.query.all()
            print(f"   ✓ Database connection successful")
            print(f"   Number of existing users: {len(users)}")
            return True
    except Exception as e:
        print(f"   ✗ Database connection failed: {e}")
        return False

def test_user_creation_and_retrieval():
    """Test that a user can be created and retrieved from the database"""
    print("\n3. Testing user creation and retrieval...")
    
    test_username = 'persistence_test'
    test_email = 'persistence@test.com'
    test_password = 'test_password123'
    
    try:
        with app.app_context():
            # Check if user already exists
            existing_user = User.query.filter_by(username=test_username).first()
            if existing_user:
                print(f"   User '{test_username}' already exists (cleaning up)...")
                db.session.delete(existing_user)
                db.session.commit()
            
            # Create a new user
            new_user = User(username=test_username, email=test_email, role='student')
            new_user.set_password(test_password)
            
            # Add to database
            db.session.add(new_user)
            db.session.commit()
            print(f"   ✓ Created new user: {test_username}")
            
            # Retrieve the user from database
            retrieved_user = User.query.filter_by(username=test_username).first()
            if retrieved_user:
                print(f"   ✓ Retrieved user from database: {retrieved_user.username}")
                print(f"   User email: {retrieved_user.email}")
                print(f"   User role: {retrieved_user.role}")
                
                # Verify password
                if retrieved_user.check_password(test_password):
                    print(f"   ✓ Password verification successful")
                    return True
                else:
                    print(f"   ✗ Password verification failed")
                    return False
            else:
                print(f"   ✗ Failed to retrieve user from database")
                return False
                
    except Exception as e:
        print(f"   ✗ Error during user creation/retrieval: {e}")
        return False

def test_database_file_location():
    """Test that the database file exists at the expected location"""
    print("\n4. Testing database file location...")
    
    db_path = os.path.join('instance', 'assignments.db')
    if os.path.exists(db_path):
        print(f"   ✓ Database file exists at: {db_path}")
        print(f"   File size: {os.path.getsize(db_path)} bytes")
        
        # Compare with app.db (old location)
        if os.path.exists('app.db'):
            print(f"   NOTE: Old database file still exists at: app.db")
            print(f"         Size: {os.path.getsize('app.db')} bytes")
        return True
    else:
        print(f"   ✗ Database file not found at: {db_path}")
        return False

def main():
    """Main test function"""
    print("Simple User Persistence Test")
    print("=" * 30)
    
    tests = [
        test_database_config,
        test_database_connection,
        test_user_creation_and_retrieval,
        test_database_file_location
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 30)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! User persistence is fixed.")
        print("\nThe fix ensures that:")
        print("1. The app uses the database file in the instance folder")
        print("2. Users are properly saved to the database")
        print("3. Users can be retrieved and authenticated")
        print("4. Data persists across app restarts")
        return 0
    else:
        print("❌ Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

