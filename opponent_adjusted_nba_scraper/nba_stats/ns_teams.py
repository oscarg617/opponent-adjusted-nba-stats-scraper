import time
import pandas as pd
from requests import get
from opponent_adjusted_nba_scraper.constants import TEAM_TO_TEAM_ABBR

try:
    from ns_utils import format_year, true_shooting_percentage, get_dataframe
    import request_constants as rc
except:
    from opponent_adjusted_nba_scraper.nba_stats.ns_utils import format_year, true_shooting_percentage, get_dataframe
    import opponent_adjusted_nba_scraper.nba_stats.request_constants as rc

def teams_within_drtg(min_drtg, max_drtg, first_year, last_year, season_type='Playoffs'):
    curr_year = first_year
    dfs = []
    while curr_year <= last_year:
        year = format_year(curr_year)
        url = 'https://stats.nba.com/stats/leaguedashteamstats'
        params = rc.team_advanced_params('Advanced', 'PerGame', year, season_type)
        df = get_dataframe(url, rc.STANDARD_HEADER, params)
        df = df.query('DEF_RATING < @max_drtg and DEF_RATING >= @min_drtg')[['TEAM_NAME', 'DEF_RATING']]
        df['TEAM_ABBR'] = df['TEAM_NAME'].str.upper().map(TEAM_TO_TEAM_ABBR)
        df = df.drop('TEAM_NAME', axis=1)
        df['SEASON_YEAR'] = year
        params = rc.team_advanced_params('Opponent', 'Totals', year, season_type)
        ts_df = get_dataframe(url, rc.STANDARD_HEADER, params)
        ts_df = ts_df[['TEAM_NAME', 'OPP_PTS', 'OPP_FGA', 'OPP_FTA']]
        ts_df['TEAM_ABBR'] = ts_df['TEAM_NAME'].str.upper().map(TEAM_TO_TEAM_ABBR)
        ts_df = (ts_df.drop('TEAM_NAME', axis=1)
            .query('TEAM_ABBR.isin(@df.TEAM_ABBR.values.tolist())'))
        df['OPP_TS_PCT'] = (ts_df['OPP_PTS']) / (2 * (ts_df['OPP_FGA'] + (0.44 * ts_df['OPP_FTA'])))
        dfs.append(df)
        curr_year += 1
    result = pd.concat(dfs)
    result = result.iloc[:,[2, 1, 0, 3]].reset_index(drop=True)
    result['OPP_TS_PCT'] = result['OPP_TS_PCT'].astype('float16')
    return result

def filter_logs_through_teams(logs_df, teams_dict):
    dfs = []
    for year in teams_dict:
        length_value = len(teams_dict[year])
        for team_index in range(length_value):
            abbr = teams_dict[year][team_index]
            df_team = logs_df[logs_df['MATCHUP'] == abbr]
            df_year = df_team[df_team['SEASON_YEAR'] == year]
            dfs.append(df_year)
    result = pd.concat(dfs)
    return result

def filter_teams_through_logs(logs_df, teams_df):
    dfs = []
    for log in range(logs_df.shape[0]):
        df_team = teams_df[teams_df['TEAM_ABBR'] == logs_df.iloc[log].MATCHUP]
        df_year = df_team[df_team['SEASON_YEAR'] == logs_df.iloc[log].SEASON_YEAR]    
        dfs.append(df_year)
    all_dfs = pd.concat(dfs)
    result = all_dfs.drop_duplicates()
    return result