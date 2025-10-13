# backend/app/whitelist.py
from pathlib import Path
import sqlite3
from difflib import SequenceMatcher
from functools import lru_cache

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "urls.db"

def get_conn():
    return sqlite3.connect(str(DB_PATH))

def load_whitelist():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT official_domain, category, canonical_url, notes FROM whitelist")
    rows = c.fetchall()
    conn.close()
    # list of dicts
    wl = [{"domain": r[0].lower(), "category": r[1], "canonical_url": r[2], "notes": r[3]} for r in rows]
    return wl

def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

@lru_cache(maxsize=1)
def whitelist_domains():
    return load_whitelist()

def find_closest(domain: str, cutoff: float = 0.55):
    """
    Return (best_match_dict, similarity_score) or (None, 0).
    domain: naked domain (no scheme), e.g. paypal.com or login.paypal.com
    """
    domain = domain.lower().strip()
    if domain.startswith("www."):
        domain = domain[4:]
    best = None
    best_score = 0.0
    for item in whitelist_domains():
        cand = item["domain"]
        score = similarity(domain, cand)
        if score > best_score:
            best_score = score
            best = item
    if best_score >= cutoff:
        return best, round(best_score, 4)
    return None, 0.0
