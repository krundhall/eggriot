import os
import time
import requests
import json

API_KEY = os.getenv("RIOT_API_KEY")
BASE_URL = "https://europe.api.riotgames.com"

def _get(url):
    headers = {"X-Riot-Token": API_KEY}
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 1))
            print(f"Rate limited. Waiting {retry_after}s...")
            time.sleep(retry_after)
            continue
        response.raise_for_status()
        return response

def get_puuid_by_riot_id(name: str, tag: str):
    """Gets PUUID using Riot ID (Name + Tag)
    https://developer.riotgames.com/docs/lol#:~:text=%28ACCOUNT,tagLine%29%2E
    """
    url = f"{BASE_URL}/riot/account/v1/accounts/by-riot-id/{name}/{tag}"
    try:
        return _get(url).json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def get_latest_match(puuid):
    url = f"{BASE_URL}/lol/match/v5/matches/by-puuid/{puuid}/ids?queue=420&count=1"
    try:
        match_ids = _get(url).json()
        return match_ids[0] if match_ids else None
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

SEASON_2026_START = 1767744000  # Jan 7 2026 00:00 UTC

def iter_ranked_match_ids(puuid):
    """Lazily yield ranked (queue 420) match IDs from season 2026 onwards, newest first."""
    start = 0
    while True:
        url = (
            f"{BASE_URL}/lol/match/v5/matches/by-puuid/{puuid}/ids"
            f"?queue=420&start={start}&count=100"
        )
        try:
            batch = _get(url).json()
            yield from batch
            if len(batch) < 100:
                break
            start += 100
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            break

def get_match_details(match_id):
    url = f"{BASE_URL}/lol/match/v5/matches/{match_id}"
    try:
        return _get(url).json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def get_items_json():
    url = "https://ddragon.leagueoflegends.com/cdn/16.4.1/data/en_US/item.json"

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def get_latest_400_game(name, tag, path="../normalgame.json"):
    """Test to fetch adn write a normal game"""

    # get puuid
    riot_account = get_puuid_by_riot_id(name, tag)
    if not riot_account or "puuid" not in riot_account:
        print("Could not fetch PUUID for given account")
        return

    puuid = riot_account["puuid"]

    # fetch latest normal
    url = f"{BASE_URL}/lol/match/v5/matches/by-puuid/{puuid}/ids?queue=400&start=0&count=1"

    try:
        match_ids = _get(url).json()
        if not match_ids:
            print(f"No normal draft games for for {name}#{tag}")
            return
        match_id = match_ids[0]
    except Exception as e:
        print(f"Failed to fetch match IDs: {e}")
        return

    # fetch match details
    match_details = get_match_details(match_id)
    if not match_details:
        print(f"Could not retrieve match details for match ID: {match_id}")
        return


    # write to json
    try:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(match_details, file, indent=2)
        print(f"Latest normal draft game details written to {path}")
        print(match_details["info"].keys())
    except Exception as e:
        print(f"Failed to write JSON: {e}")

def iter_normal_match_ids(puuid):
    """Lazily yield ranked (queue 400) match IDs from current year and onwards, newest first."""
    import time, datetime
    now = datetime.datetime.now()
    year_start = int(time.mktime(datetime.datetime(now.year, 1, 1).timetuple()))
    start = 0
    batch_size = 100
    consecutive_old = 0

    while True:
        url = (
            f"{BASE_URL}/lol/match/v5/matches/by-puuid/{puuid}/ids"
            f"?queue=400&start={start}&count={batch_size}"
        )
        try:
            batch = _get(url).json()
            if not batch:
                break
            for match_id in batch:
                match_data = get_match_details(match_id)
                if not match_data or "info" not in match_data:
                    continue

                game_creation = match_data["info"].get("gameCreation", 0) // 1000
                if game_creation < year_start:
                    consecutive_old += 1
                    if consecutive_old >= 5:
                        print(" Reached pre-year matches, stopping.")
                        return
                    continue
                consecutive_old = 0
                yield match_id, match_data
            if len(batch) < batch_size:
                break
            start += batch_size
        except Exception as e:
            print(f"Error during fetch: {e}")
            break
