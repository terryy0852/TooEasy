#!/usr/bin/env python3
"""
Simple test server to check Flask app functionality
"""

import os
import sys
from flask import Flask

# Create a minimal Flask app for testing
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello! Flask server is working!'

@app.route('/health')
def health():
    return 'Server is healthy!'

if __name__ == '__main__':
    print("Starting simple test server on http://127.0.0.1:5000")
    app.run(debug=False, host='127.0.0.1', port=5000)