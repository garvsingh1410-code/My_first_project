import sqlite3
from datetime import datetime, timedelta

DB_NAME = "library.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT UNIQUE,
            total_copies INTEGER NOT NULL DEFAULT 1,
            available_copies INTEGER NOT NULL DEFAULT 1
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS members (
            member_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            joined_on TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            txn_id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            member_id INTEGER NOT NULL,
            issue_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            return_date TEXT,
            fine_amount REAL DEFAULT 0.0,
            status TEXT NOT NULL DEFAULT 'ISSUED',
            FOREIGN KEY (book_id) REFERENCES books (book_id),
            FOREIGN KEY (member_id) REFERENCES members (member_id)
        )
    """)

    # Seed sample books if empty
    cur.execute("SELECT COUNT(*) AS cnt FROM books")
    if cur.fetchone()["cnt"] == 0:
        sample_books = [
            ("Python Crash Course", "Eric Matthes", "978-1593279288", 4, 4),
            ("Clean Code", "Robert C. Martin", "978-0132350884", 3, 3),
            ("Atomic Habits", "James Clear", "978-0735211292", 5, 5),
            ("Introduction to Algorithms", "Cormen et al.", "978-0262033848", 2, 2),
        ]
        cur.executemany(
            "INSERT INTO books (title, author, isbn, total_copies, available_copies) VALUES (?, ?, ?, ?, ?)",
            sample_books,
        )

    # Seed sample members if empty
    cur.execute("SELECT COUNT(*) AS cnt FROM members")
    if cur.fetchone()["cnt"] == 0:
        today = datetime.now().strftime("%Y-%m-%d")
        sample_members = [
            ("Aarav Sharma", "aarav.sharma@example.com", "9876543210", today),
            ("Priya Nair", "priya.nair@example.com", "9876543211", today),
        ]
        cur.executemany(
            "INSERT INTO members (name, email, phone, joined_on) VALUES (?, ?, ?, ?)",
            sample_members,
        )

    conn.commit()
    conn.close()
