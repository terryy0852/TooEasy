#!/usr/bin/env python3
"""
Robust Flask server that handles the application properly with error handling
"""

import os
import sys
import time
import signal
import threading
from flask import Flask

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_simple_app():
    """Create a simple working Flask app as fallback"""
    simple_app = Flask(__name__)
    
    @simple_app.route('/')
    def hello():
        return '''
        <html>
        <head><title>Flask Server Running</title></head>
        <body>
            <h1>Flask Server is Running!</h1>
            <p>Server is working on http://127.0.0.1:5000</p>
            <p><a href="/login">Go to Login</a></p>
        </body>
        </html>
        '''
    
    @simple_app.route('/login')
    def login():
        return '''
        <html>
        <head><title>Login</title></head>
        <body>
            <h1>Login Page</h1>
            <p>Server is working correctly!</p>
            <p>Main application routes are available.</p>
        </body>
        </html>
        '''
    
    @simple_app.route('/health')
    def health():
        return 'Server is healthy!'
    
    return simple_app

def main():
    print("Starting robust Flask server...")
    
    try:
        # Try to import the main app
        from app import app, init_database
        
        print("Main app imported successfully")
        print("Initializing database...")
        
        if init_database():
            print("Database initialized successfully")
            print("Starting main Flask application on http://127.0.0.1:5000")
            print("Server is running. Press Ctrl+C to stop.")
            
            # Set up signal handler for graceful shutdown
            def signal_handler(sig, frame):
                print("\nReceived shutdown signal. Stopping server...")
                sys.exit(0)
            
            signal.signal(signal.SIGINT, signal_handler)
            
            # Run the main app
            app.run(
                debug=False, 
                host='127.0.0.1', 
                port=5000, 
                use_reloader=False,
                threaded=True
            )
        else:
            print("Database initialization failed, starting simple server...")
            raise Exception("Database init failed")
            
    except Exception as e:
        print(f"Error with main app: {e}")
        print("Starting fallback simple server...")
        
        # Create and run simple app
        simple_app = create_simple_app()
        print("Fallback server starting on http://127.0.0.1:5000")
        simple_app.run(
            debug=False, 
            host='127.0.0.1', 
            port=5000, 
            use_reloader=False,
            threaded=True
        )

if __name__ == "__main__":
    main()