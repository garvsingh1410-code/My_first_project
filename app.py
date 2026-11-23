from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import date
from database import init_db, get_connection
from library_service import (
    add_book, list_books, add_member, list_members,
    issue_book, return_book, list_transactions,
)

app = Flask(__name__)
app.secret_key = "change-this-to-a-long-random-secret"
init_db()


def dashboard_data():
    books = list_books()
    members = list_members()
    transactions = list_transactions()
    active = [t for t in transactions if t["status"] == "ISSUED"]
    return {
        "book_titles": len(books),
        "total_copies": sum(b["total_copies"] for b in books),
        "available": sum(b["available_copies"] for b in books),
        "members": len(members),
        "issued": len(active),
        "overdue": sum(1 for t in active if t["due_date"] < __import__("datetime").date.today().isoformat()),
    }


@app.get("/")
def home():
    search = request.args.get("search", "").strip()
    books = list_books(search)
    members = list_members()
    transactions = list_transactions()
    active_transactions = [t for t in transactions if t["status"] == "ISSUED"]
    return render_template(
        "index.html",
        stats=dashboard_data(),
        books=books,
        members=members,
        transactions=transactions,
        active_transactions=active_transactions,
        search=search,
        today_iso=date.today().isoformat(),
    )


@app.post("/books/add")
def books_add():
    try:
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        isbn = request.form.get("isbn", "").strip()
        copies = int(request.form.get("copies", "1"))
        if not title or not author:
            raise ValueError("Book title and author are required.")
        add_book(title, author, isbn, copies)
        flash("Book added successfully.", "success")
    except Exception as exc:
        flash(f"Could not add book: {exc}", "error")
    return redirect(url_for("home") + "#books")


@app.post("/books/<int:book_id>/update")
def books_update(book_id):
    try:
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        isbn = request.form.get("isbn", "").strip() or None
        total = int(request.form.get("total_copies", "1"))
        if not title or not author or total < 1:
            raise ValueError("Enter a title, author and at least one copy.")
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM books WHERE book_id = ?", (book_id,))
        book = cur.fetchone()
        if not book:
            raise ValueError("Book not found.")
        borrowed = book["total_copies"] - book["available_copies"]
        if total < borrowed:
            raise ValueError(f"Cannot set total below {borrowed} borrowed copies.")
        cur.execute(
            """UPDATE books SET title=?, author=?, isbn=?, total_copies=?,
               available_copies=? WHERE book_id=?""",
            (title, author, isbn, total, total - borrowed, book_id),
        )
        conn.commit()
        conn.close()
        flash("Book updated.", "success")
    except Exception as exc:
        try:
            conn.close()
        except Exception:
            pass
        flash(f"Could not update book: {exc}", "error")
    return redirect(url_for("home") + "#books")


@app.post("/books/<int:book_id>/delete")
def books_delete(book_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM transactions WHERE book_id=?", (book_id,))
        if cur.fetchone()[0]:
            flash("This book has transaction history and cannot be deleted.", "error")
        else:
            cur.execute("DELETE FROM books WHERE book_id=?", (book_id,))
            conn.commit()
            flash("Book deleted.", "success")
    except Exception as exc:
        flash(f"Could not delete book: {exc}", "error")
    finally:
        conn.close()
    return redirect(url_for("home") + "#books")


@app.post("/members/add")
def members_add():
    try:
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        if not name:
            raise ValueError("Member name is required.")
        add_member(name, email, phone)
        flash("Member registered successfully.", "success")
    except Exception as exc:
        flash(f"Could not register member: {exc}", "error")
    return redirect(url_for("home") + "#members")


@app.post("/members/<int:member_id>/update")
def members_update(member_id):
    conn = get_connection()
    try:
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip() or None
        phone = request.form.get("phone", "").strip() or None
        if not name:
            raise ValueError("Member name is required.")
        cur = conn.cursor()
        cur.execute("UPDATE members SET name=?, email=?, phone=? WHERE member_id=?",
                    (name, email, phone, member_id))
        if cur.rowcount == 0:
            raise ValueError("Member not found.")
        conn.commit()
        flash("Member details updated.", "success")
    except Exception as exc:
        flash(f"Could not update member: {exc}", "error")
    finally:
        conn.close()
    return redirect(url_for("home") + "#members")


@app.post("/members/<int:member_id>/delete")
def members_delete(member_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM transactions WHERE member_id=?", (member_id,))
        if cur.fetchone()[0]:
            flash("This member has transaction history and cannot be deleted.", "error")
        else:
            cur.execute("DELETE FROM members WHERE member_id=?", (member_id,))
            conn.commit()
            flash("Member deleted.", "success")
    except Exception as exc:
        flash(f"Could not delete member: {exc}", "error")
    finally:
        conn.close()
    return redirect(url_for("home") + "#members")


@app.post("/issue")
def issue():
    try:
        book_id = int(request.form["book_id"])
        member_id = int(request.form["member_id"])
        days = int(request.form.get("loan_days", "14"))
        if days < 1:
            raise ValueError("Loan period must be at least one day.")
        issue_book(book_id, member_id, days)
        flash("Book issued successfully.", "success")
    except Exception as exc:
        flash(f"Could not issue book: {exc}", "error")
    return redirect(url_for("home") + "#circulation")


@app.post("/return/<int:txn_id>")
def return_one(txn_id):
    try:
        result = return_book(txn_id)
        flash(
            f"Book returned. Overdue: {result['overdue_days']} days; "
            f"fine: ₹{result['fine_inr']:.2f}.",
            "success",
        )
    except Exception as exc:
        flash(f"Could not return book: {exc}", "error")
    return redirect(url_for("home") + "#circulation")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
