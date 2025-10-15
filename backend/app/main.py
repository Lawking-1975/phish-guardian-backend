# backend/app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
import sqlite3
import joblib

# -------------------------
# FastAPI app
# -------------------------
app = FastAPI(title="Phish Guardian API")

# -------------------------
# CORS settings
# -------------------------
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://phish-guardian.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Request body
# -------------------------
class URLItem(BaseModel):
    url: str

# -------------------------
# Predict endpoint
# -------------------------
@app.post("/predict")
def predict(item: URLItem):
    from .predict import predict_url  # lazy import to avoid circular issues
    from app.main import MODEL, WHITELIST  # lazy load
    if MODEL is None:
        raise HTTPException(status_code=500, detail="MODEL not loaded")
    return predict_url(item.url, MODEL, WHITELIST)

@app.get("/")
def root():
    return {"message": "Phish Guardian API is running!"}

@app.get("/healthz")
def health_check():
    return {"status": "ok"}

# -------------------------
# Lazy load model and whitelist
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "whitelist.db")
MODEL_PATH = os.path.join(BASE_DIR, "models", "model.pkl")

try:
    MODEL = joblib.load(MODEL_PATH)
    print(f"✅ Loaded ML model from {MODEL_PATH}")
except Exception as e:
    MODEL = None
    print(f"❌ Failed to load model: {e}")

def load_whitelist():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT official_domain, category, canonical_url FROM whitelist")
        rows = c.fetchall()
        conn.close()
        return [
            {"domain": r["official_domain"].strip().lower(),
             "category": r["category"].strip(),
             "canonical_url": r["canonical_url"].strip() if r["canonical_url"] else None
            } for r in rows if r["official_domain"]
        ]
    except Exception as e:
        print(f"❌ Failed to load whitelist: {e}")
        return []

WHITELIST = load_whitelist()
print(f"✅ Loaded {len(WHITELIST)} whitelist entries")
