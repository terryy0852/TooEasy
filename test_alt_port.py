import requests
import time

# Give server a moment to fully start
time.sleep(2)

try:
    print("[🔍] Testing server access on http://127.0.0.1:8080/login...")
    response = requests.get("http://127.0.0.1:8080/login", timeout=5)
    
    if response.status_code == 200:
        print("[✅] Server is accessible!")
        print(f"[📊] Status code: {response.status_code}")
        print(f"[📝] Page title: {response.text[:100]}...")
        print("\n[🎉] Success! You can now access the login page at http://127.0.0.1:8080/login")
    else:
        print(f"[⚠️] Server returned status code: {response.status_code}")
        print(f"[📝] Response content: {response.text[:200]}...")
        
except requests.ConnectionError as e:
    print(f"[❌] Connection failed: {e}")
    print("[💡] Try checking if the server is still running.")
except requests.Timeout:
    print("[⏱️] Request timed out.")
except Exception as e:
    print(f"[❌] Unexpected error: {e}")
    import traceback
    traceback.print_exc()