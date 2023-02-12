import requests
import pandas as pd
from bs4 import BeautifulSoup
from utils.util import get_game_suffix

def get_dataframe(url, id):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        exit(f"{r.status_code} Error")
    soup = BeautifulSoup(r.text, features="lxml")
    table = soup.find("table", attrs={"id": id})
    header = []
    rows = []
    for i, row in enumerate(table.find_all('tr')):
        if i == 0:
            header = [el.text.strip() for el in row.find_all('th')]
        else:
            rows.append([el.text.strip() for el in row.find_all('td')])
    if id == "advanced-team":
        header = ["Rk", "Team", "Age", "W", "L", "PW", "PL", "MOV", "SOS", "SRS", "ORtg", "DRtg", "NRtg", "Pace", "FTr", "3PAr", "TS%", 
        " ", "eFG%", "TOV%", "ORB%", "FT/FGA", " ", "eFG%", "TOV%", "DRB%", "FT/FGA", " ", "Arena", "Attend.", "Attend./G"]
        rows = rows[1:]
    return pd.DataFrame(rows, columns=header[1:])

def add_possessions(name, logs, team_dict, season_type="Playoffs"):
    total_poss = 0
    logs["DATE"] = pd.to_datetime(logs["DATE"])
    logs["POSSESSIONS"] = ""
    for i in range(1, len(logs) + 1):
        logs.loc[i, "GAME_SUFFIX"] = get_game_suffix(logs.loc[i, "DATE"], logs.loc[i, "TEAM"], logs.loc[i, "MATCHUP"])
        suffix = logs.loc[i, "GAME_SUFFIX"]
        url = f'https://www.basketball-reference.com{suffix}'
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            exit(f"{r.status_code} Error")
        r = r.text.replace("<!--","").replace("-->","")
        soup = BeautifulSoup(r, features="lxml")
        pace = soup.find("td", attrs={"data-stat":"pace"}).text
        logs.loc[i, "POSSESSIONS"] = (logs.loc[i, "MIN"] / 48) * float(pace)
    logs["POSSESSIONS"] = logs["POSSESSIONS"].astype("float64")
    logs["PTS_PER_100"] = (logs["PTS"] * 100) / logs["POSSESSIONS"]
    logs = logs.drop(columns=["GAME_SUFFIX"])
    return total_poss