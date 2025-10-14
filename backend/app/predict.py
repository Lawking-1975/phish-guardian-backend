# backend/app/predict.py
from pathlib import Path
import joblib
import sqlite3
import os
from .utils import normalize_url, suggest_closest_whitelist, extract_domain_parts, is_ip

# Get directory of this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# MODEL path (use raw string)
MODEL_PATH = os.path.join(BASE_DIR, "models", "model.pkl")

# Load model with joblib (safer for sklearn artifacts)
try:
    MODEL = joblib.load(MODEL_PATH)
    print("ML model loaded successfully (joblib)")
except Exception as e:
    MODEL = None
    print(f"Failed to load model: {e}")

# -------------------------
# Feature extraction (same features used in training)
# -------------------------
def extract_features(url: str):
    """
    Return a 2D list [[f1,f2,...]] compatible with sklearn predict.
    Keep this aligned with what you used during training.
    """
    # Normalize first (we expect normalized like http://domain/path)
    u = url.strip()
    # simple lexical features (adjust if your training used different ones)
    num_dots = u.count(".")
    url_len = len(u)
    num_dash = u.count("-")
    has_at = int("@" in u)
    has_https = int(u.startswith("https"))
    return [[num_dots, url_len, num_dash, has_at, has_https]]

# -------------------------
# DB logging helper
# -------------------------
def log_prediction(original_url: str, label: int, confidence: float, source: str = "api"):
    """Insert a row into urls DB (creates table if not present)."""
    from .db import get_connection
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            label INTEGER,
            confidence REAL,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("INSERT INTO urls (url, label, confidence, source) VALUES (?, ?, ?, ?)",
              (original_url, label, confidence if confidence is not None else None, source))
    conn.commit()
    # do not close global connection if your get_connection manages singleton; close if using local conn
    # conn.close()

# -------------------------
# Predict function
# -------------------------
def predict_url(url: str, model=None, whitelist=None):
    """
    Predict if a URL is legit (1) or phishing (0).
    Returns: dict with url, normalized, status, confidence (0..100), suggestion (if phishing), reason
    """
    if model is None:
        model = MODEL
    if whitelist is None:
        # lazy import to avoid circulars; main should pass WHITELIST ideally
        from .db import get_connection
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT official_domain, category, canonical_url FROM whitelist")
        rows = c.fetchall()
        whitelist = [
            {"domain": r["official_domain"].strip().lower(), "category": r["category"], "canonical_url": r["canonical_url"]}
            for r in rows if r["official_domain"]
        ]

    url_str = url.strip()
    if not url_str:
        return {"url": url_str, "error": "Empty URL"}

    # Normalize
    try:
        normalized = normalize_url(url_str)
    except Exception as e:
        log_prediction(url_str, 0, 0.0)
        return {"url": url_str, "normalized": None, "status": "phishing", "confidence": 0.0, "reason": f"normalize_error:{e}"}

    # IP host -> suspicious by default
    host_parts = extract_domain_parts(normalized)
    host = host_parts.get("host", "")
    if is_ip(host):
        log_prediction(url_str, 0, 0.0)
        return {"url": url_str, "normalized": normalized, "status": "phishing", "confidence": 0.0, "reason": "ip_host"}

    # Exact whitelist override: if domain exactly matches whitelist, return legit with confidence 100%
    domain = host_parts.get("domain", "").lower()
    exact = None
    for w in whitelist:
        if w.get("domain") == domain:
            exact = w
            break
    if exact:
        log_prediction(url_str, 1, 100.0)
        return {
            "url": url_str,
            "normalized": normalized,
            "status": "legit",
            "confidence": 100.0,
            "reason": "exact_whitelist",
            "suggested_url": exact.get("canonical_url") or f"https://{exact.get('domain')}"
        }

    # If no model, be conservative (mark suspicious and suggest if close)
    if model is None:
        suggestion = suggest_closest_whitelist(url_str, whitelist)
        log_prediction(url_str, 0, 0.0)
        return {"url": url_str, "normalized": normalized, "status": "phishing", "confidence": 0.0, "suggestion": suggestion, "reason": "no_model_fallback"}

    # Build features and predict
    features = extract_features(normalized)
    try:
        pred = int(model.predict(features)[0])
    except Exception as e:
        log_prediction(url_str, 0, 0.0)
        return {"url": url_str, "normalized": normalized, "status": "phishing", "confidence": 0.0, "reason": f"model_predict_error:{e}"}

    # confidence/proba if available
    confidence = None
    try:
        proba = model.predict_proba(features)[0]
        confidence = round(float(proba[pred]) * 100.0, 2)
    except Exception:
        confidence = None

    # If predicted legit but domain is suspiciously similar to whitelist, better to mark phishing (safety)
    suggestion = suggest_closest_whitelist(url_str, whitelist)
    similarity_fraction = (suggestion.get("similarity", 0) / 100.0) if suggestion else 0.0
    # high similarity cutoff (typosquat)
    HIGH_SIM = 0.85
    if pred == 1 and suggestion and similarity_fraction >= HIGH_SIM and suggestion.get("suggested_url"):
        # treat as phishing/suspicious
        log_prediction(url_str, 0, confidence or 0.0)
        return {
            "url": url_str,
            "normalized": normalized,
            "status": "phishing",
            "confidence": confidence,
            "suggestion": suggestion,
            "reason": "ml_legit_but_high_similarity_typosquat"
        }

    # Final result
    log_prediction(url_str, pred, confidence or 0.0)
    result = {
        "url": url_str,
        "normalized": normalized,
        "status": "legit" if pred == 1 else "phishing",
        "confidence": confidence,
        "reason": "ml_prediction"
    }
    if pred == 0 and suggestion:
        result["suggestion"] = suggestion
    return result
