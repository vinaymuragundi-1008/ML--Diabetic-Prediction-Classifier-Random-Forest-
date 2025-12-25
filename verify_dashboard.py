
import requests
import re

# Use the same credentials as before or register new ones.
# Since app restarts might reset session but DB persists (sqlite).
# We'll use a new user to be safe or just login with known logic.
base_url = "http://127.0.0.1:5000"
username = "verify_dash_user"
password = "password"

s = requests.Session()

# Register (ignore if exists)
s.post(f"{base_url}/register", data={"username": username, "password": password})
# Login
s.post(f"{base_url}/login", data={"username": username, "password": password})

# Get Dashboard
r = s.get(f"{base_url}/dashboard")

print("Checking Dashboard Content...")

# Check for new Section Header
if "About the Dataset" in r.text:
    print("SUCCESS: Found 'About the Dataset' section.")
else:
    print("FAILURE: 'About the Dataset' section missing.")

# Check for Stats
# We expect Total Samples: 768
if "768" in r.text and "Total Samples" in r.text:
    print("SUCCESS: Found Total Samples (768).")
else:
    print("FAILURE: Total Samples missing or incorrect.")

# Check for Features: 8
if "8" in r.text and "Features" in r.text:
    print("SUCCESS: Found Features count (8).")
else:
    print("FAILURE: Features count missing.")

# Check for Class Distribution (268 vs 500)
if "268" in r.text and "Diabetic" in r.text:
    print("SUCCESS: Found Diabetic Count (268).")
else:
    print("FAILURE: Diabetic Count missing.")

if "500" in r.text and "Healthy" in r.text:
    print("SUCCESS: Found Healthy Count (500).")
else:
    print("FAILURE: Healthy Count missing.")
