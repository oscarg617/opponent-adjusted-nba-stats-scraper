'''Utils for calculating total and average stats.'''
import sys
import unicodedata
from typing import Callable
import requests
from bs4 import BeautifulSoup
import pandas as pd
import unidecode

try:
    from utils.constants import Mode, SeasonType
except ModuleNotFoundError:
    from opponent_adjusted_nba_scraper.utils.constants import Mode, SeasonType

# Credit to https://github.com/vishaalagartha for the following four functions
def _get_game_suffix(date, team1, team2):
    response = requests.get(f'https://www.basketball-reference.com/boxscores/index.fcgi?year=\
                   {date.year}&month={date.month}&day={date.day}', timeout=10)
    suffix = None
    if response.status_code==200:
        soup = BeautifulSoup(response.content, 'html.parser')
        for table in soup.find_all('table', attrs={'class': 'teams'}):
            for anchor in table.find_all('a'):
                if 'boxscores' in anchor.attrs['href']:
                    if team1 in anchor.attrs['href'] or team2 in anchor.attrs['href']:
                        suffix = anchor.attrs['href']
    return suffix

# Helper function for inplace creation of suffixes--necessary in order
# to fetch rookies and other players who aren't in the /players
# catalogue. Added functionality so that players with abbreviated names
# can still have a suffix created.
def _create_last_name_part_of_suffix(potential_last_names):
    last_names = ''.join(potential_last_names)
    if len(last_names) <= 5:
        return last_names[:].lower()
    return last_names[:5].lower()


# Amended version of the original suffix function--it now creates all
# suffixes in place.
# Since basketball reference standardizes URL codes, it is much more efficient
# to create them locally and compare names to the page results. The maximum
# amount of times a player code repeats is 5, but only 2 players have this
# problem--meaning most player URLs are correctly accessed within 1 to 2
# iterations of the while loop below.
# Added unidecode to make normalizing incoming string characters more
# consistent.
# This implementation dropped player lookup fail count from 306 to 35 to 0.
def _get_player_suffix(name):
    name = unidecode.unidecode(unicodedata.normalize('NFD', name)
                                          .encode('ascii', 'ignore')
                                          .decode("utf-8"))
    if name == 'Metta World Peace':
        suffix = '/players/a/artesro01.html'
    else:
        if len(name.split(' ')) < 2:
            return None
        initial = name.split(' ')[1][0].lower()
        all_names = name.split(' ')
        first_name_part = unidecode.unidecode(all_names[0][:2].lower())
        first_name = all_names[0]
        other_names = all_names[1:]
        other_names_search = other_names
        last_name_part = _create_last_name_part_of_suffix(other_names)
        suffix = '/players/'+initial+'/'+last_name_part+first_name_part+'01.html'
    player_r = requests.get(f'https://www.basketball-reference.com{suffix}', timeout=10)
    while player_r.status_code == 404:
        other_names_search.pop(0)
        last_name_part = _create_last_name_part_of_suffix(other_names_search)
        initial = last_name_part[0].lower()
        suffix = '/players/'+initial+'/'+last_name_part+first_name_part+'01.html'
        player_r = requests.get(f'https://www.basketball-reference.com{suffix}', timeout=10)
    while player_r.status_code==200:
        player_soup = BeautifulSoup(player_r.content, 'html.parser')
        heading1 = player_soup.find('h1')
        if heading1:
            page_name = heading1.find('span').text
            # Test if the URL we constructed matches the
            # name of the player on that page; if it does,
            # return suffix, if not add 1 to the numbering
            # and recheck.
            if (unidecode.unidecode(page_name)).lower() == name.lower():
                return suffix
            page_first_name = unidecode.unidecode(page_name).lower().split(' ')[0]
            if first_name.lower() == page_first_name.lower():
                return suffix
            # if players have same first two letters of last name then just
            # increment suffix
            if first_name.lower()[:2] == page_first_name.lower()[:2]:
                player_number = int(''.join(c for c in suffix if c.isdigit())) + 1
                if player_number < 10:
                    player_number = f"0{str(player_number)}"
                suffix = f"/players/\
                    {initial}/\
                    {last_name_part}\
                    {first_name_part}\
                    {player_number}.html"
            else:
                other_names_search.pop(0)
                last_name_part = _create_last_name_part_of_suffix(other_names_search)
                initial = last_name_part[0].lower()
                suffix = '/players/'+initial+'/'+last_name_part+first_name_part+'01.html'

                player_r = requests.get(f'https://www.basketball-reference.com{suffix}',
                                        timeout=10)
    sys.exit(f'{player_r.status_code} Error')


def _remove_accents(name, team, season_end_year):
    alphabet = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXZY ')
    if len(set(name).difference(alphabet))==0:
        return name
    response = requests.get(f'https://www.basketball-reference.com/teams/{team}/\
                            {season_end_year}.html', timeout=10)
    team_df = None
    best_match = name
    if response.status_code==200:
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table')
        team_df = pd.read_html(str(table))[0]
        max_matches = 0
        for player in team_df['Player']:
            matches = sum(l1 == l2 for l1, l2 in zip(player, name))
            if matches>max_matches:
                max_matches = matches
                best_match = player
    return best_match

def _calculate_stats(logs: pd.DataFrame, teams_df: pd.DataFrame, add_possessions: Callable,
                     data_format: Mode, season_type: SeasonType) -> dict:

    teams_df = _filter_teams_through_logs(logs, teams_df)

    if len(teams_df) == 0:
        return None

    teams_dict = _teams_df_to_dict(teams_df)
    logs = _filter_logs_through_teams(logs, teams_dict)

    opp_drtg, player_true_shooting, relative_true_shooting = \
        _calculate_efficiency_stats(logs, teams_dict, teams_df)

    if data_format == Mode.per_game:
        points = f"{round(logs['PTS'].mean(), 1)} points per game"
        rebounds = f"{round(logs['TRB'].mean(), 1)} rebounds per game"
        assists = f"{round(logs['AST'].mean(), 1)} assists per game"
    elif data_format == Mode.per_100_poss:
        possessions = add_possessions(logs, teams_dict, season_type)
        points = f"{round((logs['PTS'].sum() / possessions) * 100, 1)} points per 100 possessions"
        rebounds = f"{round((logs['TRB'].sum() / possessions) * 100, 1)} \
            rebounds per 100 possessions"
        assists = f"{round((logs['AST'].sum() / possessions) * 100, 1)} \
            assists per 100 possessions"
    elif data_format == Mode.pace_adj:
        possessions = add_possessions(logs, teams_dict, season_type)
        min_ratio = logs['MIN'].mean() / 48
        points = f"{round((min_ratio * (logs['PTS'].sum() / possessions) * 100), 1)} \
            pace-adjusted points per game"
        rebounds = f"{round((min_ratio * (logs['TRB'].sum() / possessions) * 100), 1)} \
            pace-adjusted rebounds per game"
        assists = f"{round((min_ratio * (logs['AST'].sum() / possessions) * 100), 1)} \
            pace-adjusted assists per game"
    elif data_format == Mode.opp_adj:
        points = f"{round((logs['PTS'].mean() * (110 / opp_drtg)), 1)} opponent-adjusted \
            points per game"
        rebounds = f"{round(logs['TRB'].mean(), 1)} rebounds per game"
        assists = f"{round(logs['AST'].mean(), 1)} assists per game"
    elif data_format == Mode.opp_pace_adj:
        possessions = add_possessions(logs, teams_dict, season_type)
        points_per_100 = (logs['PTS'].sum() / possessions) * 100
        points = f"{round(((logs['MIN'].mean() / 48) * points_per_100 * (110 / opp_drtg)), 1)} \
            opponent and pace-adjusted points per game"
        rebounds = f"{round(logs['TRB'].mean(), 1)} rebounds per game"
        assists = f"{round(logs['AST'].mean(), 1)} assists per game"

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
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
               (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code != 200:
        sys.exit(f"{response.status_code} Error")
    soup = BeautifulSoup(response.text, features="lxml")
    table = soup.findAll("th", attrs={"class": "left", "scope": "row"})
    names = [value.text for value in table]
    return names

def _print_no_logs(name):
    print(f"No logs found for `{name}`.")
