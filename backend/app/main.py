# backend/app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os
import joblib
from backend.app.predict import predict_url

# -------------------------
# FastAPI app
# -------------------------
app = FastAPI(title="Phish Guardian API")

# -------------------------
# CORS (update with your frontend domain)
# -------------------------
origins = [
    "http://localhost:5173",
    "https://phish-guardian-backend-sfp9.vercel.app/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Paths
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "model.pkl")
DB_PATH = os.path.join(BASE_DIR, "whitelist.db")

# -------------------------
# Load ML model
# -------------------------
try:
    MODEL = joblib.load(MODEL_PATH)
    print(f"✅ Loaded ML model from {MODEL_PATH}")
except Exception as e:
    MODEL = None
    print(f"❌ Failed to load ML model: {e}")

# -------------------------
# Initialize whitelist DB
# -------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS whitelist (
            official_domain TEXT,
            category TEXT,
            canonical_url TEXT
        )
    """)
    conn.commit()
    conn.close()

def load_whitelist():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT official_domain, category, canonical_url FROM whitelist")
    rows = c.fetchall()
    conn.close()
    whitelist = [
        {
            "domain": r["official_domain"].strip().lower() if r["official_domain"] else "",
            "category": r["category"].strip() if r["category"] else "",
            "canonical_url": r["canonical_url"].strip() if r["canonical_url"] else None
        }
        for r in rows
        if r["official_domain"]
    ]
    print(f"✅ Loaded {len(whitelist)} whitelist entries")
    return whitelist

WHITELIST = load_whitelist()

# -------------------------
# Request model
# -------------------------
class URLItem(BaseModel):
    url: str

# -------------------------
# Predict endpoint
# -------------------------
@app.post("/predict")
def predict(item: URLItem):
    if MODEL is None:
        raise HTTPException(status_code=500, detail="MODEL not loaded")
    result = predict_url(item.url, MODEL, WHITELIST)
    return result

# -------------------------
# Optional: health check
# -------------------------
@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": MODEL is not None, "whitelist_count": len(WHITELIST)}
