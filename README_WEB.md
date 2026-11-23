# Library Management System — Web Edition

This adds a Flask web interface to the existing Python + SQLite project.

## Features
- Dashboard statistics
- Add, search, update and delete books (books with transaction history are protected from deletion)
- Register, update and delete members (members with transaction history are protected from deletion)
- Issue and return books
- Transaction history and overdue fine display
- Responsive layout for mobile and desktop

## Run locally
1. Keep `app.py`, `database.py`, and `library_service.py` in the same project folder.
2. Install dependencies: `pip install -r requirements.txt`
3. Start the site: `python app.py`
4. Open `http://127.0.0.1:5000`

The app initializes the existing SQLite database using `init_db()`. Back up `library.db` before testing with important records.

## Deployment
Deploy this Flask app on a Python-capable host. GitHub Pages cannot run Flask or host a persistent SQLite database. Use a persistent disk for SQLite on your chosen host, or move to a managed database for production. Set a strong `SECRET_KEY`, disable debug mode, and use the included Procfile with a production WSGI server such as Gunicorn.
