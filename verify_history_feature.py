
import requests
import random
import string

def get_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

base_url = "http://127.0.0.1:5000"
username = "patient_" + get_random_string(5)
password = "password"
medical_notes = "Patient has a history of high blood pressure and occasional dizziness."

s = requests.Session()

# 1. Register with Medical History
print(f"Registering user: {username} with Medical Notes...")
r = s.post(f"{base_url}/register", data={
    "username": username, 
    "password": password,
    "medical_history": medical_notes
})

# 2. Login (This is login #1)
print("Logging in (1st time)...")
s.post(f"{base_url}/login", data={"username": username, "password": password})
r = s.get(f"{base_url}/dashboard")

# 3. Check for Medical History Display
if medical_notes in r.text:
    print("SUCCESS: Medical History displayed on Dashboard.")
else:
    print("FAILURE: Medical History NOT found.")

# 4. Check for Prediction History Section (Should be visible even empty)
if "Prediction History" in r.text and "No predictions yet" in r.text:
    print("SUCCESS: History Section visible on 1st login (Empty state).")
else:
    print("FAILURE: History Section not visible or empty state incorrect.")

# 5. Make Prediction
print("Making a prediction...")
data = {
    "pregnancies": 1, "glucose": 130, "bp": 75, "skin": 25, "insulin": 85, "bmi": 26, "dpf": 0.6, "age": 35
}
s.post(f"{base_url}/predict", data=data)

# 6. Check History again
print("Checking History after prediction...")
r = s.get(f"{base_url}/dashboard")
if "Risk" in r.text and "Probability" in r.text: 
    print("SUCCESS: Prediction recorded in History.")
else:
    print("FAILURE: Prediction likely not recorded or visible.")
