#!/usr/bin/env python3
"""
Simple Flask server runner
"""

import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Flask environment variables
os.environ['FLASK_APP'] = 'app.py'
os.environ['FLASK_ENV'] = 'development'

# Import and run the app
try:
    from app import app, init_database
    
    print("=" * 60)
    print("FLASK SERVER STARTING")
    print("=" * 60)
    
    # Initialize database
    print("Initializing database...")
    if init_database():
        print("✓ Database initialized successfully")
    else:
        print("✗ Database initialization failed")
    
    print("Starting Flask application...")
    print("Server URL: http://127.0.0.1:5000")
    print("-" * 60)
    
    # Run the app with specific configuration
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        use_reloader=False,
        threaded=True
    )
    
except Exception as e:
    print(f"Error starting server: {e}")
    import traceback
    traceback.print_exc()
    
    # Fallback: simple server
    print("\nStarting fallback server...")
    from flask import Flask
    
    fallback_app = Flask(__name__)
    
    @fallback_app.route('/')
    def hello():
        return '''
        <h1>Fallback Flask Server</h1>
        <p>Server is running on http://127.0.0.1:5000</p>
        <p><a href="/health">Health Check</a></p>
        '''
    
    @fallback_app.route('/health')
    def health():
        return 'Server is healthy!'
    
    fallback_app.run(
        host='127.0.0.1',
        port=5000,
        debug=False,
        use_reloader=False
    )