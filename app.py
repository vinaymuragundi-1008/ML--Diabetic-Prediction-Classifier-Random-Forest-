import os
import pickle
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib
matplotlib.use("Agg")   # IMPORTANT for Flask graphs
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix

from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "secret123"

# Global metrics to pass to dashboard
MODEL_METRICS = {
    "accuracy": "N/A",
    "f1_score": "N/A"
}

# Load model
with open("model/diabetes_model.pkl", "rb") as f:
    model = pickle.load(f)

# Ensure plots directory exists
if not os.path.exists("static/plots"):
    os.makedirs("static/plots")

# Generate Graphs & Calculate Metrics on Startup
try:
    df = pd.read_csv("dataset/diabetes.csv")
    
    # Preprocessing (same as training)
    cols = ['Glucose','BloodPressure','SkinThickness','Insulin','BMI']
    df[cols] = df[cols].replace(0, np.nan)
    df.fillna(df.mean(), inplace=True)
    
    X = df.drop("Outcome", axis=1)
    y = df["Outcome"]
    
    # Calculate Metrics
    y_pred = model.predict(X)
    acc = accuracy_score(y, y_pred)
    f1 = f1_score(y, y_pred)
    MODEL_METRICS["accuracy"] = f"{acc*100:.1f}%"
    MODEL_METRICS["f1_score"] = f"{f1:.2f}"
    
    # Graph 1: Correlation Matrix
    plt.figure(figsize=(10, 8))
    sns.heatmap(df.corr(), annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Correlation Matrix")
    plt.tight_layout()
    plt.savefig("static/plots/correlation.png")
    plt.close()

    # Graph 2: Confusion Matrix
    cm = confusion_matrix(y, y_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=["No Diabetes", "Diabetes"], yticklabels=["No Diabetes", "Diabetes"])
    plt.ylabel("Actual")
    plt.xlabel("Predicted")
    plt.title("Confusion Matrix")
    plt.tight_layout()
    plt.savefig("static/plots/confusion_matrix.png")
    plt.close()

    # Graph 3: Scatter Plot (Glucose vs BMI)
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.scatterplot(x="Glucose", y="BMI", hue="Outcome", data=df, palette={0: "green", 1: "red"}, alpha=0.6, ax=ax)
    plt.title("Glucose vs BMI Distribution")
    plt.tight_layout()
    plt.savefig("static/plots/scatter_plot.png")
    plt.close()

    # Graph 4: Model Confidence Histogram
    probs = model.predict_proba(X)[:, 1]
    plt.figure(figsize=(8, 6))
    plt.hist(probs, bins=20, color="purple", alpha=0.7, edgecolor='black')
    plt.title("Model Confidence Distribution (Diabetes Probability)")
    plt.xlabel("Predicted Probability")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig("static/plots/confidence.png")
    plt.close()

    print("All graphs and metrics generated successfully.")

except Exception as e:
    print(f"Error generating graphs/metrics: {e}")

import sqlite3
import datetime

# Database Helper
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    # Users Table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    login_count INTEGER DEFAULT 0,
                    medical_history TEXT
                )''')
    
    # Simple migration for existing tables (ignore failure if column exists)
    try:
        c.execute("ALTER TABLE users ADD COLUMN medical_history TEXT")
    except sqlite3.OperationalError:
        pass # Column likely exists

    # History Table
    c.execute('''CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    prediction TEXT,
                    probability TEXT,
                    timestamp TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )''')
    conn.commit()
    conn.close()

init_db()

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        
        if user:
            # user schema: id(0), username(1), password(2), login_count(3), medical_history(4)
            user_id = user[0]
            new_count = user[3] + 1
            
            # Update login count
            c.execute("UPDATE users SET login_count = ? WHERE id = ?", (new_count, user_id))
            conn.commit()
            conn.close()
            
            session["logged_in"] = True
            session["user_id"] = user_id
            session["username"] = username
            session["login_count"] = new_count
            
            return redirect(url_for("dashboard"))
        else:
            conn.close()
            return "Invalid Credentials" 
            
    return render_template("login.html")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        medical_history = request.form.get("medical_history", "")
        
        try:
            conn = sqlite3.connect("database.db")
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password, medical_history) VALUES (?, ?, ?)", (username, password, medical_history))
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            return "Username already exists"
            
    return render_template("register.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    
    user_id = session["user_id"]
    login_count = session["login_count"]
    
    # Always fetch history
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT prediction, probability, timestamp FROM history WHERE user_id = ? ORDER BY id DESC", (user_id,))
    history_data = c.fetchall()
    
    # Fetch User Details (for medical history)
    c.execute("SELECT medical_history FROM users WHERE id = ?", (user_id,))
    user_data = c.fetchone()
    medical_history = user_data[0] if user_data else ""
    
    conn.close()
    
    # Dataset Statistics
    df = pd.read_csv("dataset/diabetes.csv")
    dataset_stats = {
        "total_samples": len(df),
        "features": df.shape[1] - 1, # Exclude Outcome
        "positive": len(df[df["Outcome"] == 1]),
        "negative": len(df[df["Outcome"] == 0])
    }
    
    # Description
    dataset_desc = "The Pima Indians Diabetes Dataset involves predicting the onset of diabetes within 5 years in Pima Indian women."

    return render_template("dashboard.html", metrics=MODEL_METRICS, history=history_data, login_count=login_count, 
                           dataset_desc=dataset_desc, stats=dataset_stats, medical_history=medical_history)

# ---------------- PREDICT ----------------
@app.route("/predict", methods=["POST"])
def predict():
    try:
        values = [
            float(request.form["pregnancies"]),
            float(request.form["glucose"]),
            float(request.form["bp"]),
            float(request.form["skin"]),
            float(request.form["insulin"]),
            float(request.form["bmi"]),
            float(request.form["dpf"]),
            float(request.form["age"])
        ]

        # Predict Class and Probability
        prediction = model.predict([values])[0]
        # probability of class 1 (Diabetes)
        probability = model.predict_proba([values])[0][1] 
        
        prob_percentage = f"{probability * 100:.1f}%"
        output = "High Risk of Diabetes" if prediction == 1 else "Low Risk of Diabetes"

        # Save to History
        if session.get("logged_in"):
            conn = sqlite3.connect("database.db")
            c = conn.cursor()
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO history (user_id, prediction, probability, timestamp) VALUES (?, ?, ?, ?)",
                      (session["user_id"], output, prob_percentage, timestamp))
            conn.commit()
            conn.close()

        # --------- GRAPH 1: Probability ----------
        # Plotting both probabilities: [No Diabetes, Diabetes]
        probs = model.predict_proba([values])[0]
        plt.figure(figsize=(6, 4))
        plt.bar(["No Diabetes", "Diabetes"], probs, color=["green", "red"])
        plt.ylabel("Probability")
        plt.title("Prediction Probability")
        plt.ylim(0, 1)
        plt.tight_layout()
        plt.savefig("static/plots/probability.png")
        plt.close()

        # --------- GRAPH 2: Feature Importance ----------
        features = ["Preg", "Glucose", "BP", "Skin", "Insulin", "BMI", "DPF", "Age"]
        plt.figure(figsize=(8, 5))
        # Sort features for better visualization
        importances = model.feature_importances_
        indices = np.argsort(importances)
        
        plt.barh([features[i] for i in indices], importances[indices], color="purple")
        plt.title("Feature Importance")
        plt.xlabel("Importance")
        plt.tight_layout()
        plt.savefig("static/plots/importance.png")
        plt.close()

        return render_template(
            "predict.html",
            result=output,
            probability=prob_percentage,
            prob_img="plots/probability.png",
            imp_img="plots/importance.png"
        )

    except Exception as e:
        return f"ERROR OCCURRED: {e}"

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)