
import requests

base_url = "http://127.0.0.1:5000"

print("Checking Register Page...")
r = requests.get(f"{base_url}/register")

# Check new placeholder
if "Prescribed Medications" in r.text or "Past Conditions" in r.text:
    print("SUCCESS: Medical History placeholder updated details found.")
else:
    print("FAILURE: Medical History placeholder NOT updated.")

# CSS checks are hard via simple requests, but we verified width via file update.
# Can check if style.css contains the new max-width logic
print("\nChecking CSS for sizing fix...")
r = requests.get(f"{base_url}/static/style.css")
if "max-width: 380px" in r.text:
    print("SUCCESS: 'max-width: 380px' found in CSS.")
else:
    print("FAILURE: CSS sizing update missing.")

if "align-items: center" in r.text: # Checking page-container
    print("SUCCESS: 'align-items: center' found in CSS.")
else:
    print("FAILURE: Vertical center alignment style missing.")
