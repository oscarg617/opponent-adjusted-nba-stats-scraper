from requests import get
import pandas as pd

try:
    import nba_stats.request_constants as rc
    from utils.constants import TEAMS
except:
    import opponent_adjusted_nba_scraper.nba_stats.request_constants as rc
    from opponent_adjusted_nba_scraper.utils.constants import TEAMS

def add_possessions(name, logs, team_dict, season_type="Playoffs"):
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

def format_year(end_year):
    start_year = end_year - 1
    end_year_format = end_year % 100
    if end_year_format >= 10:
        return f'{start_year}-{end_year_format}'
    else: 
        return f'{start_year}-0{end_year_format}'
