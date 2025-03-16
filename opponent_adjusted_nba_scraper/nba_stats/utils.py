'''Utils for stats.nba.com scraping'''
import sys
import requests
import pandas as pd

try:
    from nba_stats.request_constants import _standard_header, _player_per_poss_param
    from utils.constants import _TEAMS, SeasonType
except ModuleNotFoundError:
    from opponent_adjusted_nba_scraper.nba_stats.request_constants import _standard_header, \
        _player_per_poss_param
    from opponent_adjusted_nba_scraper.utils.constants import _TEAMS, SeasonType

def _add_possessions(logs: pd.DataFrame, team_dict: dict, season_type: SeasonType):
    total_poss = 0
    for year in team_dict:
        for opp_team in team_dict[year]:
            opp_id = 1610612700 + int(_TEAMS[opp_team])
            url = 'https://stats.nba.com/stats/leaguedashplayerstats'
            per_poss_df = _get_dataframe(url, _standard_header(),
                                _player_per_poss_param(opp_id, year, season_type))
            if per_poss_df.empty:
                break
            per_poss_df = per_poss_df.query('PLAYER_NAME == @name')
            min_per_poss = per_poss_df.iloc[0]['MIN']
            filtered_logs = logs.query('SEASON == @year').query('MATCHUP == @opp_team')
            min_played = filtered_logs['MIN'].sum()
            poss = min_played / min_per_poss
            total_poss += round(poss)
    return total_poss

def _get_dataframe(url, header, param):
    response = requests.get(url, headers=header, params=param, timeout=10)
    if response.status_code != 200:
        sys.exit(f"{response.status_code} Gateway Timeout")
    response_json = response.json()
    data_frame = pd.DataFrame(response_json['resultSets'][0]['rowSet'])
    if data_frame.empty:
        return data_frame
    data_frame.columns = response_json['resultSets'][0]['headers']
    return data_frame

def _format_year(end_year):
    start_year = end_year - 1
    end_year_format = end_year % 100
    if end_year_format >= 10:
        return f'{start_year}-{end_year_format}'
    return f'{start_year}-0{end_year_format}'
