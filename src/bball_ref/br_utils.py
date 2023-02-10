import requests
import pandas as pd
from bs4 import BeautifulSoup

def get_dataframe(url, id):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        exit(f"{r.status_code} Error")
    soup = BeautifulSoup(r.text, features="lxml")
    table = soup.find("table", attrs={"id": id})
    header = []
    rows = []
    print(table == None)
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