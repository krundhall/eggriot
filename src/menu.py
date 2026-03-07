import datetime
from riot_api import iter_ranked_match_ids, iter_normal_match_ids, get_match_details, SEASON_2026_START
from accounts import load_accounts, list_accounts, add_account
from db import store_match, match_exists, init_db, clean_db, query_items_highest_winrate, query_player_kda_averages, query_longest_matches, query_player_summary
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
    input("Press Enter to continue...")

def menu_fetch_all_ranked(conn):
    _fetch_matches(conn, "ranked matches", iter_ranked_match_ids, since=SEASON_2026_START)

def menu_fetch_all_normal_games(conn):
    year_start = int(datetime.datetime(datetime.datetime.now().year, 1, 1).timestamp())
    _fetch_matches(conn, "normal games", iter_normal_match_ids, since=year_start)

def menu_query_player_kda_averages(conn):
    os.system('cls' if os.name == 'nt' else 'clear')
    result = query_player_kda_averages(conn)
    print("\n=== Player KDA Averages ===")
    print(f"{'#':<3} {'Player':<25} {'Kills':>6} {'Deaths':>7} {'Assists':>8} {'KDA':>6}")
    print("-" * 56)
    for i, (name, tag, kills, deaths, assists, kda) in enumerate(result, 1):
        player = f"{name}#{tag}"
        print(f"{i:<3} {player:<25} {kills:>6} {deaths:>7} {assists:>8} {kda:>6}")
    print("=" * 56)
    input("\nPress Enter to continue...")


def menu_query_player_summary(conn):
    os.system('cls' if os.name == 'nt' else 'clear')
    name = input("Enter summoner name: ").strip()
    result = query_player_summary(conn, name)
    if not result:
        print(f"No data found for '{name}'.")
        input("\nPress Enter to continue...")
        return
    print(f"\n=== Player Summary: {name} ===")
    print(f"{'Player':<25} {'Matches':>8} {'Kills':>6} {'Deaths':>7} {'Assists':>8} {'KDA':>6} {'WR':>6}")
    print("-" * 65)
    for summoner, tag, matches, kills, deaths, assists, kda, wr in result:
        player = f"{summoner}#{tag}"
        print(f"{player:<25} {matches:>8} {kills:>6} {deaths:>7} {assists:>8} {kda:>6} {wr:>5}%")
    print("=" * 65)
    input("\nPress Enter to continue...")


def menu_query_longest_matches(conn):
    os.system('cls' if os.name == 'nt' else 'clear')
    result = query_longest_matches(conn)
    print("\n=== Top 5 Longest Matches ===")
    print(f"{'#':<3} {'Player':<25} {'Duration':>10}")
    print("-" * 40)
    for i, (name, tag, match_id, duration) in enumerate(result, 1):
        player = f"{name}#{tag}"
        print(f"{i:<3} {player:<25} {duration:>8} min")
    print("=" * 40)
    input("\nPress Enter to continue...")


def menu_query_items_highest_winrate(conn):
    os.system('cls' if os.name == 'nt' else 'clear')
    result = query_items_highest_winrate(conn)
    print("\n=== Items with the highest winrate ===")
    for i, (item, wr) in enumerate(result):
        print(f"{i+1}. {item}: {wr}%")
    print("======================================")
    input("\nPress Enter to continue...")
