# scripts/build_whitelist.py
import pandas as pd
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "backend" / "data"
DB_PATH = DATA_DIR / "urls.db"
WHITELIST_CSV = DATA_DIR / "whitelist.csv"

print(f"🔍 Loading whitelist from: {WHITELIST_CSV}")
df = pd.read_csv(WHITELIST_CSV)

# Normalize columns
df.columns = [c.strip().lower() for c in df.columns]

# Expected columns
expected = {"official_domain", "category", "notes", "canonical_url"}
missing = expected - set(df.columns)
if missing:
    raise ValueError(f"⚠️ Missing required columns in whitelist.csv: {missing}")

# Connect to DB
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Drop and recreate whitelist table
cur.execute("DROP TABLE IF EXISTS whitelist")
cur.execute("""
CREATE TABLE whitelist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    official_domain TEXT,
    category TEXT,
    notes TEXT,
    canonical_url TEXT
)
""")

# Insert new data
df.to_sql("whitelist", conn, if_exists="append", index=False)
conn.commit()

print(f"✅ Updated whitelist.db with {len(df)} entries.")
conn.close()
