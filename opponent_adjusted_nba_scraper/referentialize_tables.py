import pandas as pd

import numpy as np

def referentialize():
    games = pd.read_csv("player_logs.csv")
    names = pd.read_csv("names.csv")
    defenses = pd.read_csv("defense_rds.csv")
    paces = pd.read_csv("game_pace.csv")
    dict2 = dict(zip(names.Player, names.Id))
    games["Player_Id"] = games["NAME"].map(dict2)
    games = games.drop(columns=["NAME"])
    games = games.iloc[:, [0, 25] + [i for i in range(1, 25)]]
    dict3 = dict(zip(defenses.Team_Id, defenses.Id))
    games = games.astype({"SEASON": "string"})
    games["Opponent_Id"] = games["SEASON"] + games["MATCHUP"]
    games["Opponent_Id"] = games["Opponent_Id"].map(dict3)
    games = games.iloc[:, [0, 1, 26] + [i for i in range(2, 26)]]
    dict4 = dict(zip(paces.Date + paces.Home_Team + paces.Away_Team, paces.Id))
    dict5 = dict(zip(paces.Date + paces.Away_Team + paces.Home_Team, paces.Id))
    dict4.update(dict5)
    games["Pace_Id"] = games["DATE"] + games["TEAM"] + games["MATCHUP"]
    games["Pace_Id"] = games["Pace_Id"].map(dict4)
    games = games.iloc[:, [0, 1, 2, 27] + [i for i in range(3, 27)]]
    games.index += 1
    games.to_csv("games_rds.csv")
