import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
from tqdm import tqdm

try:
    from utils.util import _get_game_suffix
except:
    from opponent_adjusted_nba_scraper.utils.util import _get_game_suffix

def _get_dataframe(url, id):
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

def _add_possessions(name, logs, team_dict, season_type):
    total_poss = 0
    logs["DATE"] = pd.to_datetime(logs["DATE"])
    logs["GAME_SUFFIX"] = ""
    for i in tqdm(range(1, len(logs) + 1), desc='Loading player possessions...', ncols=75):
        logs.loc[i, "GAME_SUFFIX"] = _get_game_suffix(logs.loc[i, "DATE"], logs.loc[i, "TEAM"], logs.loc[i, "MATCHUP"])
        suffix = logs.loc[i, "GAME_SUFFIX"]
        url = f'https://www.basketball-reference.com{suffix}'
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            exit(f"{r.status_code} Error")
        r = r.text.replace("<!--","").replace("-->","")
        soup = BeautifulSoup(r, features="lxml")
        pace = soup.find("td", attrs={"data-stat":"pace"}).text
        total_poss += (logs.loc[i, "MIN"] / 48) * float(pace)
        time.sleep(21)
    logs = logs.drop(columns=["GAME_SUFFIX"])
    return total_poss