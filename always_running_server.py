#!/usr/bin/env python3
"""
Always-running Flask server with persistent connection
"""

import os
import sys
import time
import signal
import threading
from flask import Flask

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def start_server():
    """Start the Flask server with proper configuration"""
    try:
        # Import the main app
        from app import app, init_database
        
        print("=" * 60)
        print("ALWAYS-RUNNING FLASK SERVER")
        print("=" * 60)
        
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
        print("-" * 60)
        
        # Use a different approach - run in a thread
        def run_app():
            app.run(
                host='127.0.0.1',
                port=5000,
                debug=False,
                use_reloader=False,
                threaded=True
            )
        
        # Start server in a thread
        server_thread = threading.Thread(target=run_app, daemon=True)
        server_thread.start()
        
        print("Server started successfully!")
        print("Server is running in background thread")
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
            if not server_thread.is_alive():
                print("Server thread died, restarting...")
                server_thread = threading.Thread(target=run_app, daemon=True)
                server_thread.start()
        
        return True
        
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function with retry logic"""
    print("Starting always-running server...")
    
    # Set up signal handlers
    def signal_handler(signum, frame):
        print(f"\nReceived signal {signum}, shutting down...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start the server
    if start_server():
        print("Server is running persistently")
    else:
        print("Failed to start server")

if __name__ == "__main__":
    main()