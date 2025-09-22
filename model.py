import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import StandardScaler
import joblib

# ======================
# 1. Load and Clean Data
# ======================
df = pd.read_csv("Rain_fall_in_Pakistan.csv")

print(f"Original dataset shape: {df.shape}")
print(f"Columns: {df.columns}")

# Convert date to datetime
df["date"] = pd.to_datetime(df["date"], errors="coerce")

# Drop useless columns
drop_cols = ["date", "ADM2_PCODE", "version"]
df = df.drop(columns=drop_cols, errors="ignore")

# Convert all columns except ID to numeric
for col in df.columns:
    if col != "adm2_id":
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Drop rows with NaN
df = df.dropna()
print(f"Cleaned dataset shape: {df.shape}")

# ======================
# 2. Features & Target
# ======================
target_column = "r1q"
if target_column not in df.columns:
    raise ValueError(f"Target column '{target_column}' not found in dataset!")

X = df.drop(columns=[target_column, "adm2_id"], errors="ignore").values
y = df[target_column].values

scaler = StandardScaler()
X = scaler.fit_transform(X)

X = torch.tensor(X, dtype=torch.float32)
y = torch.tensor(y, dtype=torch.float32).view(-1, 1)

print(f"Training on full dataset -> Features shape: {X.shape}, Target shape: {y.shape}")

# ======================
# 3. Define Model
# ======================
class RainfallModel(nn.Module):
    def __init__(self, input_dim):
        super(RainfallModel, self).__init__()
        self.fc1 = nn.Linear(input_dim, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 1)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        return self.fc3(x)

model = RainfallModel(X.shape[1])

# ======================
# 4. Training
# ======================
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

epochs = 30
for epoch in range(epochs):
    optimizer.zero_grad()
    outputs = model(X)
    loss = criterion(outputs, y)
    loss.backward()
    optimizer.step()
    if (epoch + 1) % 5 == 0:
        print(f"Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}")

# ======================
# 5. Save Model + Scaler
# ======================
torch.save(model.state_dict(), "model.pth")
joblib.dump(scaler, "scaler.pkl")
print("✅ Model trained on FULL dataset and saved as model.pth + scaler.pkl")
