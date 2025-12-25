
import requests
import random
import string

def get_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

username = "user_" + get_random_string(5)
password = "password"
base_url = "http://127.0.0.1:5000"

s = requests.Session()

# 1. Register
print(f"Registering user: {username}")
r = s.post(f"{base_url}/register", data={"username": username, "password": password})
if r.url == f"{base_url}/login":
    print("Registration Successful (Redirected to Login)")
else:
    print(f"Registration Failed. URL: {r.url}")

# 2. Login #1
print("Logging in (1st time)...")
r = s.post(f"{base_url}/login", data={"username": username, "password": password})
if "Prediction History" not in r.text:
    print("SUCCESS: History NOT visible on 1st login.")
else:
    print("FAILURE: History visible on 1st login!")

# 3. Login #2 (Logout first or just login again? Logic just increments count on login POST)
print("Logging in (2nd time)...")
r = s.post(f"{base_url}/login", data={"username": username, "password": password})
if "Prediction History" in r.text:
    print("SUCCESS: History IS visible on 2nd login.")
else:
    print("FAILURE: History NOT visible on 2nd login!")

# 4. Make Prediction
print("Making a prediction...")
data = {
    "pregnancies": 1, "glucose": 120, "bp": 70, "skin": 20, "insulin": 80, "bmi": 25, "dpf": 0.5, "age": 30
}
s.post(f"{base_url}/predict", data=data)

# 5. Check Dashboard for History Entry
print("Checking History for Entry...")
r = s.get(f"{base_url}/dashboard")
if "120.0" in r.text or "Low Risk" in r.text: # Check for input or result
    print("SUCCESS: Prediction found in History.")
else:
    print("FAILURE: Prediction not found in History.")
