#!/usr/bin/env python3
"""
Final verification test for the fixed application
"""

import os
import sys
import logging
import time
import requests
from multiprocessing import Process

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('FINAL_TEST')

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_app_initialization():
    """Test app initialization with SQLite"""
    logger.info("=== Testing app initialization with SQLite ===")
    
    # Clear any existing DATABASE_URL
    if 'DATABASE_URL' in os.environ:
        del os.environ['DATABASE_URL']
    
    # Import app fresh
    if 'app' in sys.modules:
        del sys.modules['app']
    
    try:
        from app import app, db, User, init_database
        
        with app.app_context():
            # Test database initialization
            success = init_database()
            assert success, "Database initialization failed"
            logger.info("✅ Database initialization successful")
            
            # Test health check
            client = app.test_client()
            response = client.get('/health')
            assert response.status_code == 200, f"Health check failed: {response.status_code}"
            logger.info("✅ Health check endpoint works")
            
            # Test login page
            response = client.get('/login')
            assert response.status_code == 200, f"Login page failed: {response.status_code}"
            logger.info("✅ Login page loads correctly")
            
            logger.info("✅ App initialization tests passed")
            
    except Exception as e:
        logger.error(f"❌ App initialization tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_url_conversion():
    """Test database URL conversion"""
    logger.info("=== Testing database URL conversion ===")
    
    # Clear app module
    if 'app' in sys.modules:
        del sys.modules['app']
    
    # Set Railway-like URL
    os.environ['DATABASE_URL'] = 'postgres://test_user:test_pass@test_host:5432/test_db'
    
    try:
        from app import app
        
        with app.app_context():
            db_url = app.config['SQLALCHEMY_DATABASE_URI']
            logger.info(f"Database URL: {db_url}")
            
            assert db_url.startswith('postgresql://'), f"URL not converted: {db_url}"
            assert 'test_user' in db_url, f"Username missing from URL: {db_url}"
            assert 'test_db' in db_url, f"Database name missing from URL: {db_url}"
            
            logger.info("✅ URL conversion tests passed")
            
    except Exception as e:
        logger.error(f"❌ URL conversion tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_error_handling():
    """Test error handling"""
    logger.info("=== Testing error handling ===")
    
    # Clear app module
    if 'app' in sys.modules:
        del sys.modules['app']
    
    # Test with invalid URL to trigger error
    os.environ['DATABASE_URL'] = 'postgres://invalid:invalid@invalid:5432/invalid'
    
    try:
        from app import init_database
        
        # This should return False due to connection error
        success = init_database()
        assert not success, "Expected initialization to fail with invalid URL"
        
        logger.info("✅ Error handling tests passed")
        
    except Exception as e:
        logger.error(f"❌ Error handling tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def run_tests():
    """Run all verification tests"""
    logger.info("Starting final verification tests...")
    
    tests = [
        test_app_initialization,
        test_url_conversion,
        test_error_handling
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    if all(results):
        logger.info("🎉 All final verification tests passed!")
        logger.info("The application is ready for deployment.")
        return True
    else:
        logger.error("❌ Some tests failed. Please check the logs.")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)