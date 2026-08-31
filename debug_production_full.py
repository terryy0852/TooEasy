#!/usr/bin/env python3
"""
Comprehensive debug script for Railway production deployment issues
"""

import os
import sys
import logging
from werkzeug.security import generate_password_hash

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('PROD_DEBUG')

# Simulate Railway environment variables
os.environ['SECRET_KEY'] = 'test-secret-key-12345'
os.environ['DATABASE_URL'] = 'postgresql://postgres:n5jTtilYoz2S1LwO@db.xqjscxsvcespsrkyoekf.supabase.co:5432/postgres'
os.environ['PORT'] = '5000'
os.environ['DEBUG'] = 'False'

# Print environment
print("=== ENVIRONMENT VARIABLES ===")
for key, value in os.environ.items():
    if key in ['SECRET_KEY', 'DATABASE_URL', 'PORT', 'DEBUG']:
        print(f"{key}: {value}")

print("\n=== TESTING DATABASE CONNECTION ===")

try:
    # Test PostgreSQL connection
    import psycopg2
    logger.info("Testing PostgreSQL connection directly...")
    
    db_url = os.environ['DATABASE_URL']
    
    # Parse URL like: postgresql://user:pass@host:port/dbname
    from urllib.parse import urlparse
    result = urlparse(db_url)
    
    conn_params = {
        'host': result.hostname,
        'database': result.path[1:],  # Remove leading slash
        'user': result.username,
        'password': result.password,
        'port': result.port
    }
    
    print(f"Connecting to: {conn_params['host']}:{conn_params['port']}/{conn_params['database']}")
    
    conn = psycopg2.connect(**conn_params)
    cursor = conn.cursor()
    print("✅ Direct PostgreSQL connection successful")
    
    # Check database version
    cursor.execute("SELECT version()")
    version = cursor.fetchone()[0]
    print(f"PostgreSQL version: {version}")
    
    # Check schema
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Available tables: {tables}")
    
    # Check user table specifically
    cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'user')")
    has_user_table = cursor.fetchone()[0]
    print(f"User table exists: {has_user_table}")
    
    if has_user_table:
        cursor.execute("SELECT COUNT(*) FROM \"user\"")
        user_count = cursor.fetchone()[0]
        print(f"Number of users: {user_count}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Direct PostgreSQL connection failed: {e}")
    import traceback
    traceback.print_exc()

print("\n=== TESTING FLASK APP INITIALIZATION ===")

try:
    # Import Flask app
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    logger.info("Testing Flask app import...")
    from app import app, db, User, Assignment, Submission
    print("✅ Flask app imported successfully")
    
    # Test app configuration
    print(f"Debug mode: {app.config['DEBUG']}")
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"Track modifications: {app.config['SQLALCHEMY_TRACK_MODIFICATIONS']}")
    
    # Test database connection through SQLAlchemy
    with app.app_context():
        logger.info("Testing SQLAlchemy database connection...")
        
        # Try a simple query
        try:
            user_count = db.session.query(User).count()
            print(f"✅ SQLAlchemy query successful - found {user_count} users")
        except Exception as e:
            print(f"❌ SQLAlchemy query failed: {e}")
            import traceback
            traceback.print_exc()
            
            # Try to create tables if they don't exist
            try:
                print("Attempting to create tables...")
                db.create_all()
                print("✅ Tables created successfully")
                
                # Create a test user
                test_user = User(username='testuser', email='test@example.com')
                test_user.set_password('testpassword123')
                test_user.role = 'student'
                db.session.add(test_user)
                db.session.commit()
                print("✅ Test user created successfully")
                
            except Exception as e2:
                print(f"❌ Failed to create tables: {e2}")
                traceback.print_exc()
    
    print("✅ Flask app initialization completed")
    
except Exception as e:
    print(f"❌ Flask app initialization failed: {e}")
    import traceback
    traceback.print_exc()

print("\n=== TESTING GUNICORN CONFIGURATION ===")

try:
    import gunicorn
    print(f"✅ Gunicorn installed: {gunicorn.__version__}")
    
    # Check gunicorn configuration
    import subprocess
    result = subprocess.run(['gunicorn', '--version'], capture_output=True, text=True)
    print(f"Gunicorn CLI: {result.stdout.strip()}")
    
except Exception as e:
    print(f"❌ Gunicorn test failed: {e}")

print("\n=== TESTING REQUIRED PACKAGES ===")

required_packages = ['flask', 'flask_sqlalchemy', 'flask_login', 'flask_babel', 
                     'psycopg2', 'psycopg2-binary', 'gunicorn', 'werkzeug']

for package in required_packages:
    try:
        __import__(package)
        print(f"✅ {package} installed")
    except ImportError:
        print(f"❌ {package} not installed")

print("\n=== DEBUG COMPLETE ===")

