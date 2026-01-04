import os
import sys

# Test environment variables
print("Testing Railway configuration...")
print("=" * 40)

# Check if required imports are available
try:
    from flask import Flask, jsonify
    from datetime import datetime
    print("✅ Flask imports successful")
except ImportError as e:
    print(f"❌ Flask import error: {e}")

# Test environment variable handling
try:
    # Simulate Railway environment
    os.environ['SECRET_KEY'] = 'test-secret-key'
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    
    # Import app to test configuration
    import app
    
    print(f"✅ App imported successfully")
    print(f"✅ Secret key set from environment: {app.app.secret_key[:10]}...")
    print(f"✅ Database URL set from environment: {app.app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # Check if health endpoint exists
    has_health_endpoint = False
    for rule in app.app.url_map.iter_rules():
        if str(rule) == '/health':
            has_health_endpoint = True
            break
    
    if has_health_endpoint:
        print("✅ /health endpoint found")
    else:
        print("❌ /health endpoint not found")
        
    print(f"✅ Debug mode: {app.app.config['DEBUG']}")
    
except Exception as e:
    print(f"❌ Error testing app: {e}")
    import traceback
    traceback.print_exc()

print("=" * 40)
print("Configuration test completed!")