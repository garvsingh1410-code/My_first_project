from database import init_db
from library_service import (
    add_book,
    add_member,
    issue_book,
    list_books,
    list_members,
    list_transactions,
    return_book,
)


def print_menu():
    print("\n=== Library Management System ===")
    print("1. Add Book")
    print("2. View / Search Books")
    print("3. Register Member")
    print("4. View Members")
    print("5. Issue Book")
    print("6. Return Book")
    print("7. View Transactions")
    print("0. Exit")


def main():
    init_db()
    while True:
        print_menu()
        choice = input("Enter choice: ").strip()

        try:
            if choice == "1":
                title = input("Book title: ")
                author = input("Author: ")
                isbn = input("ISBN (optional): ")
                copies = int(input("Number of copies: ") or "1")
                bid = add_book(title, author, isbn, copies)
                print(f"Book added successfully with ID: {bid}")

            elif choice == "2":
                q = input("Search keyword (leave blank for all): ")
                books = list_books(q)
                if not books:
                    print("No books found.")
                else:
                    for b in books:
                        print(
                            f"[{b['book_id']}] {b['title']} by {b['author']} | "
                            f"Available: {b['available_copies']}/{b['total_copies']} | "
                            f"ISBN: {b['isbn'] or 'N/A'}"
                        )

            elif choice == "3":
                name = input("Member name: ")
                email = input("Email (optional): ")
                phone = input("Phone (optional): ")
                mid = add_member(name, email, phone)
                print(f"Member registered with ID: {mid}")

            elif choice == "4":
                members = list_members()
                if not members:
                    print("No members registered.")
                else:
                    for m in members:
                        print(
                            f"[{m['member_id']}] {m['name']} | "
                            f"Email: {m['email'] or 'N/A'} | Joined: {m['joined_on']}"
                        )

            elif choice == "5":
                bid = int(input("Enter Book ID: "))
                mid = int(input("Enter Member ID: "))
                days = int(input("Loan days (default 14): ") or "14")
                info = issue_book(bid, mid, days)
                print(
                    f"Issued '{info['book_title']}' to {info['member_name']} "
                    f"(Txn ID: {info['txn_id']}, Due: {info['due_date']})"
                )

            elif choice == "6":
                tid = int(input("Enter Transaction ID to return: "))
                res = return_book(tid)
                print(
                    f"Returned on {res['return_date']} | "
                    f"Overdue days: {res['overdue_days']} | Fine: ₹{res['fine_inr']:.2f}"
                )

            elif choice == "7":
                active_only = input("Show only active issues? (y/N): ").strip().lower() == "y"
                txns = list_transactions(only_active=active_only)
                if not txns:
                    print("No transactions found.")
                else:
                    for t in txns:
                        print(
                            f"[Txn {t['txn_id']}] {t['book_title']} -> {t['member_name']} | "
                            f"Status: {t['status']} | Due: {t['due_date']} | "
                            f"Fine: ₹{t['fine_amount']:.2f}"
                        )

            elif choice == "0":
                print("Exiting. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

        except ValueError as ve:
            print(f"Error: {ve}")
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
