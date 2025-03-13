import requests
import pandas as pd
import numpy as np
from tqdm import tqdm
try:
    from utils.constants import Mode
    from utils.lookup import _lookup
    from utils.util import _get_player_suffix, _calculate_stats
    from bball_ref.utils import _get_dataframe, _add_possessions
    from utils.constants import _DESIRED_LOG_COLUMNS
    from bball_ref.teams import _teams_within_drtg
except:
    from opponent_adjusted_nba_scraper.utils.constants import Mode
    from opponent_adjusted_nba_scraper.utils.lookup import _lookup
    from opponent_adjusted_nba_scraper.utils.util import _get_player_suffix, _calculate_stats
    from opponent_adjusted_nba_scraper.bball_ref.utils import _get_dataframe, _add_possessions
    from opponent_adjusted_nba_scraper.utils.constants import _DESIRED_LOG_COLUMNS
    from opponent_adjusted_nba_scraper.bball_ref.teams import _teams_within_drtg

def _player_game_logs(_name, first_year, last_year, season_type="Playoffs"):
    name = _lookup(_name, ask_matches=False)
    suffix = _get_player_suffix(name)[:-5]
    dfs = []
    iterator = tqdm(range(first_year, last_year + 1), desc="Loading player game logs...", ncols=75)
    for curr in iterator:
        if season_type == "Playoffs":
            url = f'https://www.basketball-reference.com{suffix}/gamelog-playoffs/'
        else: 
            url = f'https://www.basketball-reference.com/{suffix}/gamelog/{curr}'
        data_pd = _get_dataframe(url, "pgl_basic_playoffs")
        data_pd = data_pd.drop(["G", "G#", "Series", "", "GS"], axis=1)
        data_pd = data_pd.replace("", 0)
        data_pd["SEASON"] = data_pd[data_pd.columns[0]].str[:4].astype("string")
        data_pd = data_pd.iloc[:, [len(data_pd.columns) - 1] + [x for x in range(len(data_pd.columns) - 1)]]
        data_pd = (data_pd[(data_pd["AST"].str.contains("Inactive")==False) & (data_pd["AST"].str.contains("AST")==False) & 
            (data_pd["AST"].str.contains("Did Not Play")==False) & (data_pd["AST"].str.contains("Did Not Dress")==False)]
            .rename(columns={data_pd.columns[1]: "DATE", "Tm": "TEAM", "Opp": "MATCHUP", 
            "MP": "MIN"})
        )
        data_pd["minutes"] = data_pd["MIN"].str.extract(r'([1-9]*[0-9]):')
        data_pd["seconds"] = data_pd["MIN"].str.extract(r':([0-5][0-9])')
        data_pd["MIN"] = data_pd["minutes"].astype("int32") + (data_pd["seconds"].astype("int32") / 60)
        data_pd = data_pd.drop(columns=["minutes", "seconds"])
        convert_dict = {
        'SEASON': 'int32', 'DATE': 'string', 'TEAM': 'string', 'MATCHUP': 'string', 'MIN': 'float64','FG': 'int32', 
        'FGA': 'int32', 'FG%': 'float64', '3P': 'int32', '3PA': 'int32', '3P%': 'float64', 'FT': 'int32', 'FTA': 'int32', 
        'FT%': 'float64', 'ORB': 'int32', 'DRB': 'int32', 'TRB': 'int32', 'AST' : 'int32', 'STL': 'int32', 'BLK': 'int32', 
        'TOV' : 'int32', 'PF': 'int32', 'PTS': 'int32', 'GmSc': 'float64', '+/-' : 'int32'
        }
        keep = {key: convert_dict[key] for key in data_pd.columns.values}
        data_pd = data_pd.astype(keep)
        if season_type == "Regular Season":
            data_pd["SEASON"] = curr
        data_pd = data_pd.query("SEASON >= @first_year and SEASON <= @last_year")
        dfs.append(data_pd)
        if season_type == "Playoffs":
            for _ in iterator: pass
            break
    result = pd.concat(dfs)
    result = result.reset_index(drop=True)
    result.index += 1
    for i, col in enumerate(_DESIRED_LOG_COLUMNS):
        if col not in result.columns.values:
            if col == "NAME":
                result[col] = name
            else:
                result[col] = np.nan
            left = [x for x in range(i)]
            right = [x for x in range(i, len(result.columns) - 1)]
            result = result.iloc[:, left + [len(result.columns) - 1] + right]
    return result

def player_stats(_name, first_year, last_year, min_drtg=80, max_drtg=130, data_format=Mode.default, season_type="Playoffs", printStats=False):
    logs = _player_game_logs(_name, first_year, last_year, season_type=season_type)
    teams = _teams_within_drtg(min_drtg, max_drtg, first_year, last_year)
    stats = _calculate_stats(_name, logs, teams, _add_possessions, first_year, last_year, data_format, season_type, printStats)
    return stats