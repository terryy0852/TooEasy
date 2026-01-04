#!/usr/bin/env python3
"""
Minimal Flask test to verify Flask is working correctly.
"""
from flask import Flask

app = Flask(__name__)
app.secret_key = 'test-secret-key'

@app.route('/')
def index():
    return '<h1>Minimal Flask Test</h1><p>Flask is working!</p>'

@app.route('/test')
def test():
    return '<h2>Test Page</h2><p>This is a test page.</p>'

if __name__ == '__main__':
    print("Starting minimal Flask test...")
    print("Access at: http://127.0.0.1:5001")
    app.run(debug=False, host='127.0.0.1', port=5001, use_reloader=False)