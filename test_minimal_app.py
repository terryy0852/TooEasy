import requests
import time

# Give the server a moment to start
time.sleep(2)

try:
    url = "http://127.0.0.1:5000/login"
    print(f"🔍 Testing {url}")
    response = requests.get(url, timeout=10)
    print(f"✅ Success! Status Code: {response.status_code}")
    print(f"📝 Content: {response.text}")
except Exception as e:
    print(f"❌ Failed: {e}")