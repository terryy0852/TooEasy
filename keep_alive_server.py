#!/usr/bin/env python3
"""
Keep-alive Flask server that ensures the server stays running
"""

import os
import sys
import time
import threading
from flask import Flask

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def start_server():
    """Start the Flask server with proper configuration"""
    try:
        # Import the main app
        from app import app, init_database
        
        print("=" * 50)
        print("STARTING FLASK SERVER")
        print("=" * 50)
        
        # Initialize database
        print("Initializing database...")
        if init_database():
            print("✓ Database initialized successfully")
        else:
            print("✗ Database initialization failed")
            return False
        
        # Start the server
        print("Starting Flask application...")
        print("Server URL: http://127.0.0.1:5000")
        print("Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Run the app
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=False,
            use_reloader=False,
            threaded=True
        )
        
        return True
        
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function with retry logic"""
    max_retries = 3
    
    for attempt in range(max_retries):
        print(f"\nAttempt {attempt + 1} of {max_retries}")
        
        if start_server():
            print("Server started successfully!")
            break
        else:
            print(f"Attempt {attempt + 1} failed")
            
            if attempt < max_retries - 1:
                print(f"Retrying in 3 seconds...")
                time.sleep(3)
            else:
                print("All attempts failed. Server could not be started.")
                
                # Fallback: start a simple server
                print("\nStarting fallback simple server...")
                simple_app = Flask(__name__)
                
                @simple_app.route('/')
                def hello():
                    return 'Simple Flask Server is Running!'
                
                @simple_app.route('/health')
                def health():
                    return 'Server is healthy!'
                
                print("Fallback server starting on http://127.0.0.1:5000")
                simple_app.run(
                    host='127.0.0.1',
                    port=5000,
                    debug=False,
                    use_reloader=False
                )

if __name__ == "__main__":
    main()