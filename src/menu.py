import datetime
from riot_api import iter_ranked_match_ids, iter_normal_match_ids, get_match_details, SEASON_2026_START
from accounts import load_accounts, list_accounts, add_account
from db import store_match, match_exists, init_db, clean_db, query_items_highest_winrate
import os


def menu_add_account():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n=== ADDING ACCOUNT ===")
    game_name = input("Enter name: ")
    tag_line = input("Enter tag: ")
    add_account(game_name, tag_line)
    input("Press Enter to continue...")

def menu_list_accounts():
    os.system('cls' if os.name == 'nt' else 'clear')
    list_accounts()
    input("Press Enter to continue...")



def menu_clean_db(conn):
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n=== WIPING DATABASE ====")
    confirm = input("This will wipe all tables. Are you sure? (yes/n): ").strip().lower()
    if confirm == "yes":
        clean_db(conn)
    else:
        print("Cancelled.")

    input("Press Enter to continue...")



def menu_init_db(conn):
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=== INITIALIZING DATABSE ===")
    init_db(conn)
    input("Press Enter to continue...")




def _select_accounts():
    accounts = load_accounts()
    if not accounts:
        print("No accounts tracked.")
        return None
    list_accounts()
    choice = input("Fetch for which account? (number or 'all'): ").strip().lower()
    if choice == "all":
        return accounts
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(accounts):
            return [accounts[idx]]
    except ValueError:
        pass
    print("Invalid choice.")
    return None

def _fetch_matches(conn, label, iterator_fn, since):
    accounts = _select_accounts()
    if not accounts:
        return
    for account in accounts:
        name, tag, puuid = account['gameName'], account['tagLine'], account['puuid']
        print(f"\nFetching {label} for {name}#{tag}...")
        new_count = 0
        for match_id in iterator_fn(puuid):
            if match_exists(conn, match_id):
                continue
            match_data = get_match_details(match_id)
            if not match_data or "info" not in match_data:
                continue
            if match_data["info"].get("gameCreation", 0) / 1000 < since:
                print("  Reached pre-cutoff match, stopping.")
                break
            try:
                if store_match(conn, match_data):
                    new_count += 1
                    print(f"  [{new_count} stored]")
            except Exception as e:
                print(f"  [ERROR] {match_id}: {e}")
        print(f"Done. {new_count} new {label} stored for {name}#{tag}.")

def menu_fetch_all_ranked(conn):
    _fetch_matches(conn, "ranked matches", iter_ranked_match_ids, since=SEASON_2026_START)

def menu_fetch_all_normal_games(conn):
    year_start = int(datetime.datetime(datetime.datetime.now().year, 1, 1).timestamp())
    _fetch_matches(conn, "normal games", iter_normal_match_ids, since=year_start)

def menu_query_items_highest_winrate(conn):
    os.system('cls' if os.name == 'nt' else 'clear')
    result = query_items_highest_winrate(conn)
    print("\n=== Items with the highest winrate ===")
    for i, (item, wr) in enumerate(result):
        print(f"{i+1}. {item}: {wr}%")
    print("======================================")
    input("\nPress Enter to continue...")
