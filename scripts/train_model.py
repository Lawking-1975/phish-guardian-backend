# scripts/train_model.py
"""
Train a baseline model on features.csv
Saves the trained model to backend/models/model.pkl
"""

import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "backend" / "data" / "features.csv"
MODEL_DIR = PROJECT_ROOT / "backend" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODEL_DIR / "model.pkl"

print(f"Loading features from: {DATA_PATH}")
df = pd.read_csv(DATA_PATH)

# Drop rows without labels
df = df.dropna(subset=["label"])

# Features (all numeric except label)
selected_features = [
    "NumDots",
    "UrlLength",
    "NumDash",
    "AtSymbol",
    "HttpsInHostname"
]

X = df[selected_features]
y = df["label"]
print(f"Dataset shape: {df.shape}")
print("Label distribution:")
print(y.value_counts())

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Train model
print("Training RandomForest...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print("Classification Report:")
print(classification_report(y_test, y_pred, digits=4))

# Save model
joblib.dump(model, MODEL_PATH)
print(f"✅ Model saved to {MODEL_PATH}")
