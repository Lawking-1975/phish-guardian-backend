import sqlite3

db_path = "backend/data/urls.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Count rows
cur.execute("SELECT COUNT(*) FROM urls;")
count = cur.fetchone()[0]
print(f"Total rows in DB: {count}")

# Peek a few rows
cur.execute("SELECT id, original_url, label FROM urls LIMIT 5;")
rows = cur.fetchall()
for r in rows:
    print(r)

conn.close()
