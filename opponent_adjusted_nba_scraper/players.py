'''Methods to find players' stats or game logs given a range of seasons
from basketball reference.'''
import sys
import pandas as pd
import numpy as np
from tqdm import tqdm
try:
    from bball_ref_lookup import _lookup
    from bball_ref_utils import _bball_ref_get_dataframe, _get_player_suffix, \
        _bball_ref_add_possessions
    from constants import Mode, SeasonType, Site, _desired_log_columns
    from nba_stats_request_constants import _standard_header, _player_logs_params
    from nba_stats_utils import _format_year, _nba_stats_get_dataframe, _nba_stats_add_possessions
    from teams import teams_within_drtg
    from util import _calculate_stats, _print_no_logs, _check_drtg_and_year_ranges
except ModuleNotFoundError:
    from opponent_adjusted_nba_scraper.bball_ref_lookup import _lookup
    from opponent_adjusted_nba_scraper.bball_ref_utils import _bball_ref_get_dataframe, \
        _get_player_suffix, _bball_ref_add_possessions
    from opponent_adjusted_nba_scraper.constants import Mode, SeasonType, Site, \
        _desired_log_columns
    from opponent_adjusted_nba_scraper.nba_stats_request_constants import _standard_header, \
        _player_logs_params
    from opponent_adjusted_nba_scraper.nba_stats_utils import _format_year, \
        _nba_stats_get_dataframe, _nba_stats_add_possessions
    from opponent_adjusted_nba_scraper.teams import teams_within_drtg
    from opponent_adjusted_nba_scraper.util import _calculate_stats, _print_no_logs, \
        _check_drtg_and_year_ranges

pd.set_option('display.max_rows', None)

def player_stats(_name, year_range, drtg_range, data_format=Mode.default, \
                 season_type=SeasonType.default, site=Site.default) -> dict:
    '''
    Calculates a players stats between a range of years against a select group of 
    opponents based on defensive strength.
    '''

    logs = player_game_logs(_name, year_range, season_type, site)
    teams = teams_within_drtg(year_range, drtg_range, site)
    if site == Site.basketball_reference:
        add_possessions = _bball_ref_add_possessions
    elif site == Site.nba_stats:
        add_possessions = _nba_stats_add_possessions
    else:
        sys.exit(f"Not a valid site: {site}")
    stats = _calculate_stats(_name, logs, teams, add_possessions, data_format, season_type)
    return stats



def player_game_logs(_name, year_range, season_type=SeasonType.default, site=Site.default):
    '''
    Returns a Pandas Dataframe of a players logs from a range of years.
    '''

    if site == Site.basketball_reference:
        return _bball_ref_player_game_logs(_name, year_range, season_type)
    if site == Site.nba_stats:
        return _nba_stats_player_game_logs(_name, year_range, season_type)
    return None

def _bball_ref_player_game_logs(_name, year_range, season_type=SeasonType.default):

    _check_drtg_and_year_ranges(year_range, [0, 1], Site.basketball_reference)

    _name = _lookup(_name, ask_matches=False)
    suffix = _get_player_suffix(_name)[:-5]
    iterator = tqdm(range(year_range[0], year_range[1] + 1),
                    desc="Loading player game logs...", ncols=75)

    dfs = []
    for curr in iterator:
        if season_type == SeasonType.playoffs:
            url = f'https://www.basketball-reference.com{suffix}/gamelog-playoffs/'
            data_pd = _bball_ref_get_dataframe(url, "pgl_basic_playoffs")\
                .drop(["G", "G#", "Series", "", "GS"], axis=1)\
                .replace("", np.nan)
        else:
            url = f'https://www.basketball-reference.com/{suffix}/gamelog/{curr}'
            data_pd = _bball_ref_get_dataframe(url, "pgl_basic")\
                .drop(["G", "Age", "", "GS"], axis=1)\
                .replace("", np.nan)

        data_pd["SEASON"] = data_pd[data_pd.columns[0]].str[:4].astype("string")
        data_pd = data_pd.iloc[:, [len(data_pd.columns) - 1] +
                               list(range(len(data_pd.columns) - 1))]

        data_pd.dropna(subset=["AST"], inplace=True)
        data_pd = data_pd[~(
            (data_pd["AST"].str.contains("Inactive")) |
            (data_pd["AST"].str.contains("AST")) |
            (data_pd["AST"].str.contains("Did Not Play")) |
            (data_pd["AST"].str.contains("Did Not Dress"))
            )]\
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
        data_pd = data_pd.query("SEASON >= @year_range[0] and SEASON <= @year_range[1]")
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

    if len(result) == 0:
        _print_no_logs(_name)
    return result

def _nba_stats_player_game_logs(_name, year_range, season_type=SeasonType.default):

    _check_drtg_and_year_ranges(year_range, [0, 1], Site.nba_stats)

    curr_year = year_range[0]
    dfs = []
    while curr_year <= year_range[1]:
        year = _format_year(curr_year)
        url = 'https://stats.nba.com/stats/playergamelogs'
        params = _player_logs_params(year, season_type)
        year_df = _nba_stats_get_dataframe(url, _standard_header(), params)
        year_df = year_df.query('PLAYER_NAME == @_name')
        year_df = (year_df[['SEASON_YEAR', 'PLAYER_NAME', 'TEAM_ABBREVIATION', 'TEAM_NAME',
                'MATCHUP', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT','FTM', 'FTA',
                'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'PF', 'PTS',
                'PLUS_MINUS']]
            .rename(columns={'SEASON_YEAR':'SEASON', 'TEAM_ABBREVIATION': 'TEAM',
                             'PLUS_MINUS':'+/-', 'FG_PCT': 'FG%', 'FG3M': '3PM', 'FG3A': '3PA',
                             'FG3_PCT': '3P%', 'FT_PCT': 'FT%', 'REB': 'TRB'})
            .drop('TEAM_NAME', axis=1)[::-1]
        )
        year_df['MATCHUP'] = year_df['MATCHUP'].str[-3:]
        dfs.append(year_df)
        curr_year += 1
    if len(dfs) == 0:
        return pd.DataFrame()

    result = pd.concat(dfs)
    result = result.reset_index(drop=True)
    convert_dict = {
        'FGM': 'int32', 'FGA': 'int32', '3PM': 'int32', '3PA': 'int32', 'FTA': 'int32',
        'FTM': 'int32', 'OREB': 'int32', 'DREB': 'int32', 'TRB': 'int32', 'AST': 'int32',
        'TOV': 'int32', 'STL': 'int32', 'BLK': 'int32', 'PF': 'int32', 'PTS': 'int32',
        '+/-': 'int32', 'SEASON': 'object'
    }
    result = result.astype(convert_dict)
    result['SEASON'] = result['SEASON'].str[:4].astype(int) + 1
    result.index += 1
    return result
