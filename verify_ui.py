
import requests

base_url = "http://127.0.0.1:5000"

print("Checking Index Page UI...")
r = requests.get(base_url)

if "hero-section" in r.text or "Advanced Machine Learning" in r.text:
    print("SUCCESS: Hero Section found.")
else:
    print("FAILURE: Hero Section missing.")

if "fa-heartbeat" in r.text:
    print("SUCCESS: Hero Icon found.")
else:
    print("FAILURE: Hero Icon missing.")

if "features-grid" in r.text:
    print("SUCCESS: Features Grid found.")
else:
    print("FAILURE: Features Grid missing.")

print("\nChecking Login Page UI...")
r = requests.get(f"{base_url}/login")
if "auth-icon-circle" in r.text:
    print("SUCCESS: Login Auth Icon found.")
else:
    print("FAILURE: Login Auth Icon missing.")

print("\nChecking Register Page UI...")
r = requests.get(f"{base_url}/register")
if "register-icon" in r.text:
    print("SUCCESS: Register Auth Icon found.")
else:
    print("FAILURE: Register Auth Icon missing.")
