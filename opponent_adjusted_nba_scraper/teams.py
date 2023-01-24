import time
import pandas as pd
from requests import get

try:
    from constants import TEAM_TO_TEAM_ABBR
    from utils import format_year, true_shooting_percentage
    import request_constants as rc
except:
    from opponent_adjusted_nba_scraper.constants import TEAM_TO_TEAM_ABBR
    from opponent_adjusted_nba_scraper.utils import format_year, true_shooting_percentage
    import opponent_adjusted_nba_scraper.request_constants as rc

def teams_within_drtg(min_drtg, max_drtg, first_year, last_year, season_type='Playoffs'):
    curr_year = first_year
    frames = []
    while curr_year <= last_year:
        year = format_year(curr_year)
        url = 'https://stats.nba.com/stats/leaguedashteamstats'
        response = get(url, headers=rc.STANDARD_HEADER, params=rc.team_advanced_params('Advanced', 'PerGame', year, season_type), stream=True)
        time.sleep(.600)
        response_json = response.json()
        frame = pd.DataFrame(response_json['resultSets'][0]['rowSet'])
        frame.columns = response_json['resultSets'][0]['headers']
        frame = frame[frame['DEF_RATING'] < max_drtg]
        frame = frame[frame['DEF_RATING'] >= min_drtg]
        frame = frame[['TEAM_NAME', 'DEF_RATING']]
        frame = frame.rename(columns={'TEAM_NAME': 'TEAM_ABBR'})
        year_list = [year for _ in range(frame.shape[0])]
        ds_year = pd.Series(index=range(frame.shape[0]), data=year_list, name='SEASON_YEAR', dtype=str)
        abbr_list = [TEAM_TO_TEAM_ABBR[team.upper()] for team in frame['TEAM_ABBR']]
        ds_abbr = pd.Series(index=range(frame.shape[0]), data=abbr_list, name='TEAM_ABBR', dtype=str)
        df_year = ds_year.to_frame()
        df_abbr = ds_abbr.to_frame()
        frame = frame.assign(SEASON_YEAR=df_year['SEASON_YEAR'].values)
        frame = frame.assign(TEAM_ABBR=df_abbr['TEAM_ABBR'].values)
        response = get(url, headers=rc.STANDARD_HEADER, params=rc.team_advanced_params('Opponent', 'Totals', year, season_type), stream=True)
        time.sleep(.600)
        response_json = response.json()
        ts_frame = pd.DataFrame(response_json['resultSets'][0]['rowSet'])
        ts_frame.columns = response_json['resultSets'][0]['headers']
        ts_frame = ts_frame[['TEAM_NAME', 'OPP_PTS', 'OPP_FGA', 'OPP_FTA']]
        ts_frame = ts_frame.rename(columns={'TEAM_NAME': 'TEAM_ABBR'})
        abbr_list = [TEAM_TO_TEAM_ABBR[team.upper()] for team in ts_frame['TEAM_ABBR']]
        ds_abbr = pd.Series(index=range(ts_frame.shape[0]), data=abbr_list, name='TEAM_ABBR')
        df_abbr = ds_abbr.to_frame()
        ts_frame = ts_frame.assign(TEAM_ABBR=df_abbr['TEAM_ABBR'].values)
        ts_frame = ts_frame[ts_frame['TEAM_ABBR'].isin(frame.TEAM_ABBR.values.tolist())]
        ts_frame['OPP_TS_PCT'] = ts_frame.apply(lambda row : true_shooting_percentage(row['OPP_PTS'],
                     row['OPP_FGA'], row['OPP_FTA']), axis=1)
        frame = frame.assign(OPP_TS_PCT=ts_frame['OPP_TS_PCT'].values)
        frames.append(frame)
        curr_year += 1
    result = pd.concat(frames)
    return result.iloc[:,[2, 0, 1, 3]]

def filter_logs_through_teams(logs_df, teams_dict):
    frames = []
    for year in teams_dict:
        length_value = len(teams_dict[year])
        for team_index in range(length_value):
            abbr = teams_dict[year][team_index]
            df_team = logs_df[logs_df['MATCHUP'] == abbr]
            df_year = df_team[df_team['SEASON_YEAR'] == year]
            frames.append(df_year)
    result = pd.concat(frames)
    return result

def filter_teams_through_logs(logs_df, teams_df):
    frames = []
    for log in range(logs_df.shape[0]):
        df_team = teams_df[teams_df['TEAM_ABBR'] == logs_df.iloc[log].MATCHUP]
        df_year = df_team[df_team['SEASON_YEAR'] == logs_df.iloc[log].SEASON_YEAR]    
        frames.append(df_year)
    all_frames = pd.concat(frames)
    result = all_frames.drop_duplicates()
    return result
