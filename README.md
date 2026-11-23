# Library Management System (Python + SQLite)

A clean, modular Python project for managing books, members, book issues, returns, and overdue fines (in INR).

## Project Structure

- `main.py` — Command-line interface (CLI) menu.
- `database.py` — SQLite connection and schema initialization with sample data.
- `library_service.py` — Core operations (add/search books, register members, issue/return books, calculate fines).
- `test_library.py` — Unit tests using Python's `unittest`.

## How to Run

1. Make sure Python 3.8+ is installed (uses standard library `sqlite3` only — no external `pip` packages needed).
2. Run the app:
   ```bash
   python main.py
   ```
3. Run unit tests:
   ```bash
   python -m unittest test_library.py
   ```
