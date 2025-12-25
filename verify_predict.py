
import requests

data = {
    "pregnancies": 1,
    "glucose": 120,
    "bp": 70,
    "skin": 20,
    "insulin": 80,
    "bmi": 25,
    "dpf": 0.5,
    "age": 30
}

try:
    response = requests.post("http://127.0.0.1:5000/predict", data=data)
    if response.status_code == 200:
        if "Probability:" in response.text:
            print("SUCCESS: Prediction returned with Probability.")
        else:
            print("FAILURE: 'Probability:' text not found in response.")
    else:
        print(f"FAILURE: Status code {response.status_code}")
except Exception as e:
    print(f"FAILURE: {e}")
