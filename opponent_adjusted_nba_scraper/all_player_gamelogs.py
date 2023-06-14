import concurrent.futures
import pandas as pd
from bs4 import BeautifulSoup
from utils.constants import DESIRED_LOG_COLUMNS
import numpy as np
import time
import threading
csv_writer_lock = threading.Lock()
from scrapingbee import ScrapingBeeClient # Importing SPB's client
client = ScrapingBeeClient(api_key='YIX02QIVSSSNUFEHSIFMAEA3W0SVDEXKUR9E6TLSRUS8EO54VV39E16A213PFLM9D5FIZ4CZ7GPJW4PM') # Initialize the client with your API Key, and using screenshot_full_page parameter to take a screenshot!

MAX_RETRIES = 3 # Setting the maximum number of retries if we have failed requests to 5.
MAX_THREADS = 5
BASE_URL = 'https://www.basketball-reference.com'

players_suffixes = pd.read_csv('names.csv')
urls = []
for i in range(players_suffixes.shape[0]):
    name = players_suffixes.loc[i, "Player"]
    start = players_suffixes.loc[i, "From_Year"]
    end = players_suffixes.loc[i, "To_Year"]
    suffix = players_suffixes.loc[i, "Suffix"]
    urls.append([name, start, end, suffix])

def scrape(url):
    for _ in range(MAX_RETRIES):
        time.sleep(3)
        response = client.get(BASE_URL + url[3][:-5] + '/gamelog-playoffs') # Scrape!
        
        if response.ok: # If we get a successful request
            soup = BeautifulSoup(response.text, features="lxml")
            table = soup.find("table", attrs={"id": "pgl_basic_playoffs"})
            header = []
            rows = []
            for i, row in enumerate(table.find_all('tr')):
                if i == 0:
                    header = [el.text.strip() for el in row.find_all('th')]
                else:
                    rows.append([el.text.strip() for el in row.find_all('td')])

            data_pd = pd.DataFrame(rows, columns=header[1:])

            data_pd = data_pd.drop(["G", "G#", "Series", "", "GS"], axis=1)
            data_pd = data_pd.replace("", 0)
            data_pd["SEASON"] = data_pd[data_pd.columns[0]].str[:4].astype("string")
            data_pd = data_pd.iloc[:, [len(data_pd.columns) - 1] + [x for x in range(len(data_pd.columns) - 1)]]
            data_pd = (data_pd[(data_pd["AST"].str.contains("Inactive")==False) & (data_pd["AST"].str.contains("AST")==False) & 
                (data_pd["AST"].str.contains("Did Not Play")==False) & (data_pd["AST"].str.contains("Did Not Dress")==False)]
                .rename(columns={data_pd.columns[1]: "DATE", "Tm": "TEAM", "Opp": "MATCHUP", 
                "MP": "MIN"})
            )
            data_pd["minutes"] = data_pd["MIN"].str.extract(r'([1-9]*[0-9]):')
            data_pd["seconds"] = data_pd["MIN"].str.extract(r':([0-5][0-9])')
            data_pd["MIN"] = data_pd["minutes"].astype("int32") + (data_pd["seconds"].astype("int32") / 60)
            data_pd = data_pd.drop(columns=["minutes", "seconds"])
            convert_dict = {
            'SEASON': 'int32', 'DATE': 'string', 'TEAM': 'string', 'MATCHUP': 'string', 'MIN': 'float64','FG': 'int32', 
            'FGA': 'int32', 'FG%': 'float64', '3P': 'int32', '3PA': 'int32', '3P%': 'float64', 'FT': 'int32', 'FTA': 'int32', 
            'FT%': 'float64', 'ORB': 'int32', 'DRB': 'int32', 'TRB': 'int32', 'AST' : 'int32', 'STL': 'int32', 'BLK': 'int32', 
            'TOV' : 'int32', 'PF': 'int32', 'PTS': 'int32', 'GmSc': 'float64', '+/-' : 'int32'
            }
            keep = {key: convert_dict[key] for key in data_pd.columns.values}
            data_pd = data_pd.astype(keep)
            start_year = url[1]
            end_year = url[2]
            data_pd = data_pd.query("SEASON >= @start_year and SEASON <= @end_year")
            data_pd = data_pd.reset_index(drop=True)
            data_pd.index += 1

            if data_pd.empty:
                break

            for i, col in enumerate(DESIRED_LOG_COLUMNS):
                if col not in data_pd.columns.values:
                    if col == "NAME":
                        data_pd[col] = url[0]
                    else:
                        data_pd[col] = np.nan
                    left = [x for x in range(i)]
                    right = [x for x in range(i, len(data_pd.columns) - 1)]
                    data_pd = data_pd.iloc[:, left + [len(data_pd.columns) - 1] + right]

            with csv_writer_lock:
                old_data = pd.read_csv("player_logs.csv")
                new_data = pd.concat([old_data, data_pd], axis=0)
                new_data.to_csv("player_logs.csv", index=False)
                break
        elif response.status_code == 404 or response.status_code == 500:
            print(url)
            print(str(url[0]) + " has never played a playoff game in his life.")
            break
        else: # If we get a failed request, then we continue the loop
            with csv_writer_lock:
                old_names = pd.read_csv("retry.csv")
                old_names.loc[len(old_names.index)] = url[0]
                old_names.to_csv("retry.csv", index=False)
            print("error for " + url[0] + " for years from " + str(url[1]) + " to " + str(url[2]) + ". the url is: " + BASE_URL + url[3][:-5] + '/gamelog-playoffs' + " . The response error code is: " + str(response.status_code))
            time.sleep(10)

# with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
    #  executor.map(scrape, urls)