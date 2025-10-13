# backend/app/db.py
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "urls.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def get_connection():
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT,
                label INTEGER,
                confidence REAL,
                source TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS whitelist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                official_domain TEXT UNIQUE,
                category TEXT,
                notes TEXT,
                canonical_url TEXT
            )
        """)
        conn.commit()

def insert_url(url: str, label: int, confidence: float, source: str = "api"):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO urls (url, label, confidence, source) VALUES (?, ?, ?, ?)",
            (url, label, confidence, source)
        )
        conn.commit()

def insert_whitelist(official_domain: str, category: str, notes: str = "", canonical_url: str = ""):
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO whitelist (official_domain, category, notes, canonical_url) VALUES (?, ?, ?, ?)",
            (official_domain.lower(), category, notes, canonical_url)
        )
        conn.commit()

def get_whitelist():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT official_domain, category, notes, canonical_url FROM whitelist")
        rows = c.fetchall()
        return [dict(r) for r in rows]
