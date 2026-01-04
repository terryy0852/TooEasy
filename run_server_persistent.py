#!/usr/bin/env python3
"""
Persistent server startup script that works reliably.
"""
import os
import sys
import subprocess
import time
import socket

# Ensure we're in the correct directory
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

print("📦 Starting Persistent Flask Server...")
print("=" * 50)

# Command to run the app
cmd = [
    sys.executable,
    "-c",
    "from app import app, create_tables; create_tables(); app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)"
]

# Start the server in the background
process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    shell=False
)

print(f"🚀 Server process started with PID: {process.pid}")
print("🔄 Waiting for server to initialize...")

# Wait for server to start
time.sleep(4)

# Check if server is running
if process.poll() is not None:
    print(f"❌ Server failed to start! Exit code: {process.poll()}")
    stderr = process.stderr.read()
    if stderr:
        print("Error output:")
        print(stderr)
    sys.exit(1)

# Test if port is accessible
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex(('127.0.0.1', 5000))
    sock.close()
    
    if result == 0:
        print("✅ Server is listening on port 5000")
        print("🌐 Access it at: http://127.0.0.1:5000")
        print("🔐 Login page: http://127.0.0.1:5000/login")
        print("💻 Dashboard: http://127.0.0.1:5000/student_dashboard")
        print("\n✅ Flask Server is now running!")
        print("📝 Note: Server will continue running in background")
    else:
        print(f"❌ Server is not accessible on port 5000 (socket error: {result})")
        
except Exception as e:
    print(f"❌ Connection test failed: {e}")

print("=" * 50)
print("To stop the server, run:")
print(f"   taskkill /PID {process.pid} /F")
print("=" * 50)