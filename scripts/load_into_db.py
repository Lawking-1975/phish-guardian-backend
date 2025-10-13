# scripts/load_into_db.py
import pandas as pd
from backend.app import db, utils
db.create_tables()

df = pd.read_csv("backend/data/merged.csv", dtype=str, keep_default_na=False)

for i, row in df.iterrows():
    url = row["original_url"]
    try:
        normalized = utils.normalize_url(url)
        parts = utils.extract_domain_parts(normalized)
        label = row.get("label")
        label_norm = None
        if label and label.strip().lower() in ("1","true","legit","clean","benign"):
            label_norm = 1
        elif label and label.strip().lower() in ("0","phish","malicious","malware","suspicious"):
            label_norm = 0
        db.insert_url(original_url=url, normalized_url=normalized, domain=parts["domain"], path=parts["path"], label=label_norm, source=row.get("source"))
    except Exception as e:
        print("skip row", i, e)
