import sqlite3

conn = sqlite3.connect("traffic.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS traffic_data(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    cars INTEGER,
    buses INTEGER,
    bikes INTEGER,
    persons INTEGER,
    total INTEGER,
    traffic_status TEXT
)
""")

conn.commit()
conn.close()

print("Database created successfully!")