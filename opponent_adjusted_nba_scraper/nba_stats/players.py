'''Methods to find players' stats or game logs given a range of seasons
from stats.nba.com.'''
import pandas as pd

try:
    from utils.constants import Mode, SeasonType
    from utils.util import _calculate_stats, _print_no_logs
    from nba_stats.utils import _format_year, _add_possessions, _get_dataframe
    from nba_stats.teams import teams_within_drtg
    from nba_stats.request_constants import _standard_header, _player_logs_params
except ModuleNotFoundError:
    from opponent_adjusted_nba_scraper.utils.constants import Mode, SeasonType
    from opponent_adjusted_nba_scraper.utils.util import _calculate_stats, _print_no_logs
    from opponent_adjusted_nba_scraper.nba_stats.utils import _format_year, _add_possessions, \
        _get_dataframe
    from opponent_adjusted_nba_scraper.nba_stats.teams import teams_within_drtg
    from opponent_adjusted_nba_scraper.nba_stats.request_constants import _standard_header, \
        _player_logs_params

def player_game_logs(_name, year_range, season_type=SeasonType.default):
    '''
    Returns a Pandas Dataframe of a players logs from a range of years.
    '''

    curr_year = year_range[0]
    dfs = []
    while curr_year <= year_range[1]:
        year = _format_year(curr_year)
        url = 'https://stats.nba.com/stats/playergamelogs'
        params = _player_logs_params(year, season_type)
        year_df = _get_dataframe(url, _standard_header(), params)
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

def player_stats(name, year_range, drtg_range, data_format=Mode.default,
                  season_type=SeasonType.default):
    '''
    Calculates a players stats between a range of years against a select group of 
    opponents based on defensive strength.
    '''

    logs = player_game_logs(name, year_range, season_type)
    if len(logs) == 0:
        return _print_no_logs(name)

    teams = teams_within_drtg(drtg_range, year_range)
    if len(teams) == 0:
        return _print_no_logs(name)

    stats = _calculate_stats(name, logs, teams, _add_possessions, data_format, season_type)
    if stats is None:
        return _print_no_logs(name)
    return stats
