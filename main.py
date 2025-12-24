import requests

# Simple test to verify requests is resolvable from the venv
print("requests version:", requests.__version__)
resp = requests.get("https://httpbin.org/status/200")
print("status:", resp.status_code)
