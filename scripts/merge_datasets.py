# scripts/merge_datasets.py
import pandas as pd
from pathlib import Path

RAW = Path("backend/data/raw")
OUT = Path("backend/data")
OUT.mkdir(parents=True, exist_ok=True)

def unify_file(path: Path):
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    # heuristic mapping: try to find URL and label columns
    columns = {c.lower():c for c in df.columns}
    url_col = None
    for c in ["url","url_address","phish_url","link"]:
        if c in columns:
            url_col = columns[c]
            break
    label_col = None
    for c in ["label","status","phish","target"]:
        if c in columns:
            label_col = columns[c]
            break
    if url_col is None:
        print("No URL column found in", path)
        return pd.DataFrame()
    out = pd.DataFrame()
    out["original_url"] = df[url_col]
    if label_col:
        out["label"] = df[label_col]
    else:
        out["label"] = ""
    out["source"] = path.name
    return out

def main():
    files = list(RAW.glob("*.csv"))
    frames = []
    for f in files:
        try:
            frames.append(unify_file(f))
        except Exception as e:
            print("error", f, e)
    if not frames:
        print("No raw CSVs found in", RAW)
        return
    merged = pd.concat(frames, ignore_index=True)
    merged.to_csv(OUT / "merged.csv", index=False)
    print("Merged", len(merged), "rows ->", OUT / "merged.csv")

if __name__ == "__main__":
    main()
