# scripts/load_whitelist.py
import csv
from pathlib import Path
import sys
import os

# Get project root (two levels up from this script)
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))  # backend folder is treated as package

from app.db import create_tables, insert_whitelist

CSV = ROOT / "backend" / "data" / "whitelist.csv"

# Create tables
create_tables()

# Load CSV
with open(CSV, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(filter(lambda r: r.strip() and not r.strip().startswith("#"), f))
    count = 0
    for row in reader:
        domain = row.get("official_domain") or ""
        category = row.get("category") or ""
        canonical_url = row.get("canonical_url") or ""
        if domain:
            insert_whitelist(domain.strip().lower(), category.strip(), "", canonical_url.strip())
            count += 1

print(f"✅ Inserted/ignored {count} whitelist rows.")
