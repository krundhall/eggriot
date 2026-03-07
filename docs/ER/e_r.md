# plays_in (3-way relationship: Player, Match, Champion)
A player can participate in many matches playing many different champions.
A match has many players, each playing a champion.
A player plays exactly one champion per match.
Each unique combination of (Player, Match, Champion) represents one participation.
Player = N
Match = N
Champion = 1


# uses_item (3-way relationship: Player, Match, Item)
A player can use many items across many matches.
A match sees many items used by many players.
An item can be used by many players across many matches.
Each unique combination of (Player, Match, Slot) identifies one item entry,
allowing a player to hold multiple of the same item in different slots.
Player = N
Match = N
Item = N
