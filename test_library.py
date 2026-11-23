import os
import tempfile
import unittest
import database
from library_service import add_book, add_member, issue_book, list_books, return_book


class TestLibraryManagement(unittest.TestCase):
    def setUp(self):
        self.tmp_fd, self.tmp_path = tempfile.mkstemp(suffix=".db")
        os.close(self.tmp_fd)
        self.orig_db = database.DB_NAME
        database.DB_NAME = self.tmp_path
        database.init_db()

    def tearDown(self):
        database.DB_NAME = self.orig_db
        if os.path.exists(self.tmp_path):
            os.remove(self.tmp_path)

    def test_issue_and_return_flow(self):
        bid = add_book("Test Book", "Test Author", "ISBN-001", 2)
        mid = add_member("Rohan Verma", "rohan@example.com", "9999999999")

        txn = issue_book(bid, mid, loan_days=7)
        self.assertEqual(txn["book_title"], "Test Book")

        books = list_books("Test Book")
        self.assertEqual(books[0]["available_copies"], 1)

        res = return_book(txn["txn_id"])
        self.assertEqual(res["fine_inr"], 0.0)

        books_after = list_books("Test Book")
        self.assertEqual(books_after[0]["available_copies"], 2)


if __name__ == "__main__":
    unittest.main()
