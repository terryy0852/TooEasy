#!/usr/bin/env python3
"""
Test script to verify user persistence fix
This script tests that registered users are not forgotten after restarting the app
"""

import os
import sys
import requests
import time
import subprocess
import shutil
import tempfile

BASE_URL = 'http://localhost:5000'

# Test user credentials
TEST_USER = {
    'username': 'persistence_test',
    'password': 'persistence_test_password',
    'email': 'persistence@test.com',
    'role': 'student'
}

def start_flask_server():
    """Start the Flask server in a subprocess"""
    print("Starting Flask server...")
    process = subprocess.Popen(
        [sys.executable, '-m', 'flask', 'run', '--debug'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for server to start
    time.sleep(3)
    
    if process.poll() is not None:
        print("Server failed to start!")
        print(process.stderr.read())
        return None
    
    print("Flask server started successfully")
    return process

def stop_flask_server(process):
    """Stop the Flask server subprocess"""
    if process:
        print("Stopping Flask server...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        print("Flask server stopped")

def test_user_registration():
    """Test registering a new user"""
    print("\n1. Testing user registration...")
    response = requests.post(f'{BASE_URL}/register', data=TEST_USER)
    
    if response.status_code == 200:
        print("✓ User registration successful")
        return True
    elif "Username already exists" in response.text or "Email already exists" in response.text:
        print("✓ User already exists (expected if testing multiple times)")
        return True
    else:
        print(f"✗ User registration failed: {response.status_code}")
        print(response.text)
        return False

def test_user_login():
    """Test logging in with the registered user"""
    print("\n2. Testing user login...")
    login_data = {
        'username': TEST_USER['username'],
        'password': TEST_USER['password']
    }
    
    with requests.Session() as session:
        response = session.post(f'{BASE_URL}/login', data=login_data, allow_redirects=True)
        
        if response.status_code == 200 and 'dashboard' in response.url:
            print("✓ User login successful")
            return True
        else:
            print(f"✗ User login failed: {response.status_code}")
            print(response.url)
            return False

def test_database_file_exists():
    """Test that the database file exists in the instance folder"""
    print("\n3. Checking database file location...")
    db_path = os.path.join('instance', 'assignments.db')
    
    if os.path.exists(db_path):
        print(f"✓ Database file exists at: {db_path}")
        print(f"   File size: {os.path.getsize(db_path)} bytes")
        return True
    else:
        print(f"✗ Database file not found at: {db_path}")
        # Check if app.db exists instead
        if os.path.exists('app.db'):
            print(f"   WARNING: Found app.db in current directory (old database location)")
        return False

def main():
    """Main test function"""
    print("Testing User Persistence Fix")
    print("=" * 30)
    
    # Test 1: Start server and register user
    server = start_flask_server()
    if not server:
        print("Failed to start server. Exiting.")
        return 1
    
    try:
        # Test user registration and login
        if not test_user_registration():
            return 1
        
        if not test_user_login():
            return 1
            
        # Test 2: Stop and restart server
        stop_flask_server(server)
        
        print("\nRestarting server to test persistence...")
        server = start_flask_server()
        if not server:
            print("Failed to restart server. Exiting.")
            return 1
        
        # Test login again after restart
        if not test_user_login():
            return 1
            
        # Test 3: Verify database file location
        if not test_database_file_exists():
            return 1
            
    finally:
        stop_flask_server(server)
    
    print("\n" + "=" * 30)
    print("✅ All tests passed! User persistence is working correctly.")
    print("✅ Users are now being stored in the consistent database location.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
