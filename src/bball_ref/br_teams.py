import requests
import pandas as pd
import numpy as np
from utils.constants import TEAM_TO_TEAM_ABBR

def teams_within_drtg(min_drtg, max_drtg, first_year, last_year, season_type='Playoffs'):
    curr = first_year
    dfs = []
    while curr <= last_year:
        if season_type == "Regular Season":
            url = f'https://www.basketball-reference.com/leagues/NBA_{curr}.html'
            ts_index, data_index, drtg_col = 21, 24, 11
        else: 
            url = f'https://www.basketball-reference.com/playoffs/NBA_{curr}.html'
            ts_index, data_index, drtg_col = 19, 22, 9
        response = requests.get(url).text.replace("<!--","").replace("-->","")
        ts = pd.read_html(response)[ts_index]
        data_pd = pd.read_html(response)[data_index]
        ts = ts[["Team", "FGA", "FTA", "PTS"]]
        data_pd = data_pd[[data_pd.columns[1], data_pd.columns[drtg_col]]]
        data_pd = data_pd.set_axis(['TEAM', 'DRTG'], axis=1)
        data_pd["TS%"] = ts["PTS"] / (2 * (ts["FGA"] + (0.44 * ts["FTA"])))
        data_pd = data_pd.query("DRTG >= @min_drtg and DRTG < @max_drtg")
        pd.options.mode.chained_assignment = None
        data_pd["TEAM"] = data_pd["TEAM"].str.extract(r'(.*)\*')
        data_pd["TEAM"] = data_pd["TEAM"].str.upper().map(TEAM_TO_TEAM_ABBR)
        data_pd["SEASON"] = curr
        dfs.append(data_pd)
        curr += 1
    result = pd.concat(dfs)
    result = result.reset_index(drop=True)
    result.index += 1
    return result.iloc[:,[3, 0, 1, 2]]