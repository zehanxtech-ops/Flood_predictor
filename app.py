# app.py
import torch
import torch.nn as nn
import numpy as np
import joblib
import pandas as pd
import time
import threading
from flask import Flask, render_template, request, jsonify, Response
import json
from datetime import datetime

# Must match the training architecture
class RainfallModel(nn.Module):
    def __init__(self, input_dim=9):
        super(RainfallModel, self).__init__()
        self.fc1 = nn.Linear(input_dim, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 1)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        return x

# Load model
model = RainfallModel(input_dim=9)
model.load_state_dict(torch.load("model.pth"))
model.eval()

# Load scaler
scaler = joblib.load("scaler.pkl")

feature_columns = ["n_pixels","rfh","rfh_avg","r1h","r1h_avg","r3h","r3h_avg","rfq","r3q"]

# Load original data for realistic value ranges
try:
    df = pd.read_csv("Rain_fall_in_Pakistan.csv")
    # Get statistical ranges for realistic data generation
    data_ranges = {}
    for col in feature_columns:
        if col in df.columns:
            data_ranges[col] = {
                'min': df[col].min(),
                'max': df[col].max(),
                'mean': df[col].mean(),
                'std': df[col].std()
            }
except:
    # Fallback ranges if CSV not available
    data_ranges = {col: {'min': 0, 'max': 100, 'mean': 50, 'std': 20} for col in feature_columns}

app = Flask(__name__)

# Global variable to store latest prediction
latest_prediction = {"prediction": 0, "timestamp": datetime.now().isoformat(), "features": {}}

def generate_realistic_data():
    """Generate realistic feature values based on original data distribution"""
    data = []
    features = {}
    for col in feature_columns:
        if col in data_ranges:
            # Generate values using normal distribution around mean
            value = np.random.normal(data_ranges[col]['mean'], data_ranges[col]['std'])
            # Clip to realistic range
            value = np.clip(value, data_ranges[col]['min'], data_ranges[col]['max'])
        else:
            value = np.random.uniform(0, 100)
        data.append(value)
        features[col] = round(value, 2)
    return np.array(data).reshape(1, -1), features

def convert_to_rainfall_percentage(raw_prediction):
    """Convert raw model prediction to rainfall chance percentage"""
    # Normalize prediction to 0-100% range using sigmoid-like function
    # Adjust these parameters based on your model's output range
    normalized = 1 / (1 + np.exp(-raw_prediction * 0.1))  # Sigmoid normalization
    percentage = normalized * 100
    return min(max(percentage, 0), 100)  # Clamp between 0-100

def get_threat_level(percentage):
    """Determine threat level based on rainfall percentage"""
    if percentage >= 70:
        return "HIGH"
    elif percentage >= 40:
        return "MEDIUM"
    else:
        return "LOW"

def continuous_prediction():
    """Continuously generate predictions in background"""
    global latest_prediction
    while True:
        try:
            # Generate realistic input data
            X, features = generate_realistic_data()
            
            # Scale and predict
            X_scaled = scaler.transform(X)
            X_tensor = torch.tensor(X_scaled, dtype=torch.float32)
            
            with torch.no_grad():
                raw_prediction = model(X_tensor).item()
            
            # Convert to percentage
            rainfall_percentage = convert_to_rainfall_percentage(raw_prediction)
            threat_level = get_threat_level(rainfall_percentage)
            
            # Update global prediction
            latest_prediction = {
                "prediction": round(rainfall_percentage, 1),
                "raw_prediction": round(raw_prediction, 4),
                "threat_level": threat_level,
                "timestamp": datetime.now().isoformat(),
                "features": features
            }
            
            time.sleep(1)  # Update every second for real-time feel
        except Exception as e:
            print(f"Prediction error: {e}")
            time.sleep(5)

# Start background prediction thread
prediction_thread = threading.Thread(target=continuous_prediction, daemon=True)
prediction_thread.start()

@app.route('/')
def index():
    return render_template('realtime_dashboard.html', features=feature_columns)

@app.route('/stream')
def stream():
    """Server-sent events endpoint for real-time data"""
    def event_stream():
        while True:
            yield f"data: {json.dumps(latest_prediction)}\n\n"
            time.sleep(1)  # Send updates every second
    
    return Response(event_stream(), mimetype="text/plain")

@app.route('/latest')
def get_latest():
    """Get latest prediction as JSON"""
    return jsonify(latest_prediction)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = []
        for col in feature_columns:
            value = float(request.form.get(col, 0))
            data.append(value)
        X = np.array(data).reshape(1, -1)
        X_scaled = scaler.transform(X)
        X_tensor = torch.tensor(X_scaled, dtype=torch.float32)
        with torch.no_grad():
            raw_prediction = model(X_tensor).item()
        
        rainfall_percentage = convert_to_rainfall_percentage(raw_prediction)
        threat_level = get_threat_level(rainfall_percentage)
        
        return jsonify({
            "prediction": round(rainfall_percentage, 1),
            "raw_prediction": round(raw_prediction, 4),
            "threat_level": threat_level
        })
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
