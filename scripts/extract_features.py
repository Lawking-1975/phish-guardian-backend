# scripts/extract_features.py
"""
Extract features from new_dataset.csv and normalize labels.
Saves to backend/data/features.csv
"""

import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "backend" / "data"
RAW_PATH = DATA_DIR / "new_dataset.csv"
OUT_PATH = DATA_DIR / "features.csv"

print("Loading dataset:", RAW_PATH)
df = pd.read_csv(RAW_PATH)

# Rename label column
if "CLASS_LABEL" in df.columns:
    df = df.rename(columns={"CLASS_LABEL": "label"})

# Normalize labels: -1 → 0 (phish), 1 → 1 (legit)
df["label"] =  (
    df["label"]
    .astype(str)        # ensure string
    .str.strip()        # remove spaces
    .replace({"-1": 0, "1": 1})  # string mapping
    .astype(float)      # back to numbers
    .astype(int)        # final integers
)

print("Label distribution:")
print(df["label"].value_counts(dropna=False))

# Save
df.to_csv(OUT_PATH, index=False)
print(f"Saved normalized features to {OUT_PATH}, rows: {len(df)}")
