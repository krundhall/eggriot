import time
from riot_api import *
from accounts import *
from db import store_match, populate_items, match_exists, init_db, clean_db


def fetch_latest_match_data():
    list_accounts()
    game_name = input("Enter name: ")
    tag_line = input("Enter tag: ")

    puuid = get_puuid_by_riot_id(game_name, tag_line)['puuid']
    if not puuid:
        return None

    match_id = get_latest_match(puuid)
    if not match_id:
        print("No match found!")
        return None

    print(f"Latest match: {match_id}\n")
    return get_match_details(match_id)


def menu_add_account():
    game_name = input("Enter name: ")
    tag_line = input("Enter tag: ")
    add_account(game_name, tag_line)


def menu_list_accounts():
    list_accounts()


def menu_store_match(conn):
    match_data = fetch_latest_match_data()
    if not match_data:
        return

    print("\nThe match has been fetched.")
    print("Would you like to store the match in the database?")
    print("1) YES")
    print("q) NO")
    usr_choice = input(">>> ").strip().lower()

    if usr_choice == "1":
        try:
            store_match(conn, match_data)
        except Exception as e:
            print(f"[ERROR]: {e}")
    elif usr_choice == "q":
        print("Ok!")
    else:
        print("Faulty input")


def menu_clean_db(conn):
    confirm = input("This will wipe all tables. Are you sure? (yes/n): ").strip().lower()
    if confirm == "yes":
        clean_db(conn)
    else:
        print("Cancelled.")


def menu_init_db(conn):
    init_db(conn)


def menu_populate_items(conn):
    populate_items(conn)


def menu_fetch_all_ranked(conn):
    accounts = load_accounts()
    if not accounts:
        print("No accounts tracked.")
        return

    for account in accounts:
        name = account['gameName']
        tag = account['tagLine']
        puuid = account['puuid']

        print(f"\nFetching ranked matches for {name}#{tag}...")

        new_count = 0
        consecutive_old = 0
        start_time = time.time()
        for i, match_id in enumerate(iter_ranked_match_ids(puuid)):
            if match_exists(conn, match_id):
                continue
            match_data = get_match_details(match_id)
            if not match_data:
                continue
            game_creation = match_data['info']['gameCreation'] / 1000
            if game_creation < SEASON_2026_START:
                consecutive_old += 1
                if consecutive_old >= 5:
                    print(f"  Reached pre-season matches, stopping.")
                    break
                continue
            consecutive_old = 0
            try:
                if store_match(conn, match_data):
                    new_count += 1
                    elapsed = time.time() - start_time
                    rate = new_count / (elapsed / 60)
                    print(f"  [{new_count} stored | {rate:.1f}/min | {int(elapsed // 60)}m {int(elapsed % 60)}s elapsed] {match_id}")
            except Exception as e:
                print(f"  [ERROR] {match_id}: {e}")

        print(f"Done. {new_count} new matches stored for {name}#{tag}.")
