import threading
import pandas as pd
import concurrent.futures
from bs4 import BeautifulSoup
from scrapingbee import ScrapingBeeClient
client = ScrapingBeeClient(
    api_key='YIX02QIVSSSNUFEHSIFMAEA3W0SVDEXKUR9E6TLSRUS8EO54VV39E16A213PFLM9D5FIZ4CZ7GPJW4PM')
csv_writer_lock = threading.Lock()

BASE_URL = 'https://www.basketball-reference.com'

MAX_THREADS = 20

years_lst = [_ for _ in range(1980, 2023)]

failed = []


def scrape_pace(years):
    res = []
    for year in years:
        url = f'/playoffs/NBA_{year}_games.html'
        response = client.get(BASE_URL + url)
        if response.ok:
            soup = BeautifulSoup(response.text, features='lxml')
            box_scores = soup.findAll(
                "td", attrs={"class": "center", "data-stat": "box_score_text"})
            res.extend([box.a.get("href") for box in box_scores])
        else:
            return response.status_code
    return res


def get_pace_dataframe(suffix):
    response = client.get(BASE_URL + suffix)
    if response.ok:
        soup = BeautifulSoup(response.text, features='lxml')
        teams = soup.findAll(
            "th", attrs={"scope": "row", "class": "left", "data-stat": "team_id"})
        home_team = teams[0].text
        away_team = teams[1].text
        pace = soup.find(
            "td", attrs={"class": "right", "data-stat": "pace"}).text
        year = suffix[11:15]
        month = suffix[15:17]
        day = suffix[17:19]
        df = pd.DataFrame(
            columns=["Season", "Date", "Home_Team", "Away_Team", "Pace"])
        df.loc[len(df.index)] = [int(year), year+'-' +
                                 month+'-'+day, home_team, away_team, pace]
        with csv_writer_lock:
            old_data = pd.read_csv("game_pace.csv")
            new_data = pd.concat([old_data, df], axis=0)
            new_data.to_csv("game_pace.csv", index=False)
    else:
        failed.append(suffix)


suffices = scrape_pace(years_lst)


# with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
#      executor.map(get_pace_dataframe, suffices)
