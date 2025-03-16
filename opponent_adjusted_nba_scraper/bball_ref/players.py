'''Methods to find players' stats or game logs given a range of seasons
from basketball reference.'''
import pandas as pd
import numpy as np
from tqdm import tqdm
try:
    from utils.constants import Mode, SeasonType
    from utils.lookup import _lookup
    from utils.util import _get_player_suffix, _calculate_stats, _print_no_logs
    from utils.constants import _desired_log_columns
    from bball_ref.utils import _get_dataframe, _add_possessions
    from bball_ref.teams import teams_within_drtg
except ModuleNotFoundError:
    from opponent_adjusted_nba_scraper.utils.constants import Mode, SeasonType
    from opponent_adjusted_nba_scraper.utils.lookup import _lookup
    from opponent_adjusted_nba_scraper.utils.constants import _desired_log_columns
    from opponent_adjusted_nba_scraper.utils.util import _get_player_suffix, _calculate_stats,\
                                                                            _print_no_logs
    from opponent_adjusted_nba_scraper.bball_ref.utils import _get_dataframe, _add_possessions
    from opponent_adjusted_nba_scraper.bball_ref.teams import teams_within_drtg

def player_game_logs(_name, year_range, season_type=SeasonType.default):
    '''
    Returns a Pandas Dataframe of a players logs from a range of years.
    '''

    _name = _lookup(_name, ask_matches=False)
    suffix = _get_player_suffix(_name)[:-5]
    iterator = tqdm(range(year_range[0], year_range[1] + 1),
                    desc="Loading player game logs...", ncols=75)

    dfs = []
    for curr in iterator:

        if season_type == SeasonType.playoffs:
            url = f'https://www.basketball-reference.com{suffix}/gamelog-playoffs/'
        else:
            url = f'https://www.basketball-reference.com/{suffix}/gamelog/{curr}'

        data_pd = _get_dataframe(url, "pgl_basic_playoffs")\
            .drop(["G", "G#", "Series", "", "GS"], axis=1)\
            .replace("", 0)

        data_pd["SEASON"] = data_pd[data_pd.columns[0]].str[:4].astype("string")
        data_pd = data_pd.iloc[:, [len(data_pd.columns) - 1] +
                               list(range(len(data_pd.columns) - 1))]
        data_pd = data_pd[
            (data_pd["AST"].str.contains("Inactive") is False) &
            (data_pd["AST"].str.contains("AST") is False) &
            (data_pd["AST"].str.contains("Did Not Play") is False) &
            (data_pd["AST"].str.contains("Did Not Dress") is False)
            ]\
            .rename(columns={
                data_pd.columns[1]: "DATE",
                "Tm": "TEAM",
                "Opp": "MATCHUP",
                "MP": "MIN"})

        data_pd["minutes"] = data_pd["MIN"].str.extract(r'([1-9]*[0-9]):')
        data_pd["seconds"] = data_pd["MIN"].str.extract(r':([0-5][0-9])')
        data_pd["MIN"] = data_pd["minutes"].astype("int32") + \
                        (data_pd["seconds"].astype("int32") / 60)

        data_pd = data_pd.drop(columns=["minutes", "seconds"])
        convert_dict = {
        'SEASON': 'int32', 'DATE': 'string', 'TEAM': 'string', 'MATCHUP': 'string',
        'MIN': 'float64','FG': 'int32', 'FGA': 'int32', 'FG%': 'float64', '3P': 'int32',
        '3PA': 'int32', '3P%': 'float64', 'FT': 'int32', 'FTA': 'int32', 'FT%': 'float64',
        'ORB': 'int32', 'DRB': 'int32', 'TRB': 'int32', 'AST' : 'int32', 'STL': 'int32',
        'BLK': 'int32', 'TOV' : 'int32', 'PF': 'int32', 'PTS': 'int32', 'GmSc': 'float64',
        '+/-' : 'int32'
        }
        keep = {key: convert_dict[key] for key in data_pd.columns.values}
        data_pd = data_pd.astype(keep)
        if season_type == SeasonType.default:
            data_pd["SEASON"] = curr
        data_pd = data_pd.query("SEASON >= @first_year and SEASON <= @last_year")
        dfs.append(data_pd)
        if season_type == SeasonType.playoffs:
            for _ in iterator:
                pass
            break
    result = pd.concat(dfs)
    result = result.reset_index(drop=True)
    result.index += 1
    for i, col in enumerate(_desired_log_columns()):
        if col not in result.columns.values:
            if col == "NAME":
                result[col] = _name
            else:
                result[col] = np.nan
            left = list(range(i))
            right = list(range(i, len(result.columns) - 1))
            result = result.iloc[:, left + [len(result.columns) - 1] + right]
    return result

def player_stats(_name, year_range, drtg_range,
                 data_format=Mode.default, season_type="Playoffs") -> dict:
    '''
    Calculates a players stats between a range of years against a select group of 
    opponents based on defensive strength.
    '''

    logs = player_game_logs(_name, year_range, season_type=season_type)
    if len(logs) == 0:
        return _print_no_logs(_name)

    teams = teams_within_drtg(drtg_range, year_range)
    if len(teams) == 0:
        return _print_no_logs(_name)

    stats = _calculate_stats(logs, teams, _add_possessions, data_format, season_type)
    if stats is None:
        return _print_no_logs(_name)
    return stats
