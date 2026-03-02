from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from db import get_connection
from menu import *

def main():
    conn = get_connection()

    while True:
        print("\n=== Noob ===")
        print("1. Add account")
        print("2. List accounts")
        print("3. Get latest match")
        print("4. Fetch all ranked matches (this season)")
        print("5. Initialise database")
        print("6. Wipe database")
        print("q. Exit")

        choice = input(">>> ")

        if choice == "1":
            menu_add_account()
        elif choice == "2":
            menu_list_accounts()
        elif choice == "3":
            menu_store_match(conn)
        elif choice == "4":
            menu_fetch_all_ranked(conn)
        elif choice == "5":
            menu_init_db(conn)
        elif choice == "6":
            menu_clean_db(conn)
        elif choice == "q":
            break
        else:
            print("Invalid option")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
