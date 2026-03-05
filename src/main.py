from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from db import get_connection
from menu import *
import os

def main():
    conn = get_connection()

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n=== Eggriot ===")
        print("1. Add account")
        print("2. List accounts")
        print("3. Fetch all ranked matches (this season)")
        print("4. Fetch all normal matches (this year)")
        print("5. Query what items has the highest winrate")
        print("6.")
        print("7.")
        print("8.")
        print("9.")
        print("0.")
        print("q. Exit\n")
        print("init). Initialise database")
        print("wipe). Wipe database")


        choice = input(">>> ")

        if choice == "1":
            menu_add_account()
        elif choice == "2":
            menu_list_accounts()
        elif choice == "3":
            menu_fetch_all_ranked(conn)
        elif choice == "4":
            menu_fetch_all_normal_games(conn)
        elif choice == "5":
            menu_query_items_highest_winrate(conn)
        elif choice == "init":
            menu_init_db(conn)
        elif choice == "wipe":
            menu_clean_db(conn)
        elif choice == "q":
            break
        else:
            print("Invalid option")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
