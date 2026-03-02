-- --------------------------------------------------------
-- New schema: weak entities replaced with 3-way relations
-- --------------------------------------------------------

CREATE TABLE players (
  PlayerID int NOT NULL AUTO_INCREMENT,
  SummonerName varchar(30) DEFAULT NULL,
  Region varchar(10) DEFAULT NULL,
  RankTier varchar(30) DEFAULT NULL,
  PUUID varchar(255) NOT NULL,
  Tag varchar(10) DEFAULT NULL,
  PRIMARY KEY (PlayerID),
  UNIQUE KEY (PUUID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

CREATE TABLE matches (
  MatchID int NOT NULL AUTO_INCREMENT,
  Duration int DEFAULT NULL,
  GameMode varchar(30) DEFAULT NULL,
  PatchVersion varchar(30) DEFAULT NULL,
  WinningTeam varchar(5) DEFAULT NULL,
  RiotMatchID varchar(50) DEFAULT NULL,
  PRIMARY KEY (MatchID),
  UNIQUE KEY (RiotMatchID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

CREATE TABLE champions (
  ChampID int NOT NULL,
  Name varchar(30) DEFAULT NULL,
  PRIMARY KEY (ChampID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

CREATE TABLE items (
  ItemID int NOT NULL,
  Name varchar(30) DEFAULT NULL,
  GoldCost int DEFAULT NULL,
  PRIMARY KEY (ItemID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------
-- 3-way relation: Player x Match x Champion
-- Replaces weak entity: participantstats
-- --------------------------------------------------------

CREATE TABLE plays_in (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------
-- 3-way relation: Player x Match x Item
-- Replaces weak entity: participantitems
-- --------------------------------------------------------

CREATE TABLE uses_item (
  PlayerID int NOT NULL,
  MatchID int NOT NULL,
  Slot tinyint NOT NULL,
  ItemID int NOT NULL,
  Timestamp int DEFAULT NULL,
  PRIMARY KEY (PlayerID, MatchID, Slot),
  CONSTRAINT uses_item_fk_player FOREIGN KEY (PlayerID) REFERENCES players (PlayerID),
  CONSTRAINT uses_item_fk_match FOREIGN KEY (MatchID) REFERENCES matches (MatchID),
  CONSTRAINT uses_item_fk_item FOREIGN KEY (ItemID) REFERENCES items (ItemID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
