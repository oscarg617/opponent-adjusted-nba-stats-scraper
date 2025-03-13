import requests
import pandas as pd
import numpy as np
from tqdm import tqdm
try:
    from utils.constants import _TEAM_TO_TEAM_ABBR
    from bball_ref.utils import _get_dataframe
except:
    from opponent_adjusted_nba_scraper.utils.constants import _TEAM_TO_TEAM_ABBR
    from opponent_adjusted_nba_scraper.bball_ref.utils import _get_dataframe

def _teams_within_drtg(min_drtg, max_drtg, first_year, last_year, season_type='Regular Season'):
    dfs = []
    for curr in tqdm(range(first_year, last_year + 1), desc="Loading opponents' stats...", ncols=75):
        if season_type == "Regular Season":
            url = f'https://www.basketball-reference.com/leagues/NBA_{curr}.html'
        else: 
            url = f'https://www.basketball-reference.com/playoffs/NBA_{curr}.html'
        ts = _get_dataframe(url, "totals-opponent")
        data_pd = _get_dataframe(url, "advanced-team")
        ts = ts[["Team", "FGA", "FTA", "PTS"]]
        data_pd = data_pd[["Team", "DRtg"]]
        data_pd = data_pd.rename(columns={"Team": "TEAM", "DRtg": "DRTG"})
        ts = ts.astype({'Team': 'string', 'FGA': 'int32', 'FGA': 'int32', 'FTA': 'int32', 'PTS': 'int32'})
        data_pd = data_pd.astype({'TEAM': 'string', 'DRTG': 'float64'})
        data_pd["OPP_TS"] = ts["PTS"] / (2 * (ts["FGA"] + (0.44 * ts["FTA"])))
        data_pd = data_pd.query("DRTG >= @min_drtg and DRTG < @max_drtg")
        pd.options.mode.chained_assignment = None
        data_pd = data_pd.replace('\*','',regex=True).astype(str)
        data_pd = data_pd[(data_pd["TEAM"].str.contains("League Average")==False)]
        data_pd["TEAM"] = data_pd["TEAM"].str.upper().map(_TEAM_TO_TEAM_ABBR)
        data_pd["SEASON"] = curr
        dfs.append(data_pd)
    result = pd.concat(dfs)
    result = result.reset_index(drop=True)
    result.index += 1
    return result.iloc[:,[3, 0, 1, 2]]