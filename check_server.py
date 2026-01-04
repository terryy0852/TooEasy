import requests

try:
    r = requests.get('http://127.0.0.1:5001/login')
    print(f'Server is running, status code: {r.status_code}')
    print('Response length:', len(r.text))
except Exception as e:
    print(f'Server not reachable: {e}')
