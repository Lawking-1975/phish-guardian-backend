# backend/app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.app.predict import MODEL, predict_url
from backend.app.db import get_connection
import sqlite3

app = FastAPI(title="Phish Guardian API")
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow your frontend (adjust port if needed)
origins = [
    "http://localhost:5173",  # React dev server
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow POST, GET, OPTIONS, etc.
    allow_headers=["*"],  # Allow all headers
)

# -------------------------
# Load whitelist
# -------------------------
def load_whitelist():
    conn = get_connection()
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

WHITELIST = load_whitelist()
print(f"Loaded {len(WHITELIST)} whitelist entries")

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
