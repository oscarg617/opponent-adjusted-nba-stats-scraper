'''Utils for basketball-reference scraping.'''
import sys
import time
import unicodedata
import requests
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm
import unidecode

try:
    from parameters import SeasonType
    from util import _request_get_wrapper
except ModuleNotFoundError:
    from opponent_adjusted_nba_scraper.parameters import SeasonType
    from opponent_adjusted_nba_scraper.util import _request_get_wrapper

def _bball_ref_get_dataframe(url: str, attrs_id: str) -> pd.DataFrame:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}

    response = _request_get_wrapper(requests.get, url=url, headers=headers, check_error=True)
    soup = BeautifulSoup(response.text, features="lxml")
    table = soup.find("table", attrs={"id": attrs_id})
    header = []
    rows = []
    for i, row in enumerate(table.find_all('tr')):
        if i == 0:
            header = [el.text.strip() for el in row.find_all('th')]
        else:
            rows.append([el.text.strip() for el in row.find_all('td')])
    if attrs_id == "advanced-team":
        header = ["Rk", "Team", "Age", "W", "L", "PW", "PL", "MOV", "SOS", "SRS", "ORtg",
                "DRtg", "NRtg", "Pace", "FTr", "3PAr", "TS%", " ", "eFG%", "TOV%", "ORB%",
                "FT/FGA", " ", "eFG%", "TOV%", "DRB%", "FT/FGA", " ", "Arena", "Attend.",
                "Attend./G"]
        rows = rows[1:]
    return pd.DataFrame(rows, columns=header[1:])

def _bball_ref_add_possessions(_name: str, logs: pd.DataFrame, _team_dict: dict, \
                     _season_type: SeasonType) -> int:
    total_poss = 0
    logs["DATE"] = pd.to_datetime(logs["DATE"])
    logs["GAME_SUFFIX"] = ""
    for i in tqdm(range(len(logs)), desc='Loading player possessions...', ncols=75):
        suffix = _get_game_suffix(logs.iloc[i]["DATE"], logs.iloc[i]["TEAM"],
                                                    logs.iloc[i]["MATCHUP"])
        url = f'https://www.basketball-reference.com{suffix}'
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" + \
        " (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}
        response = _request_get_wrapper(requests.get, url=url, headers=headers, check_error=True)
        response = response.text.replace("<!--","").replace("-->","")
        soup = BeautifulSoup(response, features="lxml")
        pace = soup.find("td", attrs={"data-stat":"pace"}).text
        total_poss += (logs.iloc[i]["MIN"] / 48) * float(pace)
        time.sleep(21)
    logs = logs.drop(columns=["GAME_SUFFIX"])
    return total_poss

# Credit to https://github.com/vishaalagartha for the following four functions

def _get_game_suffix(date, team1, team2):
    url = "https://www.basketball-reference.com/boxscores/index.fcgi?year=" + \
            f"{date.year}&month={date.month}&day={date.day}"
    response = _request_get_wrapper(requests.get, url=url)
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
        return '/players/a/artesro01.html'

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
    player_r = _request_get_wrapper(requests.get, url='https://www.basketball' + \
                                    f'-reference.com{suffix}')
    while player_r.status_code == 404:
        other_names_search.pop(0)
        last_name_part = _create_last_name_part_of_suffix(other_names_search)
        initial = last_name_part[0].lower()
        suffix = '/players/'+initial+'/'+last_name_part+first_name_part+'01.html'
        player_r = _request_get_wrapper(requests.get, url='https://www.basketball' + \
                                        f'-reference.com{suffix}')
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
                player_r = _request_get_wrapper(requests.get, url='https://www.basketball' + \
                                                f'-reference.com{suffix}')
    sys.exit(f'{player_r.status_code} Error')


def _remove_accents(name, team, season_end_year):
    alphabet = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXZY ')
    if len(set(name).difference(alphabet))==0:
        return name
    response = _request_get_wrapper(requests.get, url='https://www.basketball-reference.com' + \
                                    f'/teams/{team}/{season_end_year}.html')
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
