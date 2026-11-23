from datetime import datetime, timedelta
from database import get_connection

FINE_PER_DAY_INR = 5.0
DEFAULT_LOAN_DAYS = 14


def add_book(title: str, author: str, isbn: str, copies: int = 1):
    if copies < 1:
        raise ValueError("Copies must be at least 1.")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO books (title, author, isbn, total_copies, available_copies)
        VALUES (?, ?, ?, ?, ?)
        """,
        (title.strip(), author.strip(), isbn.strip() or None, copies, copies),
    )
    conn.commit()
    book_id = cur.lastrowid
    conn.close()
    return book_id


def list_books(search: str = ""):
    conn = get_connection()
    cur = conn.cursor()
    if search.strip():
        pattern = f"%{search.strip()}%"
        cur.execute(
            """
            SELECT * FROM books
            WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ?
            ORDER BY book_id ASC
            """,
            (pattern, pattern, pattern),
        )
    else:
        cur.execute("SELECT * FROM books ORDER BY book_id ASC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def add_member(name: str, email: str, phone: str = ""):
    conn = get_connection()
    cur = conn.cursor()
    joined_on = datetime.now().strftime("%Y-%m-%d")
    cur.execute(
        """
        INSERT INTO members (name, email, phone, joined_on)
        VALUES (?, ?, ?, ?)
        """,
        (name.strip(), email.strip() or None, phone.strip() or None, joined_on),
    )
    conn.commit()
    member_id = cur.lastrowid
    conn.close()
    return member_id


def list_members():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM members ORDER BY member_id ASC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def issue_book(book_id: int, member_id: int, loan_days: int = DEFAULT_LOAN_DAYS):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM books WHERE book_id = ?", (book_id,))
    book = cur.fetchone()
    if not book:
        conn.close()
        raise ValueError(f"Book ID {book_id} not found.")
    if book["available_copies"] <= 0:
        conn.close()
        raise ValueError(f"No available copies for '{book['title']}'.")

    cur.execute("SELECT * FROM members WHERE member_id = ?", (member_id,))
    member = cur.fetchone()
    if not member:
        conn.close()
        raise ValueError(f"Member ID {member_id} not found.")

    issue_dt = datetime.now()
    due_dt = issue_dt + timedelta(days=loan_days)

    cur.execute(
        """
        INSERT INTO transactions (book_id, member_id, issue_date, due_date, status)
        VALUES (?, ?, ?, ?, 'ISSUED')
        """,
        (
            book_id,
            member_id,
            issue_dt.strftime("%Y-%m-%d"),
            due_dt.strftime("%Y-%m-%d"),
        ),
    )
    cur.execute(
        """
        UPDATE books
        SET available_copies = available_copies - 1
        WHERE book_id = ?
        """,
        (book_id,),
    )

    conn.commit()
    txn_id = cur.lastrowid
    conn.close()
    return {
        "txn_id": txn_id,
        "book_title": book["title"],
        "member_name": member["name"],
        "issue_date": issue_dt.strftime("%Y-%m-%d"),
        "due_date": due_dt.strftime("%Y-%m-%d"),
    }


def return_book(txn_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM transactions WHERE txn_id = ?", (txn_id,))
    txn = cur.fetchone()
    if not txn:
        conn.close()
        raise ValueError(f"Transaction ID {txn_id} not found.")
    if txn["status"] == "RETURNED":
        conn.close()
        raise ValueError(f"Transaction ID {txn_id} is already returned.")

    now_dt = datetime.now()
    due_dt = datetime.strptime(txn["due_date"], "%Y-%m-%d")
    overdue_days = max(0, (now_dt.date() - due_dt.date()).days)
    fine = round(overdue_days * FINE_PER_DAY_INR, 2)
    return_str = now_dt.strftime("%Y-%m-%d")

    cur.execute(
        """
        UPDATE transactions
        SET return_date = ?, fine_amount = ?, status = 'RETURNED'
        WHERE txn_id = ?
        """,
        (return_str, fine, txn_id),
    )
    cur.execute(
        """
        UPDATE books
        SET available_copies = available_copies + 1
        WHERE book_id = ?
        """,
        (txn["book_id"],),
    )

    conn.commit()
    conn.close()
    return {
        "txn_id": txn_id,
        "return_date": return_str,
        "overdue_days": overdue_days,
        "fine_inr": fine,
    }


def list_transactions(only_active: bool = False):
    conn = get_connection()
    cur = conn.cursor()
    query = """
        SELECT t.txn_id, b.title AS book_title, m.name AS member_name,
               t.issue_date, t.due_date, t.return_date, t.fine_amount, t.status
        FROM transactions t
        JOIN books b ON t.book_id = b.book_id
        JOIN members m ON t.member_id = m.member_id
    """
    if only_active:
        query += " WHERE t.status = 'ISSUED'"
    query += " ORDER BY t.txn_id DESC"
    cur.execute(query)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows
