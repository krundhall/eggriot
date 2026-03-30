import os
from dotenv import load_dotenv
import mysql.connector
from parse import parse_all, get_and_parse_items_json
load_dotenv()

TABLES = [
    """CREATE TABLE IF NOT EXISTS players (
        PlayerID int NOT NULL AUTO_INCREMENT,
        SummonerName varchar(30) DEFAULT NULL,
        Region varchar(10) DEFAULT NULL,
        RankTier varchar(30) DEFAULT NULL,
        PUUID varchar(255) NOT NULL,
        Tag varchar(10) DEFAULT NULL,
        PRIMARY KEY (PlayerID),
        UNIQUE KEY (PUUID)
    )""",

    """CREATE TABLE IF NOT EXISTS matches (
        MatchID int NOT NULL AUTO_INCREMENT,
        Duration int DEFAULT NULL,
        GameMode varchar(30) DEFAULT NULL,
        PatchVersion varchar(30) DEFAULT NULL,
        WinningTeam varchar(5) DEFAULT NULL,
        RiotMatchID varchar(50) DEFAULT NULL,
        QueueID int DEFAULT NULL,
        QueueName varchar(30) DEFAULT NULL,
        PRIMARY KEY (MatchID),
        UNIQUE KEY (RiotMatchID)
    )""",

    """CREATE TABLE IF NOT EXISTS champions (
        ChampID int NOT NULL,
        Name varchar(30) DEFAULT NULL,
        PRIMARY KEY (ChampID)
    )""",

    """CREATE TABLE IF NOT EXISTS items (
        ItemID int NOT NULL,
        Name varchar(30) DEFAULT NULL,
        GoldCost int DEFAULT NULL,
        PRIMARY KEY (ItemID)
    )""",

    """CREATE TABLE IF NOT EXISTS plays_in (
        PlayerID int NOT NULL,
        MatchID int NOT NULL,
        ChampID int NOT NULL,
        Kills int DEFAULT NULL,
        Deaths int DEFAULT NULL,
        Assists int DEFAULT NULL,
        GoldEarned int DEFAULT NULL,
        GoldSpent int DEFAULT NULL,
        VisionScore int DEFAULT NULL,
        MinionsKilled int DEFAULT NULL,
        DamageDealt int DEFAULT NULL,
        Team enum('BLUE','RED') NOT NULL,
        Level int DEFAULT NULL,
        PlayerWon tinyint(1) DEFAULT NULL,
        Role varchar(20) DEFAULT NULL,
        PRIMARY KEY (PlayerID, MatchID, ChampID),
        CONSTRAINT plays_in_fk_player FOREIGN KEY (PlayerID) REFERENCES players (PlayerID),
        CONSTRAINT plays_in_fk_match FOREIGN KEY (MatchID) REFERENCES matches (MatchID),
        CONSTRAINT plays_in_fk_champ FOREIGN KEY (ChampID) REFERENCES champions (ChampID)
    )""",

    """CREATE TABLE IF NOT EXISTS uses_item (
        PlayerID int NOT NULL,
        MatchID int NOT NULL,
        Slot tinyint NOT NULL,
        ItemID int NOT NULL,
        Timestamp int DEFAULT NULL,
        PRIMARY KEY (PlayerID, MatchID, Slot),
        CONSTRAINT uses_item_fk_player FOREIGN KEY (PlayerID) REFERENCES players (PlayerID),
        CONSTRAINT uses_item_fk_match FOREIGN KEY (MatchID) REFERENCES matches (MatchID),
        CONSTRAINT uses_item_fk_item FOREIGN KEY (ItemID) REFERENCES items (ItemID)
    )""",
]

def clean_db(conn):
    cur = conn.cursor()
    cur.execute("SET FOREIGN_KEY_CHECKS = 0")
    tables = [
        "uses_item", "plays_in",
        "items", "champions", "matches", "players"
    ]
    for table in tables:
        cur.execute(f"DROP TABLE IF EXISTS {table}")
    cur.execute("SET FOREIGN_KEY_CHECKS = 1")
    conn.commit()
    cur.close()
    print("Database wiped.")

def init_db(conn):
    cur = conn.cursor()
    for statement in TABLES:
        cur.execute(statement)
    conn.commit()
    cur.execute("DROP TRIGGER IF EXISTS t_insertQueueName")
    cur.execute("""
        CREATE TRIGGER t_insertQueueName
        BEFORE INSERT ON matches
        FOR EACH ROW
        BEGIN
            IF NEW.QueueID = 400 THEN
                SET NEW.QueueName = 'Normal SR';
            ELSEIF NEW.QueueID = 420 THEN
                SET NEW.QueueName = 'Ranked SR';
            ELSE
                SET NEW.QueueName = 'Unknown';
            END IF;
        END
    """)
    conn.commit()
    cur.execute("DROP PROCEDURE IF EXISTS GetPlayerSummary")
    cur.execute("""
        CREATE PROCEDURE GetPlayerSummary(IN p_name VARCHAR(30))
        BEGIN
            SELECT p.SummonerName, p.Tag,
                   COUNT(*) AS TotalMatches,
                   ROUND(AVG(pi.Kills), 2) AS AvgKills,
                   ROUND(AVG(pi.Deaths), 2) AS AvgDeaths,
                   ROUND(AVG(pi.Assists), 2) AS AvgAssists,
                   ROUND(AVG((pi.Kills + pi.Assists) / GREATEST(pi.Deaths, 1)), 2) AS AvgKDA,
                   ROUND(AVG(pi.PlayerWon) * 100, 2) AS WinRate
            FROM plays_in pi
            JOIN players p ON pi.PlayerID = p.PlayerID
            WHERE p.SummonerName = p_name
            GROUP BY pi.PlayerID, p.SummonerName, p.Tag;
        END
    """)
    conn.commit()
    cur.close()
    print("Tables created.")
    populate_items(conn)
    print("Database initialised.")

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database = os.getenv("DB_NAME")
    )

def insert_match(conn, parsed_match):
    cur = conn.cursor()
    cur.execute("SELECT MatchID FROM matches WHERE RiotMatchID = %s", (parsed_match['MatchID'],))
    result = cur.fetchone()
    if result:
        cur.close()
        return result[0]
    cur.execute(
    """
    INSERT INTO matches (RiotMatchID, Duration, GameMode, PatchVersion, WinningTeam, QueueID)
    VALUES (%s, %s, %s, %s, %s, %s)
    """,
    (parsed_match['MatchID'],parsed_match['Duration'], parsed_match['GameMode'],
     parsed_match['PatchVersion'], parsed_match['WinningTeam'], parsed_match['QueueID'],)
    )

    conn.commit()
    match_id = cur.lastrowid
    cur.close()
    return match_id


def insert_player(conn, parsed_players):
    cur = conn.cursor()

    cur.execute("SELECT PlayerID FROM players WHERE PUUID = %s", (parsed_players['PUUID'],))
    result = cur.fetchone()
    if result:
        cur.close()
        return result[0]
    else:
        cur.execute(
        """
        INSERT INTO players (SummonerName, Tag, PUUID)
        VALUES (%s, %s, %s)
        """,
        (parsed_players['SummonerName'],
         parsed_players['Tag'],
         parsed_players['PUUID'])
        )

        conn.commit()
        player_id = cur.lastrowid
        cur.close()
        return player_id

def insert_champions(conn, parsed_champions):
    cur = conn.cursor()

    cur.execute("SELECT ChampID FROM champions WHERE ChampID = %s", (parsed_champions['ChampID'],))
    result = cur.fetchone()
    if result:
        cur.close()
        return result[0]
    else:
        cur.execute(
        """
        INSERT INTO champions (ChampID, Name)
        VALUES (%s, %s)
        """,
        (parsed_champions['ChampID'], parsed_champions['Name'])
        )

        conn.commit()
        cur.close()
        return parsed_champions['ChampID']


def insert_participants(conn, parsed_participants, match_id, player_id):
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM plays_in WHERE MatchID = %s AND PlayerID = %s AND ChampID = %s",
                (match_id, player_id, parsed_participants['ChampID'],))
    if cur.fetchone():
        cur.close()
        return

    cur.execute(
    """
    INSERT INTO plays_in (
        MatchID, PlayerID, ChampID, Kills,
        Deaths, Assists, GoldEarned, GoldSpent,
        VisionScore, MinionsKilled, DamageDealt,
        Team, Level, PlayerWon, Role)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """,
    (match_id, player_id, parsed_participants['ChampID'], parsed_participants['Kills'],
     parsed_participants['Deaths'], parsed_participants['Assists'], parsed_participants['GoldEarned'],
     parsed_participants['GoldSpent'], parsed_participants['VisionScore'], parsed_participants['MinionsKilled'],
     parsed_participants['DamageDealt'], parsed_participants['Team'], parsed_participants['Level'],
     parsed_participants['PlayerWon'], parsed_participants['Role'],)
    )

    conn.commit()
    cur.close()

def insert_items(conn, parsed_items, player_id, match_id):
    cur = conn.cursor()

    cur.execute(
    """
    INSERT IGNORE INTO uses_item (PlayerID, MatchID, Slot, ItemID)
    VALUES (%s, %s, %s, %s)
    """,
    (player_id, match_id, parsed_items['Slot'], parsed_items['ItemID'],)
    )

    conn.commit()
    cur.close()

def match_exists(conn, riot_match_id):
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM matches WHERE RiotMatchID = %s", (riot_match_id,))
    result = cur.fetchone()
    cur.close()
    return result is not None

def populate_items(conn):
    cur = conn.cursor()
    items = get_and_parse_items_json()

    for item in items:
        cur.execute(
        """
        INSERT IGNORE INTO items (ItemID, Name, GoldCost)
        VALUES (%s, %s, %s)
        """,
        (item['ItemID'], item['Name'], item['GoldCost'])
        )

    conn.commit()
    cur.close()


def store_match(conn, match_data):
    parsed_data = parse_all(match_data)
    if parsed_data is None:
        return False
    print(f"\nStoring match: {parsed_data['match']['MatchID']}...")

    match_id = insert_match(conn, parsed_data['match'])
    for i in range(10):
        player_id = insert_player(conn, parsed_data['players'][i])
        insert_champions(conn, parsed_data['champions'][i])
        insert_participants(conn, parsed_data['participants'][i], match_id, player_id)

        puuid = parsed_data['participants'][i]['puuid']
        for item in parsed_data['items']:
            if item['puuid'] == puuid:
                insert_items(conn, item, player_id, match_id)
    return True

def query_player_kda_averages(conn):
    cur = conn.cursor()
    cur.execute(
        """
        SELECT p.SummonerName, p.Tag,
               ROUND(AVG(pi.Kills), 2) AS AvgKills,
               ROUND(AVG(pi.Deaths), 2) AS AvgDeaths,
               ROUND(AVG(pi.Assists), 2) AS AvgAssists,
               ROUND(AVG((pi.Kills + pi.Assists) / GREATEST(pi.Deaths, 1)), 2) AS AvgKDA
        FROM plays_in pi
        JOIN players p ON pi.PlayerID = p.PlayerID
        WHERE p.SummonerName LIKE '% Egg'
        GROUP BY pi.PlayerID, p.SummonerName, p.Tag
        ORDER BY AvgKDA DESC
        LIMIT 10
        """
    )
    result = cur.fetchall()
    cur.close()
    return result


def query_player_summary(conn, summoner_name):
    cur = conn.cursor()
    cur.callproc("GetPlayerSummary", [summoner_name])
    result = []
    for res in cur.stored_results():
        result = res.fetchall()
    cur.close()
    return result


def query_longest_matches(conn):
    cur = conn.cursor()
    cur.execute(
        """
        SELECT p.SummonerName, p.Tag, m.RiotMatchID,
               ROUND(m.Duration / 60, 1) AS Duration_minutes
        FROM plays_in pi
        JOIN players p ON pi.PlayerID = p.PlayerID
        JOIN matches m ON pi.MatchID = m.MatchID
        WHERE p.SummonerName LIKE '% Egg'
        ORDER BY m.Duration DESC
        LIMIT 5
        """
    )
    result = cur.fetchall()
    cur.close()
    return result


def query_items_highest_winrate(conn):
    cur = conn.cursor()
    cur.execute(
        """
        SELECT i.Name, ROUND(AVG(PlayerWon) * 100, 2) AS WR
        FROM items i
        JOIN uses_item as ui ON i.itemID = ui.ItemID
        JOIN plays_in pi ON pi.PlayerID = ui.PlayerID AND pi.MatchID = ui.MatchID
        GROUP BY i.Name
        HAVING COUNT(*) >= 10
        ORDER BY WR DESC
        LIMIT 10
        """
    )
    result = cur.fetchall()
    cur.close()
    return result



def query_most_played_champions(conn):
    cur = conn.cursor()
    cur.execute(
        """
        SELECT c.Name, COUNT(*) AS TimesPlayed
        FROM plays_in pi
        JOIN champions c ON pi.ChampID = c.ChampID
        GROUP BY pi.ChampID, c.Name
        ORDER BY TimesPlayed DESC
        LIMIT 10
        """
    )
    result = cur.fetchall()
    cur.close()
    return result


def query_most_purchased_items(conn):
    cur = conn.cursor()
    cur.execute(
        """
        SELECT i.Name, COUNT(*) AS TimesBought
        FROM uses_item ui
        JOIN items i ON ui.ItemID = i.ItemID
        WHERE ui.Slot != 6
        GROUP BY ui.ItemID, i.Name
        ORDER BY TimesBought DESC
        LIMIT 10
        """
    )
    result = cur.fetchall()
    cur.close()
    return result


if __name__ == "__main__":
    conn = get_connection()
    print("Connected:", conn.is_connected())
    conn.close()
