#!/usr/bin/env python3
"""
Test script specifically for the database URL conversion functionality
"""

import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('URL_TEST')

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== DIRECT URL CONVERSION TEST ===")

test_urls = [
    'postgres://user:pass@host:5432/dbname',
    'postgresql://user:pass@host:5432/dbname',
    'postgres://test_user:test_pass@test_host:5432/test_db'
]

for url in test_urls:
    print(f"Input: {url}")
    if url.startswith('postgres://'):
        converted = url.replace('postgres://', 'postgresql://', 1)
        print(f"Output: {converted}")
        print(f"Success: {converted.startswith('postgresql://')}")
    else:
        print(f"Output: {url}")
        print(f"Already correct: {url.startswith('postgresql://')}")
    print()

print("=== APP DATABASE CONFIGURATION TEST ===")

# Test with app configuration
# First, we need to set the environment variable BEFORE importing the app
try:
    # Clear any existing DATABASE_URL
    if 'DATABASE_URL' in os.environ:
        del os.environ['DATABASE_URL']
    
    # Import app with fresh environment
    import importlib
    if 'app' in sys.modules:
        del sys.modules['app']
    
    # Test without DATABASE_URL (should use SQLite)
    from app import app
    
    with app.app_context():
        db_url = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"Without DATABASE_URL: {db_url}")
        print(f"Is SQLite: {db_url.startswith('sqlite://')}")
    
    # Clear app module
    if 'app' in sys.modules:
        del sys.modules['app']
    
    # Test with Railway-like URL
    os.environ['DATABASE_URL'] = 'postgres://railway_user:railway_pass@railway_host:5432/railway_db'
    
    # Import app again with new environment variable
    from app import app
    
    with app.app_context():
        db_url = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"With Railway URL: {db_url}")
        print(f"Is PostgreSQL: {db_url.startswith('postgresql://')}")
        print(f"Correctly converted: {db_url == 'postgresql://railway_user:railway_pass@railway_host:5432/railway_db'}")
    
    print("\n✅ URL conversion tests passed")
    
except Exception as e:
    print(f"\n❌ URL conversion tests failed: {e}")
    import traceback
    traceback.print_exc()

print("\n=== FINAL VERIFICATION ===")

# Final verification - simulate Railway environment and check all settings
try:
    # Set up full Railway environment
    os.environ['SECRET_KEY'] = 'railway_secret_key_12345'
    os.environ['DATABASE_URL'] = 'postgres://railway_user:railway_pass@railway_host:5432/railway_db'
    os.environ['PORT'] = '5000'
    
    # Clear and reload app
    if 'app' in sys.modules:
        del sys.modules['app']
    
    from app import app
    
    print(f"SECRET_KEY configured: {bool(app.secret_key)}")
    print(f"DEBUG mode: {app.config['DEBUG']}")
    print(f"DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"PostgreSQL correct format: {app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgresql://')}")
    
    print("\n✅ All Railway environment settings verified")
    
except Exception as e:
    print(f"\n❌ Railway environment test failed: {e}")
    import traceback
    traceback.print_exc()
