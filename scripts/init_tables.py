# scripts/init_tables.py
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "backend" / "data" / "urls.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

print("DB path:", DB_PATH)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# create urls table (prediction history)
c.execute("""
CREATE TABLE IF NOT EXISTS urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    label INTEGER,
    source TEXT,
    confidence REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# create whitelist table (if not present)
c.execute("""
CREATE TABLE IF NOT EXISTS whitelist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    official_domain TEXT UNIQUE,
    category TEXT,
    notes TEXT,
    canonical_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()
print("✅ Database initialized with tables: urls, whitelist")
