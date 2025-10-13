# backend/scripts/retrain_model.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle
from pathlib import Path

# Paths
FEATURES_PATH = Path(__file__).resolve().parents[1] / "data" / "features.csv"
MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "model.pkl"

# 1️⃣ Load dataset
data = pd.read_csv(FEATURES_PATH)
X = data.drop("label", axis=1)
y = data["label"]

# 2️⃣ Train RandomForest model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# 3️⃣ Save model in backend/models/
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(MODEL_PATH, "wb") as f:
    pickle.dump(model, f)

print(f"Model trained and saved at: {MODEL_PATH}")
