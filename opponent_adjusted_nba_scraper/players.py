'''Methods to find players' stats or game logs given a range of seasons
from basketball reference.'''
import sys
import pandas as pd
import numpy as np
from tqdm import tqdm
try:
    from bball_ref_utils import _bball_ref_get_dataframe, _get_player_suffix, \
        _bball_ref_add_possessions
    from constants import _desired_log_columns
    from nba_stats_request_constants import _standard_header, _player_logs_params
    from nba_stats_utils import _format_year, _nba_stats_get_dataframe, _nba_stats_add_possessions
    from parameters import Mode, SeasonType, Site
    from teams import teams_within_drtg
    from util import _calculate_stats, _print_no_logs, _check_drtg_and_year_ranges
except ModuleNotFoundError:
    from opponent_adjusted_nba_scraper.bball_ref_utils import _bball_ref_get_dataframe, \
        _get_player_suffix, _bball_ref_add_possessions
    from opponent_adjusted_nba_scraper.constants import _desired_log_columns
    from opponent_adjusted_nba_scraper.nba_stats_request_constants import _standard_header, \
        _player_logs_params
    from opponent_adjusted_nba_scraper.nba_stats_utils import _format_year, \
        _nba_stats_get_dataframe, _nba_stats_add_possessions
    from opponent_adjusted_nba_scraper.parameters import Mode, SeasonType, Site
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

    # _name = _lookup(_name, ask_matches=False)
    suffix = _get_player_suffix(_name)[:-5]
    iterator = tqdm(range(year_range[0], year_range[1] + 1),
                    desc="Loading player game logs...", ncols=75)

    dfs = []
    for curr_year in iterator:
        if season_type == SeasonType.playoffs:
            url = f'https://www.basketball-reference.com{suffix}/gamelog-playoffs/'
            attr_id = "player_game_log_post"
        else:
            url = f'https://www.basketball-reference.com{suffix}/gamelog/{curr_year}'
            attr_id = "player_game_log_reg"

        data_pd = _bball_ref_get_dataframe(url, attr_id)\
            .drop(columns=["Gtm", "", "GS", "Result"], axis=1)\
            .replace("", np.nan)

        data_pd = data_pd[~(
            (data_pd["Gcar"].astype(str).str.contains("nan")) |
            (data_pd["Gcar"].astype(str).str.contains("none"))
            )]\
            .rename(columns={
                data_pd.columns[1]: "DATE",
                "Team": "TEAM",
                "Opp": "MATCHUP",
                "MP": "MIN"})\
            .dropna(subset=["AST"])\
            .drop(columns=["Gcar"])

        # Calculate Season from Date column instead of using `curr_year` because playoff
        # game logs shows for all years
        data_pd["SEASON"] = curr_year
        data_pd["MIN"] = data_pd["MIN"].str.extract(r'([1-9]*[0-9]):').astype("int32") + \
                        data_pd["MIN"].str.extract(r':([0-5][0-9])').astype("int32") / 60

        convert_dict = {
            'SEASON': 'int32', 'DATE': 'string', 'TEAM': 'string', 'MATCHUP': 'string',
            'MIN': 'float64','FG': 'int32', 'FGA': 'int32', 'FG%': 'float64', '3P': 'float32',
            '3PA': 'float32', '3P%': 'float64', 'FT': 'int32', 'FTA': 'int32', 'FT%': 'float32',
            'ORB': 'float32', 'DRB': 'float32', 'TRB': 'int32', 'AST' : 'int32', 'STL': 'float32',
            'BLK': 'float32', 'TOV' : 'float32', 'PF': 'int32', 'PTS': 'int32', 'GmSc': 'float64',
            '+/-' : 'int32', '2P': 'float32', "2PA": 'float32', '2P%': 'float64', 'eFG%': "float64"
        }
        data_pd = data_pd.astype({key: convert_dict[key] for key in data_pd.columns.values})

        dfs.append(data_pd)

        if season_type == SeasonType.playoffs:
            for _ in iterator:
                pass
            break
        continue

    result = pd.concat(dfs)\
        .reset_index(drop=True, )\
        .query("SEASON >= @year_range[0] and SEASON <= @year_range[1]")
    result.index += 1

    # Some stats were not tracked in the 1970s, so we add those columns with value np.nan
    result["NAME"] = _name
    result.loc[:, list(set(_desired_log_columns()) - set(result.columns.values))] = np.nan
    result = result[_desired_log_columns()]

    if len(result) == 0:
        _print_no_logs(_name)
    return result

def _nba_stats_player_game_logs(_name, year_range, season_type=SeasonType.default):

    _check_drtg_and_year_ranges(year_range, [0, 1], Site.nba_stats)

    iterator = tqdm(range(year_range[0], year_range[1] + 1),
                    desc="Loading player game logs...", ncols=75)

    dfs = []
    for curr_year in iterator:
        curr_year = _format_year(curr_year)
        url = 'https://stats.nba.com/stats/playergamelogs'
        params = _player_logs_params(curr_year, season_type)
        year_df = _nba_stats_get_dataframe(url, _standard_header(), params)
        year_df = year_df.query('PLAYER_NAME == @_name')\
            [['SEASON_YEAR', 'PLAYER_NAME', 'TEAM_ABBREVIATION', 'MATCHUP', 'MIN',
              'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT','FTM', 'FTA', 'FT_PCT', 'OREB',
              'DREB', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'PF', 'PTS', 'PLUS_MINUS']]\
            .rename(columns={
                'SEASON_YEAR':'SEASON', 'TEAM_ABBREVIATION': 'TEAM', 'PLUS_MINUS':'+/-',
                'FG_PCT': 'FG%', 'FG3M': '3PM', 'FG3A': '3PA', 'FG3_PCT': '3P%', 'FT_PCT': 'FT%',
                'REB': 'TRB'})[::-1]
        year_df['MATCHUP'] = year_df['MATCHUP'].str[-3:]

        dfs.append(year_df)

    if len(dfs) == 0:
        return pd.DataFrame()

    result = pd.concat(dfs)\
        .reset_index(drop=True)\
        .astype({
            'FGM': 'int32', 'FGA': 'int32', '3PM': 'int32', '3PA': 'int32', 'FTA': 'int32',
            'FTM': 'int32', 'OREB': 'int32', 'DREB': 'int32', 'TRB': 'int32', 'AST': 'int32',
            'TOV': 'int32', 'STL': 'int32', 'BLK': 'int32', 'PF': 'int32', 'PTS': 'int32',
            '+/-': 'int32', 'SEASON': 'object'})

    result['SEASON'] = result['SEASON'].str[:4].astype(int) + 1
    result.index += 1
    return result
