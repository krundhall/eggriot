import os
import time
import requests

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
