import sqlite3
import os
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    title TEXT,
    body TEXT
)
""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER,
        name TEXT,
        body TEXT
    )
    """)

    conn.commit()
    conn.close()


def seed_data():
    conn = get_db()
    cursor = conn.cursor()

    existing = cursor.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
    if existing > 0:
        print("Data already seeded")
        conn.close()
        return

    print("Seeding data...")

    posts = requests.get("https://jsonplaceholder.typicode.com/posts").json()
    comments = requests.get("https://jsonplaceholder.typicode.com/comments").json()

    for post in posts:
        cursor.execute(
    "INSERT INTO posts (id, user_id, title, body) VALUES (?, ?, ?, ?)",
    (post["id"], post["userId"], post["title"], post["body"])
)

    for comment in comments:
        cursor.execute(
            "INSERT INTO comments (post_id, name, body) VALUES (?, ?, ?)",
            (comment["postId"], comment["name"], comment["body"])
        )

    conn.commit()
    conn.close()

    print("Seeding done ✅")