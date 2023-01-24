import time
import requests
import pandas as pd

try:
    from constants import TEAMS
    import request_constants as rc
except:
    from opponent_adjusted_nba_scraper.constants import TEAMS
    import opponent_adjusted_nba_scraper.request_constants as rc


def total_possessions(_name, logs, team_dict, season_type="Playoffs"):
    total_poss = 0
    for year in team_dict:
        for opp_team in team_dict[year]:
            opp_id = 1610612700 + int(TEAMS[opp_team])
            url = 'https://stats.nba.com/stats/leaguedashplayerstats'
            response = requests.get(url, headers=rc.STANDARD_HEADER, params=rc.player_per_poss_param(opp_id, year, season_type), stream=True)
            time.sleep(.600)
            response_json = response.json()
            frame = pd.DataFrame(response_json['resultSets'][0]['rowSet'])
            if frame.empty: return
            frame.columns = response_json['resultSets'][0]['headers']
            rslt_df_large = frame[frame['PLAYER_NAME'] == _name]
            if rslt_df_large.empty: return
            min_per_poss = rslt_df_large.iloc[0]['MIN']
            filter_season = logs[logs['SEASON_YEAR'] == year]
            filter_both = filter_season[filter_season['MATCHUP'] == opp_team]
            min_played = filter_both['MIN'].sum()
            poss = min_played / min_per_poss
            total_poss += round(poss)
    return total_poss

def teams_df_to_dict(df):
    if not df.empty:
        df_list = list(zip(df.SEASON_YEAR, df.TEAM_ABBR))
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

def format_year(end_year):
    start_year = end_year - 1
    end_year_format = end_year % 100
    if end_year_format >= 10:
        return f'{start_year}-{end_year_format}'
    else: 
        return f'{start_year}-0{end_year_format}'

def true_shooting_percentage(pts, fga, fta):
    return pts / (2 * (fga + (0.44 * fta)))
