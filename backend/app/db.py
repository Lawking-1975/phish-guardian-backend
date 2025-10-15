# backend/app/db.py
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "whitelist.db")

def get_connection():
    """Return a new SQLite connection."""
    os.makedirs(BASE_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_connection()
    c = conn.cursor()
    # Whitelist table
    c.execute("""
        CREATE TABLE IF NOT EXISTS whitelist (
            official_domain TEXT PRIMARY KEY,
            category TEXT,
            notes TEXT,
            canonical_url TEXT
        )
    """)
    # Prediction logs
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
    conn.commit()
    conn.close()

def insert_whitelist(domain: str, category: str, notes: str, canonical_url: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT OR IGNORE INTO whitelist (official_domain, category, notes, canonical_url)
        VALUES (?, ?, ?, ?)
    """, (domain, category, notes, canonical_url))
    conn.commit()
    conn.close()
