import http.server
import socketserver
import time
import threading

print("[📦] Testing basic HTTP server...")

# Test if we can even create a socket
try:
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 9999))
    s.listen(1)
    s.close()
    print("[✅] Socket creation successful")
except Exception as e:
    print(f"[❌] Socket creation failed: {e}")

# Try with built-in HTTP server
PORT = 9999

handler = http.server.SimpleHTTPRequestHandler

try:
    httpd = socketserver.TCPServer(('', PORT), handler)
    print(f"[🚀] Basic HTTP server running on http://localhost:{PORT}")
    
    # Run in a thread for a short time
    def run_server():
        httpd.serve_forever()
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait a moment then try to connect
    time.sleep(2)
    
    # Test connection to ourselves
    print("[🔍] Testing self-connection...")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', PORT))
    client.sendall(b'GET / HTTP/1.1\r\nHost: localhost\r\n\r\n')
    response = client.recv(1024)
    client.close()
    
    if response:
        print("[✅] Self-connection successful!")
        print(f"[📝] Response: {response[:100]}...")
    
    # Cleanup
    httpd.shutdown()
    httpd.server_close()
    
    print("\n[🎉] Basic server test completed successfully!")
    print("[💡] The environment supports HTTP servers, so the issue is specific to the Flask app configuration.")
    
except Exception as e:
    print(f"[❌] Basic server test failed: {e}")
    import traceback
    traceback.print_exc()