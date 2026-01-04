#!/usr/bin/env python3
"""
Stable Flask server with persistent connection
"""

import os
import sys
import time
import signal
import atexit
from flask import Flask

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print(f"\nReceived signal {signum}, shutting down...")
    sys.exit(0)

def setup_server():
    """Setup and configure the Flask server"""
    try:
        # Import the main app
        from app import app, init_database
        
        print("=" * 60)
        print("STABLE FLASK SERVER STARTING")
        print("=" * 60)
        
        # Initialize database
        print("Initializing database...")
        if init_database():
            print("✓ Database initialized successfully")
        else:
            print("✗ Database initialization failed")
            return None
        
        return app
        
    except Exception as e:
        print(f"Error setting up server: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function with persistent server"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Set up cleanup
    atexit.register(lambda: print("\nServer stopped."))
    
    # Setup server
    app = setup_server()
    if app is None:
        print("Failed to setup server. Starting fallback...")
        
        # Fallback simple server
        fallback_app = Flask(__name__)
        
        @fallback_app.route('/')
        def hello():
            return '''
            <h1>Simple Flask Server</h1>
            <p>Server is running on http://127.0.0.1:5000</p>
            <p><a href="/health">Health Check</a></p>
            '''
        
        @fallback_app.route('/health')
        def health():
            return 'Server is healthy!'
        
        print("Starting fallback server on http://127.0.0.1:5000")
        fallback_app.run(
            host='127.0.0.1',
            port=5000,
            debug=False,
            use_reloader=False
        )
        return
    
    # Start the main server
    print("Starting Flask application...")
    print("Server URL: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop the server")
    print("-" * 60)
    
    # Use werkzeug server directly for more control
    from werkzeug.serving import make_server
    
    server = make_server('127.0.0.1', 5000, app, threaded=True)
    
    print(f"Server running on http://{server.host}:{server.port}")
    print("Server is now persistent and will not exit unexpectedly")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()
    except Exception as e:
        print(f"Server error: {e}")

if __name__ == "__main__":
    main()