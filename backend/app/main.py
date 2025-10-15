# backend/app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
import csv
import joblib
from .db import create_tables, insert_whitelist, get_connection
from .predict import predict_url

# -------------------------
# FastAPI app
# -------------------------
app = FastAPI(title="Phish Guardian API")

# -------------------------
# CORS settings
# -------------------------
origins = [
    "http://localhost:5173",  # React dev server
    "http://127.0.0.1:5173",
    "https://your-frontend-domain.com"  # replace with actual frontend domain
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
WHITELIST_CSV_PATH = os.path.join(BASE_DIR,"whitelist.csv")

# -------------------------
# Load ML model
# -------------------------
try:
    MODEL = joblib.load(MODEL_PATH)
    print(f"✅ Loaded ML model from {MODEL_PATH}")
except Exception as e:
    MODEL = None
    print(f"❌ Failed to load model: {e}")

# -------------------------
# Initialize database & whitelist
# -------------------------
def init_whitelist():
    """
    Create tables if missing and populate whitelist from CSV.
    Returns a list of whitelist entries.
    """
    create_tables()  # ensures whitelist & urls tables exist
    whitelist = []
    if os.path.exists(WHITELIST_CSV_PATH):
        with open(WHITELIST_CSV_PATH, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(filter(lambda row: row.strip() and not row.strip().startswith("#"), f))
            for row in reader:
                domain = row.get("official_domain") or ""
                category = row.get("category") or ""
                canonical_url = row.get("canonical_url") or ""
                notes = row.get("notes") or ""
                if domain:
                    insert_whitelist(domain.strip().lower(), category.strip(), notes.strip(), canonical_url.strip())
                    whitelist.append({
                        "domain": domain.strip().lower(),
                        "category": category.strip(),
                        "canonical_url": canonical_url.strip()
                    })
    else:
        print(f"❌ Whitelist CSV not found at {WHITELIST_CSV_PATH}")
    return whitelist

WHITELIST = init_whitelist()
print(f"✅ Loaded {len(WHITELIST)} whitelist entries")

# -------------------------
# Request body
# -------------------------
class URLItem(BaseModel):
    url: str

# -------------------------
# Endpoints
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
