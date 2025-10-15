# backend/app/predict.py
import os
import joblib
from .utils import normalize_url, extract_domain_parts, is_ip, suggest_closest_whitelist, extract_features
from .db import get_connection

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "model.pkl")

# Load ML model
try:
    MODEL = joblib.load(MODEL_PATH)
    print(f"✅ Loaded ML model from {MODEL_PATH}")
except Exception as e:
    MODEL = None
    print(f"❌ Failed to load model: {e}")

def log_prediction(url, label, confidence, source="api"):
    """Log prediction to the database."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO urls (url, label, confidence, source)
        VALUES (?, ?, ?, ?)
    """, (url, label, confidence if confidence is not None else None, source))
    conn.commit()
    conn.close()

def predict_url(url: str, model=None, whitelist=None):
    """Predict if a URL is phishing or legit, with suggestions."""
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

    # Normalize URL
    try:
        normalized = normalize_url(url)
    except Exception as e:
        log_prediction(url, 0, 0)
        return {"url": url, "normalized": None, "status": "phishing", "confidence": 0, "reason": f"normalize_error:{e}"}

    host_parts = extract_domain_parts(normalized)
    domain = host_parts.get("domain", "").lower()

    # 1️⃣ Exact whitelist match → legit
    for w in whitelist:
        if w["domain"] == domain:
            log_prediction(url, 1, 100)
            return {
                "url": url,
                "normalized": normalized,
                "status": "legit",
                "confidence": 100,
                "reason": "exact_whitelist",
                "suggested_url": w.get("canonical_url")
            }

    # 2️⃣ IP-based URLs → phishing
    if is_ip(host_parts.get("host", "")):
        log_prediction(url, 0, 0)
        return {"url": url, "normalized": normalized, "status": "phishing", "confidence": 0, "reason": "ip_host"}

    # 3️⃣ Suggestion-based typo-squatting detection
    suggestion = suggest_closest_whitelist(url, whitelist)
    HIGH_SIM = 0.75  # Threshold for typo-squatting
    if suggestion and suggestion.get("similarity", 0)/100 >= HIGH_SIM:
        log_prediction(url, 0, 0)
        return {
            "url": url,
            "normalized": normalized,
            "status": "phishing",
            "confidence": 0,
            "suggestion": suggestion,
            "reason": "typo_squatting_detected"
        }

    # 4️⃣ ML model prediction
    if model is None:
        log_prediction(url, 0, 0)
        return {
            "url": url,
            "normalized": normalized,
            "status": "phishing",
            "confidence": 0,
            "suggestion": suggestion,
            "reason": "no_model_fallback"
        }

    features = extract_features(normalized)
    try:
        pred = int(model.predict(features)[0])
        proba = model.predict_proba(features)[0]
        confidence = round(float(proba[pred]) * 100, 2)
    except Exception as e:
        log_prediction(url, 0, 0)
        return {"url": url, "normalized": normalized, "status": "phishing", "confidence": 0, "reason": f"model_error:{e}"}

    # 5️⃣ ML prediction result
    log_prediction(url, pred, confidence)
    result = {
        "url": url,
        "normalized": normalized,
        "status": "legit" if pred == 1 else "phishing",
        "confidence": confidence,
        "reason": "ml_prediction"
    }
    if suggestion:
        result["suggestion"] = suggestion
    return result
