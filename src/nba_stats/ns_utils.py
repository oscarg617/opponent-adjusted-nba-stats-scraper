from requests import get
import pandas as pd

import nba_stats.request_constants as rc
from utils.constants import TEAMS


def total_possessions(name, logs, team_dict, season_type="Playoffs"):
    total_poss = 0
    for year in team_dict:
        for opp_team in team_dict[year]:
            opp_id = 1610612700 + int(TEAMS[opp_team])
            url = 'https://stats.nba.com/stats/leaguedashplayerstats'
            df = get_dataframe(url, rc.STANDARD_HEADER, rc.player_per_poss_param(opp_id, year, season_type))
            if df.empty: return
            df = df.query('PLAYER_NAME == @name')
            min_per_poss = df.iloc[0]['MIN']
            filter = logs.query('SEASON == @year')
            filter = logs.query('MATCHUP == @opp_team')
            min_played = filter['MIN'].sum()
            poss = min_played / min_per_poss
            total_poss += round(poss)
    return total_poss

def get_dataframe(url, header, param):
    response = get(url, headers=header, params=param)
    if response.status_code != 200:
        exit(f"{response.status_code} Gateway Timeout")
    response_json = response.json()
    df = pd.DataFrame(response_json['resultSets'][0]['rowSet'])
    if df.empty: 
        return df
    df.columns = response_json['resultSets'][0]['headers']
    return df

def teams_df_to_dict(df):
    if not df.empty:
        df_list = list(zip(df.SEASON, df.TEAM_ABBR))
        rslt = {}
        length = len(df_list)
        for index in range(length):
            if df_list[index][0] in rslt:
                rslt[df_list[index][0]].append(df_list[index][1])
            else:
                rslt[df_list[index][0]] = [df_list[index][1]]
        return rslt
    else:
        return None

def filter_logs_through_teams(logs_df, teams_dict):
    dfs = []
    for year in teams_dict:
        length_value = len(teams_dict[year])
        for team_index in range(length_value):
            abbr = teams_dict[year][team_index]
            df_team = logs_df[logs_df['MATCHUP'] == abbr]
            df_year = df_team[df_team['SEASON'] == year]
            dfs.append(df_year)
    result = pd.concat(dfs)
    return result

def filter_teams_through_logs(logs_df, teams_df):
    dfs = []
    for log in range(logs_df.shape[0]):
        df_team = teams_df[teams_df['TEAM'] == logs_df.iloc[log].MATCHUP]
        df_year = df_team[df_team['SEASON'] == logs_df.iloc[log].SEASON]    
        dfs.append(df_year)
    all_dfs = pd.concat(dfs)
    result = all_dfs.drop_duplicates()
    return result

def format_year(end_year):
    start_year = end_year - 1
    end_year_format = end_year % 100
    if end_year_format >= 10:
        return f'{start_year}-{end_year_format}'
    else: 
        return f'{start_year}-0{end_year_format}'

def true_shooting_percentage(pts, fga, fta):
    return pts / (2 * (fga + (0.44 * fta)))
