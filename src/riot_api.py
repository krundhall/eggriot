import os
import time
import datetime
import requests

API_KEY = os.getenv("RIOT_API_KEY")
BASE_URL = "https://europe.api.riotgames.com"
SEASON_2026_START = 1767744000  # Jan 7 2026 00:00 UTC

def _get(url):
    headers = {"X-Riot-Token": API_KEY}
    while True:
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 429:
                print(f"Rate limited. Waiting {int(response.headers.get('Retry-After', 1))}s...")
                time.sleep(int(response.headers.get("Retry-After", 1)))
                continue
            response.raise_for_status()
            return response
        except Exception as e:
            print(f"Error: {e}")
            return None

def get_puuid_by_riot_id(name: str, tag: str):
    r = _get(f"{BASE_URL}/riot/account/v1/accounts/by-riot-id/{name}/{tag}")
    return r.json() if r else None

def iter_ranked_match_ids(puuid):
    start = 0
    while True:
        r = _get(f"{BASE_URL}/lol/match/v5/matches/by-puuid/{puuid}/ids?queue=420&start={start}&count=100&startTime={SEASON_2026_START}")
        if not r:
            break
        batch = r.json()
        if not batch:
            break
        yield from batch
        if len(batch) < 100:
            break
        start += 100

def get_match_details(match_id):
    r = _get(f"{BASE_URL}/lol/match/v5/matches/{match_id}")
    return r.json() if r else None

def get_items_json():
    try:
        r = requests.get("https://ddragon.leagueoflegends.com/cdn/16.4.1/data/en_US/item.json")
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def iter_normal_match_ids(puuid):
    year_start = int(datetime.datetime(datetime.datetime.now().year, 1, 1).timestamp())
    start = 0

    while True:
        r = _get(f"{BASE_URL}/lol/match/v5/matches/by-puuid/{puuid}/ids?queue=400&start={start}&count=100&startTime={year_start}")
        if not r:
            break
        batch = r.json()
        if not batch:
            break
        yield from batch
        if len(batch) < 100:
            break
        start += 100
