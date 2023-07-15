import os
import threading
import pandas as pd
import concurrent.futures
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from scrapingbee import ScrapingBeeClient

csv_writer_lock = threading.Lock()

load_dotenv()
api_key = os.getenv("API-KEY")
client = ScrapingBeeClient(api_key=api_key)

MAX_THREADS = 10
BASE_URL = "https://basketball-reference.com"

years_lst = [_ for _ in range(1980, 2023)]


def scrape_defense(year):
    url = f"/leagues/NBA_{str(year)}.html"
    response = client.get(BASE_URL + url)
    if response.ok:
        soup = BeautifulSoup(response.text, features="lxml")
        # teams_lst = soup.findAll("td", attrs={"class": "left", "data-stat": "team"}) # [td.a.get("href")[7:10] for td in soup.findAll("td", attrs={"class": "left", "data-stat": "team"})]
        table = soup.find("table", attrs={"id": "advanced-team"})
        teams_lst = table.find_all("td", attrs={"class": "left", "data-stat": "team"})
        teams_lst = [
            a.get("href")[7:10]
            for a in [td for td in [td.a for td in teams_lst] if td is not None]
        ]
        drtg_lst = [
            float(td.text)
            for td in table.find_all(
                "td", attrs={"class": "right", "data-stat": "def_rtg"}
            )
        ]
        table_ts_pct = soup.find("table", attrs={"id": "totals-opponent"})
        teams_lst2 = table_ts_pct.find_all(
            "td", attrs={"class": "left", "data-stat": "team"}
        )
        teams_lst2 = [
            a.get("href")[7:10]
            for a in [td for td in [td.a for td in teams_lst2] if td is not None]
        ]
        fga = [
            int(td.text)
            for td in table_ts_pct.find_all(
                "td", attrs={"class": "right", "data-stat": "opp_fga"}
            )
        ]
        fta = [
            int(td.text)
            for td in table_ts_pct.find_all(
                "td", attrs={"class": "right", "data-stat": "opp_fta"}
            )
        ]
        pts = [
            int(td.text)
            for td in table_ts_pct.find_all(
                "td", attrs={"class": "right", "data-stat": "opp_pts"}
            )
        ]
        ts_lst = [(pts[i] / (2 * (fga[i] + (0.44 * fta[i])))) for i in range(len(pts))]
        drtg_tuples = [(teams_lst[i], drtg_lst[i]) for i in range(len(teams_lst))]
        ts_tuples = [(teams_lst2[i], ts_lst[i]) for i in range(len(teams_lst2))]
        drtg_tuples.sort(key=lambda x: x[0])
        ts_tuples.sort(key=lambda x: x[0])
        defense_tuples = [
            (ts_tuples[i][0], drtg_tuples[i][1], ts_tuples[i][1])
            for i in range(len(ts_tuples))
        ]
        df = pd.DataFrame(defense_tuples, columns=["Team", "Def_Rtg", "TS_Pct"])
        df["SEASON"] = year
        df = df.iloc[:, [3, 0, 1, 2]]
        with csv_writer_lock:
            old_data = pd.read_csv("team_defense.csv")
            new_data = pd.concat([old_data, df], axis=0)
            new_data.to_csv("team_defense.csv", index=False)
    else:
        return response.status_code


# with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
#      executor.map(scrape_defense, years_lst)
