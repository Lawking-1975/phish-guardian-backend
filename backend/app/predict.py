# backend/app/predict.py
import os
import joblib
from .utils import normalize_url, extract_domain_parts, is_ip, suggest_closest_whitelist, extract_features
from .db import get_connection

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "model.pkl")

# Load model
try:
    MODEL = joblib.load(MODEL_PATH)
    print(f"✅ Loaded ML model from {MODEL_PATH}")
except Exception as e:
    MODEL = None
    print(f"❌ Failed to load model: {e}")

def log_prediction(url, label, confidence, source="api"):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO urls (url, label, confidence, source)
        VALUES (?, ?, ?, ?)
    """, (url, label, confidence if confidence is not None else None, source))
    conn.commit()
    conn.close()

def predict_url(url: str, model=None, whitelist=None):
    if model is None:
        model = MODEL
    if whitelist is None:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT official_domain, category, canonical_url FROM whitelist")
        rows = c.fetchall()
        whitelist = [{"domain": r["official_domain"].strip().lower(),
                      "category": r["category"],
                      "canonical_url": r["canonical_url"]} for r in rows]

    url = url.strip()
    if not url:
        return {"url": url, "error": "Empty URL"}

    try:
        normalized = normalize_url(url)
    except Exception as e:
        log_prediction(url, 0, 0)
        return {"url": url, "normalized": None, "status": "phishing", "confidence": 0, "reason": f"normalize_error:{e}"}

    host_parts = extract_domain_parts(normalized)
    domain = host_parts.get("domain", "").lower()

    # Exact whitelist match
    for w in whitelist:
        if w["domain"] == domain:
            log_prediction(url, 0, 100)  # 0 = legit
            return {
                "url": url,
                "normalized": normalized,
                "status": "legit",
                "confidence": 100,
                "reason": "exact_whitelist",
                "suggested_url": w.get("canonical_url")
            }

    # IP address -> phishing
    if is_ip(host_parts.get("host", "")):
        log_prediction(url, 1, 0)
        return {"url": url, "normalized": normalized, "status": "phishing", "confidence": 0, "reason": "ip_host"}

    # If no ML model, fallback to suggestion only
    if model is None:
        suggestion = suggest_closest_whitelist(url, whitelist)
        log_prediction(url, 1, 0)
        return {"url": url, "normalized": normalized, "status": "phishing",
                "confidence": 0, "reason": "no_model_fallback",
                "suggested_url": suggestion.get("suggested_url") if suggestion else None}

    # ML prediction
    features = extract_features(normalized)
    try:
        pred = int(model.predict(features)[0])
        proba = model.predict_proba(features)[0] if hasattr(model, "predict_proba") else None
        confidence = round(float(proba[pred]) * 100, 2) if proba is not None else "N/A"
    except Exception as e:
        log_prediction(url, 1, 0)
        return {"url": url, "normalized": normalized, "status": "phishing", "confidence": 0, "reason": f"model_error:{e}"}

    # Suggest closest whitelist URL
    suggestion = suggest_closest_whitelist(url, whitelist)
    HIGH_SIM = 0.85  # similarity threshold
    if pred == 1 and suggestion and suggestion.get("similarity", 0)/100 >= HIGH_SIM:
        log_prediction(url, 1, confidence)
        return {
            "url": url,
            "normalized": normalized,
            "status": "phishing",
            "confidence": confidence,
            "reason": "ml_phishing_high_similarity",
            "suggested_url": suggestion.get("suggested_url")
        }

    # Normal result
    status = "phishing" if pred == 1 else "legit"
    log_prediction(url, pred, confidence)
    return {
        "url": url,
        "normalized": normalized,
        "status": status,
        "confidence": confidence,
        "reason": "ml_prediction",
        "suggested_url": suggestion.get("suggested_url") if suggestion else None
    }
