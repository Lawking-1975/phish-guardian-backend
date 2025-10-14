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
# CORS settings (allow your frontend)
# -------------------------
origins = [
    "http://localhost:5173",  # React dev server
    "http://127.0.0.1:5173",
   "https://phish-guardian-backend-sfp9.vercel.app/" # Replace with your frontend domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Paths for deployment
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "whitelist.db")  # SQLite DB
MODEL_PATH = os.path.join(BASE_DIR, "models", "model.pkl")  # ML model

# -------------------------
# Load ML model safely
# -------------------------
try:
    MODEL = joblib.load(MODEL_PATH)
    print(f"✅ Loaded ML model from {MODEL_PATH}")
except Exception as e:
    MODEL = None
    print(f"❌ Failed to load model: {e}")

# -------------------------
# Initialize SQLite whitelist safely
# -------------------------
def init_db():
    os.makedirs(BASE_DIR, exist_ok=True)  # Ensure directory exists
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
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT official_domain, category, canonical_url FROM whitelist")
        rows = c.fetchall()
        conn.close()
        return [
            {
                "domain": r["official_domain"].strip().lower() if r["official_domain"] else "",
                "category": r["category"].strip() if r["category"] else "",
                "canonical_url": r["canonical_url"].strip() if r["canonical_url"] else None
            }
            for r in rows
            if r["official_domain"]
        ]
    except sqlite3.Error as e:
        print(f"❌ Failed to load whitelist: {e}")
        return []

WHITELIST = load_whitelist()
print(f"✅ Loaded {len(WHITELIST)} whitelist entries")

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
    if MODEL is None:
        raise HTTPException(status_code=500, detail="MODEL not loaded")
    result = predict_url(item.url, MODEL, WHITELIST)
    return result
@app.get("/")
def root():
    return {"message": "Phish Guardian API is running!"}

@app.get("/healthz")
def health_check():
    return {"status": "ok"}
