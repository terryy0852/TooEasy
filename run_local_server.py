#!/usr/bin/env python3
"""
Simple script to run the Flask app locally on 127.0.0.1
"""

import os
import sys
from app import app, init_database

if __name__ == '__main__':
    print("Starting Flask application on localhost...")
    
    # Initialize database
    if init_database():
        print("Database initialized successfully")
        print("Starting server on http://127.0.0.1:5000")
        
        # Run the app on localhost
        app.run(debug=False, host='127.0.0.1', port=5000)
    else:
        print("Failed to initialize database")
        sys.exit(1)