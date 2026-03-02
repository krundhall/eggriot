from riot_api import get_items_json

def parse_match(match_data):
    match_id = match_data['metadata']['matchId']
    info = match_data['info']
    if info.get('endOfGameResult') != 'GameComplete':
        return None
    if info['gameDuration'] < 210:
        return None
    if 'gameEndTimestamp' in info:
        duration = info['gameDuration']  # seconds (patch 11.20+)
    else:
        duration = info['gameDuration'] // 1000  # milliseconds, convert to seconds
    gamemode = info['gameMode']
    patchversion = info['gameVersion']
    winning_team = 'BLUE' if info['teams'][0]['win'] else 'RED'

    return {
        'MatchID': match_id,
        'Duration': duration,
        'GameMode': gamemode,
        'PatchVersion': patchversion,
        'WinningTeam': winning_team,
        'QueueID': info.get('queueId')
    }

def parse_players(match_data):
    players = []
    for participant in match_data['info']['participants']:
        players.append({
            'SummonerName': participant['riotIdGameName'],
            'Tag': participant['riotIdTagline'],
            'PUUID': participant['puuid']
        })

    return players


def parse_champions(match_data):
    champions = []
    for participant in match_data['info']['participants']:
        champions.append({
            'ChampID': participant['championId'],
            'Name': participant['championName']
        })

    return champions

def parse_participants(match_data):
    # PlayerID, MatchID, ChampID,
    # Kills, Deaths, Assists, GoldEarned,
    # GoldSpent, VisionScore, MinionsKilled,
    # DamageDealt, Team, Level, PlayerWon, Role
    participants = []

    for participant in match_data['info']['participants']:
        participants.append({
            'Kills': participant['kills'],
            'Deaths': participant['deaths'],
            'Assists': participant['assists'],
            'GoldEarned': participant['goldEarned'],
            'GoldSpent': participant['goldSpent'],
            'VisionScore': participant['visionScore'],
            'MinionsKilled': participant['totalMinionsKilled'],
            'DamageDealt': participant['totalDamageDealtToChampions'],
            'Team': 'BLUE' if participant['teamId'] == 100 else 'RED',
            'Level': participant['champLevel'],
            'PlayerWon': 1 if participant['win'] == True else 0,
            'Role': participant['teamPosition'],
            'puuid': participant['puuid'],
            'ChampID': participant['championId']
        })

    return participants


def parse_items(match_data):
    # ItemID, Name,
    items = []

    for participant in match_data['info']['participants']:
        for i in range(7): # item0 through item6
            item_id = participant[f'item{i}']
            if item_id != 0:
                items.append({
                    'puuid': participant['puuid'],
                    'Slot': i,
                    'ItemID': item_id
                })

    return items


def parse_all(match_data):
    match = parse_match(match_data)
    if match is None:
        return None
    return {
        'match': match,
        'players': parse_players(match_data),
        'champions': parse_champions(match_data),
        'participants': parse_participants(match_data),
        'items': parse_items(match_data)
    }

def get_and_parse_items_json():
    items_data = get_items_json()
    if not items_data:
        print("Failed to fetch items data")
        return []

    items = []
    for item_id, item in items_data['data'].items():
        items.append({
            'ItemID': int(item_id),
            'Name': item['name'],
            'GoldCost': item['gold']['total']
        })

    return items
