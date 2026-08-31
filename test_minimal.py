#!/usr/bin/env python3
"""
Minimal Flask test app to diagnose the server issue.
"""
from flask import Flask

# Create minimal app
app = Flask(__name__)
app.secret_key = 'test-secret-key'

@app.route('/')
def home():
    return "<h1>Test Server is Running!</h1>"

@app.route('/login')
def login():
    return "<h2>Login Page</h2>"

if __name__ == '__main__':
    print("Starting minimal test server...")
    print("Access at: http://127.0.0.1:5000")
    app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)