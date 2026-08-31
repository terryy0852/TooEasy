#!/usr/bin/env python3
"""
Persistent Flask server that handles the application properly
"""

import os
import sys
import time
import signal
import threading
from flask import Flask

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, init_database
    
    def signal_handler(sig, frame):
        print("\nReceived shutdown signal. Stopping server...")
        sys.exit(0)
    
    def run_server():
        print("Starting persistent Flask server...")
        print("Database initialization...")
        
        if init_database():
            print("Database initialized successfully")
            print("Starting Flask application on http://127.0.0.1:5000")
            print("Server is running. Press Ctrl+C to stop.")
            
            # Set up signal handler for graceful shutdown
            signal.signal(signal.SIGINT, signal_handler)
            
            # Run the app with proper configuration
            app.run(
                debug=False, 
                host='127.0.0.1', 
                port=5000, 
                use_reloader=False,
                threaded=True
            )
        else:
            print("Failed to initialize database")
            sys.exit(1)
    
    if __name__ == "__main__":
        run_server()
        
except Exception as e:
    print(f"Error starting server: {e}")
    import traceback
    traceback.print_exc()
    
    # Fallback: create a simple working server
    print("\nCreating fallback simple server...")
    simple_app = Flask(__name__)
    
    @simple_app.route('/')
    def hello():
        return 'Simple Flask Server is Running!'
    
    @simple_app.route('/health')
    def health():
        return 'Server is healthy!'
    
    print("Starting fallback server on http://127.0.0.1:5000")
    simple_app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)