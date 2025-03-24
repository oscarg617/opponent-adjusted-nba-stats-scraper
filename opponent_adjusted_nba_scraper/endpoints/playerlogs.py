'''Player Logs Endpoint'''
import os
import sys
import numpy as np
import pandas as pd
from tqdm import tqdm

try:
    from _base import Endpoint
    from library.arguments import SeasonType
    from library.request import Request
except ImportError:
    from opponent_adjusted_nba_scraper.endpoints._base import Endpoint
    from opponent_adjusted_nba_scraper.library.arguments import SeasonType
    from opponent_adjusted_nba_scraper.library.request import Request

class PlayerLogs(Endpoint):
    '''Finds a player's game logs within a given range of years'''

    expected_columns = [
        'SEASON',
        'DATE',
        'NAME',
        'TEAM',
        'HOME',
        'MATCHUP',
        'MIN',
        'FG',
        'FGA',
        'FG%',
        '3P',
        '3PA',
        '3P%',
        'FT',
        'FTA',
        'FT%',
        'ORB',
        'DRB',
        'TRB',
        'AST',
        'STL',
        'BLK',
        'TOV',
        'PF',
        'PTS',
        'GmSc',
        '+/-'
    ]

    data = None
    data_frame = None

    def __init__(
        self,
        name,
        year_range,
        season_type=SeasonType.default
    ):
        self.name = name
        self.year_range = year_range
        self.season_type = season_type
        self.suffix = self._lookup(name)

    def _lookup(self, name):
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data\\player_names.csv')
        names_df = pd.read_csv(path)
        player = names_df[names_df["NAME"] == name]["SUFFIX"]
        if len(player) == 0:
            sys.exit(f"Player not found: `{name}`")
        return player.iloc[0]

    def bball_ref(self):
        '''Uses bball-ref to find player game logs.'''
        format_suffix = 'players/' + self.suffix[0] + '/' + self.suffix
        iterator = tqdm(range(self.year_range[0], self.year_range[1] + 1),
                        desc="Loading player game logs...", ncols=75)

        dfs = []
        for curr_year in iterator:
            if self.season_type == SeasonType.playoffs:
                url = f'https://www.basketball-reference.com/{format_suffix}/gamelog-playoffs/'
                attr_id = "player_game_log_post"
            else:
                url = f'https://www.basketball-reference.com/{format_suffix}/gamelog/{curr_year}'
                attr_id = "player_game_log_reg"

            data_pd = Request(url=url, attr_id={"id": attr_id}).get_response()\
                .drop(columns=["Gtm", "GS", "Result"], axis=1)\
                .replace("", np.nan)

            data_pd = data_pd[~(
                (data_pd["Gcar"].astype(str).str.contains("nan")) |
                (data_pd["Gcar"].astype(str).str.contains("none"))
                )]\
                .rename(columns={
                    data_pd.columns[1]: "DATE",
                    "Team": "TEAM",
                    "Opp": "MATCHUP",
                    "MP": "MIN",
                    "": "HOME"})\
                .dropna(subset=["AST"])\
                .drop(columns=["Gcar"])

            # Calculate Season from Date column instead of using `curr_year` because playoff
            # game logs shows for all years
            data_pd["SEASON"] = data_pd["DATE"].str[0:4].astype(int)
            data_pd["MIN"] = data_pd["MIN"].str.extract(r'([1-9]*[0-9]):').astype("int32") + \
                            data_pd["MIN"].str.extract(r':([0-5][0-9])').astype("int32") / 60

            convert_dict = {
                'SEASON': 'int32', 'DATE': 'string', 'TEAM': 'string', 'MATCHUP': 'string',
                'MIN': 'float64','FG': 'int32', 'FGA': 'int32', 'FG%': 'float64', '3P': 'float32',
                '3PA': 'float32', '3P%': 'float64', 'FT': 'int32', 'FTA': 'int32',
                'FT%': 'float32', 'ORB': 'float32', 'DRB': 'float32', 'TRB': 'int32',
                'AST' : 'int32', 'STL': 'float32', 'BLK': 'float32', 'TOV' : 'float32',
                'PF': 'int32', 'PTS': 'int32', 'GmSc': 'float64', '+/-' : 'int32',
                '2P': 'float32', "2PA": 'float32', '2P%': 'float64', 'eFG%': "float64",
                'HOME': 'string'
            }
            data_pd = data_pd.astype({key: convert_dict[key] for key in data_pd.columns.values})

            dfs.append(data_pd)

            if self.season_type == SeasonType.playoffs:
                for _ in iterator:
                    pass
                break
            continue

        result = pd.concat(dfs)\
            .reset_index(drop=True)\
            .query("SEASON >= @self.year_range[0] and SEASON <= @self.year_range[1]")

        # Some stats were not tracked in the 1970s, so we add those columns with value np.nan
        result["NAME"] = self.name
        result["HOME"] = result['HOME'].replace(np.nan, "")
        result.loc[:, list(set(self.expected_columns) - set(result.columns.values))] = np.nan
        result = result[self.expected_columns]
        return result

    def nba_stats(self):
        '''Uses nba-stats to find player game logs'''
        iterator = tqdm(range(self.year_range[0], self.year_range[1] + 1),
                        desc="Loading player game logs...", ncols=75)

        dfs = []
        for curr_year in iterator:
            curr_year = self._format_year(curr_year)
            url = 'https://stats.nba.com/stats/playergamelogs'
            year_df = Request(url=url, year=curr_year, season_type=self.season_type).get_response()
            year_df = year_df.query('PLAYER_NAME == @self.name')\
                [['SEASON_YEAR', 'PLAYER_NAME', 'TEAM_ABBREVIATION', 'MATCHUP', 'MIN',
                'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT','FTM', 'FTA', 'FT_PCT', 'OREB',
                'DREB', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'PF', 'PTS', 'PLUS_MINUS']]\
                .rename(columns={
                    'SEASON_YEAR':'SEASON', 'TEAM_ABBREVIATION': 'TEAM', 'PLUS_MINUS':'+/-',
                    'FG_PCT': 'FG%', 'FG3M': '3PM', 'FG3A': '3PA', 'FG3_PCT': '3P%',
                    'FT_PCT': 'FT%', 'REB': 'TRB'})[::-1]
            year_df['MATCHUP'] = year_df['MATCHUP'].str[-3:]

            dfs.append(year_df)

        if len(dfs) == 0:
            return pd.DataFrame()

        result = pd.concat(dfs)\
            .reset_index(drop=True)\
            .astype({
                'FGM': 'int32', 'FGA': 'int32', '3PM': 'int32', '3PA': 'int32', 'FTA': 'int32',
                'FTM': 'int32', 'OREB': 'int32', 'DREB': 'int32', 'TRB': 'int32', 'AST': 'int32',
                'TOV': 'int32', 'STL': 'int32', 'BLK': 'int32', 'PF': 'int32', 'PTS': 'int32',
                '+/-': 'int32', 'SEASON': 'object'})

        result['SEASON'] = result['SEASON'].str[:4].astype(int) + 1
        return result
