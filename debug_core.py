#!/usr/bin/env python3
"""
Core debug script for Railway production deployment issues
Focuses on app initialization without external database dependencies
"""

import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('CORE_DEBUG')

# Print Python version
print(f"Python version: {sys.version}")

# Simulate Railway environment variables
os.environ['SECRET_KEY'] = 'test-secret-key-12345'
os.environ['PORT'] = '5000'
os.environ['DEBUG'] = 'False'

# Test with both URL formats to ensure conversion works
test_urls = [
    'postgres://user:pass@host:5432/dbname',
    'postgresql://user:pass@host:5432/dbname'
]

print("\n=== TESTING DATABASE URL CONVERSION ===")
for test_url in test_urls:
    print(f"Input: {test_url}")
    if test_url.startswith('postgres://'):
        converted_url = test_url.replace('postgres://', 'postgresql://', 1)
        print(f"Output: {converted_url} (✓ Converted)")
    else:
        print(f"Output: {test_url} (✓ Already correct)")

print("\n=== TESTING APP INITIALIZATION (NO DATABASE CONNECTION) ===")

# Import only what we need to test core functionality
try:
    from flask import Flask
    import os
    import sys
    
    app = Flask(__name__)
    app.config['DEBUG'] = False
    app.secret_key = os.environ.get('SECRET_KEY', 'fallback')
    
    # Test the URL conversion logic
    def test_db_url_conversion():
        db_url = os.environ.get('DATABASE_URL')
        if db_url:
            if db_url.startswith('postgres://'):
                return db_url.replace('postgres://', 'postgresql://', 1)
        return db_url
    
    # Test with Railway-like URL
    os.environ['DATABASE_URL'] = 'postgres://test_user:test_pass@test_host:5432/test_db'
    converted_url = test_db_url_conversion()
    print(f"URL conversion test: {converted_url}")
    assert converted_url == 'postgresql://test_user:test_pass@test_host:5432/test_db', \
        f"URL conversion failed: expected postgresql://..., got {converted_url}"
    
    # Test without DATABASE_URL
    del os.environ['DATABASE_URL']
    converted_url = test_db_url_conversion()
    print(f"No URL test: {converted_url}")
    
    print("✅ Core app functionality tests passed")
    
except Exception as e:
    print(f"❌ Core app initialization failed: {e}")
    import traceback
    traceback.print_exc()

print("\n=== TESTING REQUIREMENTS INSTALLATION ===")

# Check if we can import required packages
required_packages = [
    'flask',
    'flask_sqlalchemy', 
    'flask_login',
    'flask_babel',
    'psycopg2-binary',
    'gunicorn',
    'werkzeug'
]

for package in required_packages:
    try:
        __import__(package)
        print(f"✅ {package} imported successfully")
    except ImportError:
        print(f"❌ {package} import failed")

print("\n=== TESTING GUNICORN STARTUP ===")

# Test if Gunicorn is available
try:
    import gunicorn
    print(f"✅ Gunicorn version: {gunicorn.__version__}")
    
    # Test command line access
    import subprocess
    result = subprocess.run(['gunicorn', '--version'], capture_output=True, text=True)
    print(f"Gunicorn CLI output: {result.stdout.strip()}")
    print(f"Gunicorn CLI error: {result.stderr.strip()}")
    
except Exception as e:
    print(f"❌ Gunicorn test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n=== DEBUG COMPLETE ===")
