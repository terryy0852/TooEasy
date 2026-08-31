#!/usr/bin/env python3
"""
Test script to verify production initialization works correctly
"""

import os
import sys
import logging
import tempfile

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('PROD_TEST')

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test with SQLite first (more reliable for local testing)
print("=== TESTING WITH SQLITE DATABASE ===")

try:
    # Clear any existing DATABASE_URL to force SQLite usage
    if 'DATABASE_URL' in os.environ:
        del os.environ['DATABASE_URL']
    
    # Import app components
    from app import app, db, User, Assignment, Submission, init_database
    
    # Initialize database
    with app.app_context():
        logger.info("Testing SQLite database initialization...")
        db.create_all()
        logger.info("SQLite tables created successfully")
        
        # Test user creation
        test_user = User(username='testuser', email='test@example.com', role='admin')
        test_user.set_password('testpassword123')
        db.session.add(test_user)
        db.session.commit()
        logger.info("Test user created successfully")
        
        # Test user retrieval
        retrieved_user = User.query.filter_by(username='testuser').first()
        if retrieved_user and retrieved_user.check_password('testpassword123'):
            logger.info("User authentication test passed")
        else:
            logger.error("User authentication test failed")
        
        # Clean up
        db.session.delete(retrieved_user)
        db.session.commit()
        logger.info("Cleanup complete")
        
    print("✅ SQLite database tests passed")
    
except Exception as e:
    print(f"❌ SQLite database tests failed: {e}")
    import traceback
    traceback.print_exc()

print("\n=== TESTING DATABASE URL CONVERSION ===")

# Test the URL conversion logic specifically
try:
    from app import app
    
    # Simulate Railway environment with postgres:// URL
    os.environ['DATABASE_URL'] = 'postgres://test_user:test_pass@test_host:5432/test_db'
    
    with app.app_context():
        db_url = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"App DATABASE_URI: {db_url}")
        
        if db_url.startswith('postgresql://'):
            print("✅ URL conversion from postgres:// to postgresql:// works correctly")
        else:
            print("❌ URL conversion failed")
    
except Exception as e:
    print(f"❌ URL conversion test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n=== TESTING ERROR HANDLING ===")

# Test error handling with invalid database URL
try:
    # Clear imports and reload
    for module in list(sys.modules.keys()):
        if module in ['app', 'app.db', 'app.User', 'app.Assignment', 'app.Submission']:
            del sys.modules[module]
    
    # Set invalid database URL
    os.environ['DATABASE_URL'] = 'postgres://invalid_user:invalid_pass@invalid_host:5432/invalid_db'
    
    from app import app, db
    
    with app.app_context():
        try:
            # This should fail with invalid connection
            db.session.execute('SELECT 1')
            print("❌ Should have failed with invalid database URL")
        except Exception as e:
            print(f"✅ Correctly handled invalid database URL: {type(e).__name__}")
    
except Exception as e:
    print(f"❌ Error handling test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n=== TESTING APP STRUCTURE ===")

# Verify all required components are present
try:
    from app import app, db, User, Assignment, Submission
    from flask_login import LoginManager
    
    # Check core components
    print("✅ All required modules imported")
    
    # Check for required routes
    required_routes = ['login', 'register', 'student_dashboard', 'health_check']
    for route in required_routes:
        if route in app.view_functions:
            print(f"✅ Route {route} found")
        else:
            print(f"❌ Route {route} missing")
    
except Exception as e:
    print(f"❌ App structure test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n=== TEST COMPLETE ===")
