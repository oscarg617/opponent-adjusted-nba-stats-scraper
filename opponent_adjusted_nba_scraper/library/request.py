'''Sending Requests through HTTP'''
import sys
import requests
import pandas as pd
from bs4 import BeautifulSoup
from ratelimit import sleep_and_retry, limits
from opponent_adjusted_nba_scraper.library import parameters

class Request:
    '''Class used for sending requests'''

    def __init__(
        self,
        url,
        attr_id=None,
        function=None,
        year=None,
        season_type=None,
        measure_type=None,
        per_mode=None,
        opp_id=None
    ):
        self.function = function
        self.url = url
        self.attr_id = attr_id
        self.headers = None

        if function is None:
            self.function = requests.get

        if "stats.nba.com" in self.url:
            self.headers = parameters._standard_header()

        if measure_type and per_mode and year and season_type:
            self.params = parameters\
                ._team_advanced_params(measure_type, per_mode, year, season_type)
        elif opp_id and year and season_type:
            self.params = parameters\
                ._player_per_poss_param(opp_id, year, season_type)
        elif year and season_type:
            self.params = parameters\
                ._player_logs_params(year, season_type)
        else:
            self.params = ()

    def get_response(self):
        '''Send request based on url'''
        if "basketball-reference.com" in self.url:
            return self._bball_ref_response()
        if "stats.nba.com" in self.url:
            return self._nba_stats_response()
        return None

    def _bball_ref_response(self):
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}
        response = self.get_wrapper().text.replace("<!--","").replace("-->","")
        soup = BeautifulSoup(response, features="lxml")
        table = soup.find("table", attrs=self.attr_id)
        header = []
        rows = []
        for i, row in enumerate(table.find_all('tr')):
            if i == 0:
                header = [el.text.strip() for el in row.find_all('th')]
            else:
                rows.append([el.text.strip() for el in row.find_all('td')])

        return pd.DataFrame(rows, columns=header[1:])

    def _nba_stats_response(self):
        response = self.get_wrapper()
        response_json = response.json()
        data_frame = pd.DataFrame(response_json['resultSets'][0]['rowSet'])

        if data_frame.empty:
            return data_frame
        data_frame.columns = response_json['resultSets'][0]['headers']
        return data_frame

    @sleep_and_retry
    @limits(calls=19, period=60)
    def get_wrapper(self):
        '''Wrapper used to limit HTTP calls.'''

        if not self.headers:
            self.headers = {}

        response = \
            self.function(url=self.url, headers=self.headers, params=self.params, timeout=10)
        if response.status_code != 200:
            sys.exit(f"{response.status_code} Error")
        return response
