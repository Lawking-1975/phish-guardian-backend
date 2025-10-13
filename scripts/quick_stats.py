# scripts/quick_stats.py
"""
Quick dataset statistics for backend/data/features.csv
Usage:
    python -m scripts.quick_stats
"""

from pathlib import Path
import pandas as pd
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FEATURES_PATH = PROJECT_ROOT / "backend" / "data" / "features.csv"

if not FEATURES_PATH.exists():
    print("ERROR: features.csv not found at:", FEATURES_PATH)
    print("Run: python -m scripts.extract_features")
    sys.exit(1)

df = pd.read_csv(FEATURES_PATH)
print("features.csv path:", FEATURES_PATH)
print("Shape:", df.shape)
if "label" in df.columns:
    print("Label counts (including blanks):")
    # show normalized label counts
    print(df["label"].value_counts(dropna=False).head(20))
else:
    print("No 'label' column present in features.csv")

print("\nSample rows:")
print(df.head(8).to_string(index=False))
