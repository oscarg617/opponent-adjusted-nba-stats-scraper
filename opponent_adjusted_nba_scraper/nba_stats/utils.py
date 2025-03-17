'''Utils for stats.nba.com scraping'''
import sys
import requests
import pandas as pd
from tqdm import tqdm

try:
    from nba_stats.request_constants import _standard_header, _player_per_poss_param
    from utils.constants import _teams, SeasonType
    from utils.util import _request_get_wrapper
except ModuleNotFoundError:
    from opponent_adjusted_nba_scraper.nba_stats.request_constants import _standard_header, \
        _player_per_poss_param
    from opponent_adjusted_nba_scraper.utils.constants import _teams, SeasonType
    from opponent_adjusted_nba_scraper.utils.util import _request_get_wrapper

def _add_possessions(logs: pd.DataFrame, team_dict: dict, season_type: SeasonType):
    total_poss = 0
    teams_list = [(year, opp_team) for year in team_dict for opp_team in team_dict[year]]
    for year, opp_team in tqdm(teams_list, desc="Loading player possessions...", ncols=75):
            opp_id = 1610612700 + int(_teams()[opp_team])
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

def _get_dataframe(url, headers, params):
    response = _request_get_wrapper(requests.get, {
        "url": url,
        "headers": headers,
        "params": params,
        "timeout": 10
    })
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
