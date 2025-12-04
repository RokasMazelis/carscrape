import requests
url = 'https://ip.decodo.com/json'
# Use the credentials provided in the prompt
username = 'user-spnn7jyi3f-sessionduration-30-asn-15502'
password = 'f3zHx753fZt~nEibMx'
proxy = f"http://{username}:{password}@gate.decodo.com:10001"
print(f"Testing proxy: {proxy}")
try:
    result = requests.get(url, proxies = {
        'http': proxy,
        'https': proxy
    }, timeout=30)
    print(result.text)
except Exception as e:
    print(f"Proxy test failed: {e}")
