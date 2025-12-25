
import requests
import sys

try:
    response = requests.get("http://127.0.0.1:5000", timeout=5)
    if response.status_code == 200:
        print("SUCCESS: App is running and returning 200 OK")
    else:
        print(f"FAILURE: App returned status code {response.status_code}")
except Exception as e:
    print(f"FAILURE: Could not connect to app. Error: {e}")
