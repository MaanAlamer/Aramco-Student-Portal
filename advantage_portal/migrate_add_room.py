import sqlite3

DB_PATH = "advantage.db"

def column_exists(conn, table, column):
    cur = conn.execute(f"PRAGMA table_info({table})")
    cols = [row[1] for row in cur.fetchall()]
    return column in cols

conn = sqlite3.connect(DB_PATH)

if not column_exists(conn, "students", "room"):
    conn.execute("ALTER TABLE students ADD COLUMN room TEXT")
    conn.commit()
    print("✅ Added column: students.room")
else:
    print("ℹ️ Column students.room already exists")

conn.close()
