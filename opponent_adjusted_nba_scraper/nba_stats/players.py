import pandas as pd

try:
    from utils.util import _teams_df_to_dict, _filter_logs_through_teams, _filter_teams_through_logs
    from nba_stats.utils import _true_shooting_percentage, _format_year, _total_possessions, _get_dataframe
    from nba_stats.teams import _teams_within_drtg
    import nba_stats.request_constants as rc
except:
    from opponent_adjusted_nba_scraper.utils.util import _teams_df_to_dict, _filter_logs_through_teams, _filter_teams_through_logs
    from opponent_adjusted_nba_scraper.nba_stats.utils import _true_shooting_percentage, _format_year, _total_possessions, _get_dataframe
    from opponent_adjusted_nba_scraper.nba_stats.teams import _teams_within_drtg
    import opponent_adjusted_nba_scraper.nba_stats.request_constants as rc

def _player_game_logs(name, first_year, last_year, season_type="Playoffs"):
    curr_year = first_year
    dfs = []
    while curr_year <= last_year:
        year = _format_year(curr_year)
        url = 'https://stats.nba.com/stats/playergamelogs'
        params = rc.player_logs_params(year, season_type)
        df = _get_dataframe(url, rc._STANDARD_HEADER, params)
        df = df.query('PLAYER_NAME == @name')
        df = (df[['SEASON_YEAR', 'PLAYER_NAME', 'TEAM_ABBREVIATION', 'TEAM_NAME', 'MATCHUP', 'MIN', 'FGM', 'FGA', 'FG_PCT', 
        'FG3M', 'FG3A', 'FG3_PCT','FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'PF', 'PTS', 'PLUS_MINUS']]
            .rename(columns={'SEASON_YEAR':'SEASON', 'TEAM_ABBREVIATION': 'TEAM', 'PLUS_MINUS':'+/-', 'FG_PCT': 'FG%', 
            'FG3M': '3PM', 'FG3A': '3PA', 'FG3_PCT': '3P%', 'FT_PCT': 'FT%'})
            .drop('TEAM_NAME', axis=1)[::-1]
        )
        df['MATCHUP'] = df['MATCHUP'].str[-3:]
        dfs.append(df)
        curr_year += 1
    result = pd.concat(dfs)
    result = result.reset_index(drop=True)
    convert_dict = {
        'FGM': 'int32', 'FGA': 'int32', '3PM': 'int32', '3PA': 'int32', 'FTA': 'int32', 'FTM': 'int32', 'OREB': 'int32', 'DREB': 'int32',
        'REB': 'int32', 'AST': 'int32', 'TOV': 'int32', 'STL': 'int32', 'BLK': 'int32', 'PF': 'int32', 'PTS': 'int32', '+/-': 'int32',
    }
    result = result.astype(convert_dict)
    result.index += 1
    print(result.info())
    return result
