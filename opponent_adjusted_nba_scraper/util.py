'''Utils for calculating total and average stats.'''
import sys
from typing import Callable
import requests
from ratelimit import sleep_and_retry, limits
from bs4 import BeautifulSoup
import pandas as pd
import unidecode

try:
    from constants import Mode, SeasonType, Site
except ModuleNotFoundError:
    from opponent_adjusted_nba_scraper.constants import Mode, SeasonType, Site


def _calculate_stats(_name: str, logs: pd.DataFrame, teams_df: pd.DataFrame, \
                add_possessions: Callable, data_format: Mode, season_type: SeasonType) -> dict:

    teams_df = _filter_teams_through_logs(logs, teams_df)

    if len(teams_df) == 0:
        _print_no_logs(_name)

    teams_dict = _teams_df_to_dict(teams_df)
    logs = _filter_logs_through_teams(logs, teams_dict)

    opp_drtg, player_true_shooting, relative_true_shooting = \
        _calculate_efficiency_stats(logs, teams_dict, teams_df)

    if data_format == Mode.per_game:
        points = f"{round(logs['PTS'].mean(), 1)} points per game"
        rebounds = f"{round(logs['TRB'].mean(), 1)} rebounds per game"
        assists = f"{round(logs['AST'].mean(), 1)} assists per game"
    elif data_format == Mode.per_100_poss:
        possessions = add_possessions(_name, logs, teams_dict, season_type)
        points = f"{round((logs['PTS'].sum() / possessions) * 100, 1)} points per 100 possessions"
        rebounds = f"{round((logs['TRB'].sum() / possessions) * 100, 1)}" + \
            "rebounds per 100 possessions"
        assists = f"{round((logs['AST'].sum() / possessions) * 100, 1)}" + \
            "assists per 100 possessions"
    elif data_format == Mode.pace_adj:
        possessions = add_possessions(_name, logs, teams_dict, season_type)
        min_ratio = logs['MIN'].mean() / 48
        points = f"{round((min_ratio * (logs['PTS'].sum() / possessions) * 100), 1)}" + \
            " pace-adjusted points per game"
        rebounds = f"{round((min_ratio * (logs['TRB'].sum() / possessions) * 100), 1)}" + \
            " pace-adjusted rebounds per game"
        assists = f"{round((min_ratio * (logs['AST'].sum() / possessions) * 100), 1)}" + \
            " pace-adjusted assists per game"
    elif data_format == Mode.opp_adj:
        points = f"{round((logs['PTS'].mean() * (110 / opp_drtg)), 1)} opponent-adjusted" + \
            " points per game"
        rebounds = f"{round(logs['TRB'].mean(), 1)} rebounds per game"
        assists = f"{round(logs['AST'].mean(), 1)} assists per game"
    elif data_format == Mode.opp_pace_adj:
        possessions = add_possessions(_name, logs, teams_dict, season_type)
        points_per_100 = (logs['PTS'].sum() / possessions) * 100
        points = f"{round(((logs['MIN'].mean() / 48) * points_per_100 * (110 / opp_drtg)), 1)}" + \
            " opponent and pace-adjusted points per game"
        rebounds = f"{round(logs['TRB'].mean(), 1)} rebounds per game"
        assists = f"{round(logs['AST'].mean(), 1)} assists per game"
    else:
        sys.exit(f"Not a valid data format: {data_format}")

    return {
        "points": points,
        "rebounds": rebounds, 
        "assists": assists, 
        "TS%": player_true_shooting, 
        "rTS%": relative_true_shooting, 
        "DRTG": opp_drtg
    }

def _calculate_efficiency_stats(logs: pd.DataFrame, teams_dict: dict, teams_df: pd.DataFrame)\
      -> tuple[float, float, float]:
    opp_drtg_sum = 0
    opp_true_shooting_sum = 0
    for year in teams_dict:
        for opp_team in teams_dict[year]:
            logs_in_year = logs[logs['SEASON'] == year]
            logs_vs_team = logs_in_year[logs_in_year['MATCHUP'] == opp_team]
            opp_drtg_sum += (float(teams_df[teams_df['TEAM'] == opp_team].DRTG.values[0]) *
                             logs_vs_team.shape[0])
            teams_in_year = teams_df[teams_df['SEASON'] == year]
            opp_true_shooting_sum += (float(teams_in_year[teams_in_year['TEAM'] == opp_team]
                                            .OPP_TS.values[0]) * logs_vs_team.shape[0])
    opp_drtg = round((opp_drtg_sum / logs.shape[0]), 1)
    opp_true_shooting = (opp_true_shooting_sum / logs.shape[0]) * 100
    player_true_shooting = \
        _true_shooting_percentage(logs.PTS.sum(), logs.FGA.sum(), logs.FTA.sum()) * 100
    relative_true_shooting = round(player_true_shooting - opp_true_shooting, 1)
    return (opp_drtg, player_true_shooting, relative_true_shooting)

def _teams_df_to_dict(teams_df: pd.DataFrame) -> dict:
    if not teams_df.empty:
        df_list = list(zip(teams_df.SEASON, teams_df.TEAM))
        rslt = {}
        length = len(df_list)
        for index in range(length):
            if df_list[index][0] in rslt:
                rslt[df_list[index][0]].append(df_list[index][1])
            else:
                rslt[df_list[index][0]] = [df_list[index][1]]
        return rslt
    return None

def _filter_logs_through_teams(logs_df, teams_dict):
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

def _filter_teams_through_logs(logs_df, teams_df):
    dfs = []
    for log in range(logs_df.shape[0]):
        df_team = teams_df[teams_df['TEAM'] == logs_df.iloc[log].MATCHUP]
        df_year = df_team[df_team['SEASON'] == logs_df.iloc[log].SEASON]
        dfs.append(df_year)
    all_dfs = pd.concat(dfs)
    result = all_dfs.drop_duplicates()
    return result

def _true_shooting_percentage(pts, fga, fta):
    return pts / (2 * (fga + (0.44 * fta)))

def _add_names():
    url = 'https://www.basketball-reference.com/players/'
    alphabet= ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q',
               'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    with open("names.txt", "w", encoding='utf-8') as file:
        for letter in alphabet:
            names = _get_names(url + letter + '/players')
            for name in names:
                file.write(unidecode.unidecode(name).replace("*", "") + "\n")
    file.close()

def _get_names(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" + \
               "(KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}
    response = \
        _request_get_wrapper(requests.get, url=url, headers=headers, check_error=True)
    soup = BeautifulSoup(response.text, features="lxml")
    table = soup.findAll("th", attrs={"class": "left", "scope": "row"})
    names = [value.text for value in table]
    return names

def _check_drtg_and_year_ranges(year_range: list, drtg_range: list, site: Site):
    if len(year_range) != 2:
        sys.exit(f"Year range list {year_range} must have 2 elements.")
    if len(drtg_range) != 2:
        sys.exit(f"DRTG range list {drtg_range} must have 2 elements.")
    if year_range[0] > year_range[1]:
        sys.exit(f"Year range list {year_range} must be in non-descending order.")
    if drtg_range[0] > drtg_range[1]:
        sys.exit(f"DRTG range list {drtg_range} must be in non-descending order.")
    if site == Site.basketball_reference:
        if year_range[0] < 1971:
            sys.exit(f"Required data is not avaiable before the 1970-71 season ({site}).")
    elif site == Site.nba_stats:
        if year_range[0] < 1997:
            sys.exit(f"Required data is not avaiable before the 1970-71 season ({site}).")


def _print_no_logs(name):
    print(f"No logs found for `{name}`.")
    sys.exit(1)

@sleep_and_retry
@limits(calls=19, period=60)
def _request_get_wrapper(function: Callable, url: str, headers=None, params=(), check_error=False):
    if not headers:
        headers = {}

    response = function(url=url, headers=headers, params=params, timeout=10)
    if check_error and response.status_code != 200:
        # if url.contains("gamelog"):
        #     sys.exit(f"{response.status_code} Error. Check if the player's name" + \
        #              " is spelled correctly.")
        sys.exit(f"{response.status_code} Error")
    return response
