# scripts/load_whitelist.py
import csv
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "backend"/"data"/"whitelist.csv"
sys.path.insert(0, str(ROOT / "backend"))  # ensure imports work when run from project root

from app.db import create_tables, insert_whitelist

create_tables()

with open(CSV, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(filter(lambda row: row.strip() and not row.strip().startswith("#"), f))
    count = 0
    for row in reader:
        domain = row.get("official_domain") or row.get("domain") or ""
        category = row.get("category") or ""
        canonical_url = row.get("canonical_url") or ""
        if domain:
            insert_whitelist(domain.strip().lower(), category.strip(), "", canonical_url.strip())
            count += 1

print(f"Inserted/ignored {count} whitelist rows.")
