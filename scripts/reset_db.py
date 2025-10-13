from backend.app.db import get_connection

def recreate_whitelist():
    conn = get_connection()
    c = conn.cursor()

    # Drop old table if exists
    c.execute("DROP TABLE IF EXISTS whitelist")

    # Create clean schema
    c.execute("""
    CREATE TABLE whitelist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        domain TEXT UNIQUE,
        category TEXT
    )
    """)

    conn.commit()
    conn.close()
    print("✅ whitelist table recreated successfully!")

if __name__ == "__main__":
    recreate_whitelist()
