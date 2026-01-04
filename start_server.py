#!/usr/bin/env python3
"""
Simple server startup script that works reliably.
"""
import sys
import os

# Ensure we're in the correct directory
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

# Add current directory to path
if '.' not in sys.path:
    sys.path.insert(0, '.')

print("Starting Flask Application...")
print("=" * 40)
print(f"Directory: {os.getcwd()}")
print(f"Python: {sys.executable}")
print("=" * 40)

# Import and run the app
from app import app, create_tables

# Initialize database
create_tables()

print("\n🚀 Starting server...")
print("   Access at: http://127.0.0.1:5000")
print("   Press Ctrl+C to stop\n")

# Run the server
app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)