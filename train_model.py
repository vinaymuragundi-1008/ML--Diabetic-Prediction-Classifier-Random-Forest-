import pandas as pd
import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier

df = pd.read_csv("dataset/diabetes.csv")

cols = ['Glucose','BloodPressure','SkinThickness','Insulin','BMI']
df[cols] = df[cols].replace(0, np.nan)
df.fillna(df.mean(), inplace=True)

X = df.drop("Outcome", axis=1)
y = df["Outcome"]

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

with open("model/diabetes_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model trained and saved")