from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from db import get_connection
from menu import *
import os

# code for nice stuff!

def main():
    conn = get_connection()

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n=== Eggriot ===")
        print("1.  Add account")
        print("2.  List accounts")
        print("3.  Fetch all ranked matches (this season)")
        print("4.  Fetch all normal matches (this year)")
        print("5.  Query: 10 Highest Item Winrates")
        print("6.  Query: KDA Averages")
        print("7.  Query: Longest 5 Matches")
        print("8.  Query: Specific Player Summary")
        print("9.  Query: Most Purchased Items")
        print("10. Query: Most Played Champions")
        print("q.  Exit\n")
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
        elif choice == "6":
            menu_query_player_kda_averages(conn)
        elif choice == "7":
            menu_query_longest_matches(conn)
        elif choice == "8":
            menu_query_player_summary(conn)
        elif choice == "9":
            menu_query_most_purchased_items(conn)
        elif choice == "10":
            menu_query_most_played_champions(conn)
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
