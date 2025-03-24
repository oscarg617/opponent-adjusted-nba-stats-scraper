'''Player Stats Endpoint.'''
import sys
import requests
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup

try:
    from library.arguments import SeasonType, Mode
    from library.request import Request
    from library import constants
    from _base import Endpoint
    from playerlogs import PlayerLogs
    from teams import Teams
except ImportError:
    from opponent_adjusted_nba_scraper.library.arguments import SeasonType, Mode
    from opponent_adjusted_nba_scraper.library.request import Request
    from opponent_adjusted_nba_scraper.library import constants
    from opponent_adjusted_nba_scraper.endpoints._base import Endpoint
    from opponent_adjusted_nba_scraper.endpoints.playerlogs import PlayerLogs
    from opponent_adjusted_nba_scraper.endpoints.teams import Teams

class PlayerStats(Endpoint):
    '''Calculates players stats against opponents within a given range of defensive strength'''

    def __init__(
        self,
        _name,
        year_range,
        drtg_range,
        data_format=Mode.default,
        season_type=SeasonType.default
    ):
        self.name = _name
        self.year_range = year_range
        self.drtg_range = drtg_range
        self.data_format = data_format
        self.season_type = season_type

    def bball_ref(self):
        '''Uses bball-ref to calculate player logs and team defensive metrics.'''
        logs_df = PlayerLogs(self.name, self.year_range, self.season_type).bball_ref()
        teams_df = Teams(self.year_range, self.drtg_range).bball_ref()
        add_possessions = self._bball_ref_add_possessions
        return self._calculate_stats(logs_df, teams_df, add_possessions)

    def nba_stats(self):
        '''Uses nba-stats to calculate player logs and team defensive metrics.'''
        logs_df = PlayerLogs(self.name, self.year_range, self.season_type).nba_stats()
        teams_df = Teams(self.year_range, self.drtg_range).nba_stats()
        add_possessions = self._nba_stats_add_possessions
        return self._calculate_stats(logs_df, teams_df, add_possessions)

    def _calculate_stats(self, logs_df, teams_df, add_possessions):

        teams_df = self._filter_teams_through_logs(logs_df, teams_df)
        teams_dict = self._teams_df_to_dict(teams_df)
        logs_df = self._filter_logs_through_teams(logs_df, teams_dict)

        opp_drtg, player_true_shooting, relative_true_shooting = \
            self._calculate_efficiency_stats(logs_df, teams_df, teams_dict)

        if self.data_format == Mode.per_game:
            points, rebounds, assists = self._per_game_stats(logs_df)
        elif self.data_format == Mode.per_100_poss:
            points, rebounds, assists = self._per_100_poss_stats(
                logs_df, teams_dict, add_possessions)
        elif self.data_format == Mode.pace_adj:
            points, rebounds, assists = self._pace_adj_stats(
                logs_df, teams_dict, add_possessions)
        elif self.data_format == Mode.opp_adj:
            points, rebounds, assists = self._opp_adj_stats(logs_df, opp_drtg)
        elif self.data_format == Mode.opp_pace_adj:
            points, rebounds, assists = self._opp_pace_adj_stats(
                logs_df, teams_dict, add_possessions, opp_drtg)
        else:
            sys.exit(f"Not a valid data format: {self.data_format}")

        return {
            "points": points,
            "rebounds": rebounds, 
            "assists": assists, 
            "TS%": player_true_shooting, 
            "rTS%": relative_true_shooting, 
            "DRTG": opp_drtg
        }

    def _per_game_stats(self, logs_df):
        points = f"{round(logs_df['PTS'].mean(), 1)} points per game"
        rebounds = f"{round(logs_df['TRB'].mean(), 1)} rebounds per game"
        assists = f"{round(logs_df['AST'].mean(), 1)} assists per game"
        return (points, rebounds, assists)

    def _per_100_poss_stats(self, logs_df, teams_dict, add_possessions):
        possessions = add_possessions(self.name, logs_df, teams_dict, self.season_type)
        points = f"{round((logs_df['PTS'].sum() / possessions) * 100, 1)}" + \
            " points per 100 possessions"
        rebounds = f"{round((logs_df['TRB'].sum() / possessions) * 100, 1)}" + \
            " rebounds per 100 possessions"
        assists = f"{round((logs_df['AST'].sum() / possessions) * 100, 1)}" + \
            " assists per 100 possessions"
        return (points, rebounds, assists)

    def _pace_adj_stats(self, logs_df, teams_dict, add_possessions):
        possessions = add_possessions(logs_df, teams_dict, \
                                            self.season_type, self.site)
        min_ratio = logs_df['MIN'].mean() / 48
        points_val = round((min_ratio * (logs_df['PTS'].sum() / possessions) * 100), 1)
        points = f"{points_val} pace-adjusted points per game"
        rebounds_val = round((min_ratio * (logs_df['TRB'].sum() / possessions) * 100), 1)
        rebounds = f"{rebounds_val} pace-adjusted rebounds per game"
        assists_val = round((min_ratio * (logs_df['AST'].sum() / possessions) * 100), 1)
        assists = f"{assists_val} pace-adjusted assists per game"
        return points, rebounds, assists

    def _opp_adj_stats(self, logs_df, opp_drtg):
        points = f"{round((logs_df['PTS'].mean() * (110 / opp_drtg)), 1)}" + \
            " opponent-adjusted points per game"
        rebounds = f"{round(logs_df['TRB'].mean(), 1)} rebounds per game"
        assists = f"{round(logs_df['AST'].mean(), 1)} assists per game"
        return points, rebounds, assists

    def _opp_pace_adj_stats(self, logs_df, teams_dict, add_possessions, opp_drtg):
        possessions = add_possessions(self.name, logs_df, \
                                            teams_dict, self.season_type)
        points_per_100 = (logs_df['PTS'].sum() / possessions) * 100
        points_val = round(((logs_df['MIN'].mean() / 48) *
                            points_per_100 * (110 / opp_drtg)), 1)
        points = f"{points_val} opponent and pace-adjusted points per game"
        rebounds = f"{round(logs_df['TRB'].mean(), 1)} rebounds per game"
        assists = f"{round(logs_df['AST'].mean(), 1)} assists per game"
        return points, rebounds, assists

    def _filter_teams_through_logs(self, logs_df, teams_df):
        dfs = []
        for log in range(logs_df.shape[0]):
            df_team = teams_df[teams_df['TEAM'] == logs_df.iloc[log].MATCHUP]
            df_year = df_team[df_team['SEASON'] == logs_df.iloc[log].SEASON]
            dfs.append(df_year)
        all_dfs = pd.concat(dfs)
        result = all_dfs.drop_duplicates()
        return result

    def _teams_df_to_dict(self, teams_df):
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

    def _filter_logs_through_teams(self, logs_df, teams_dict):
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

    def _true_shooting_percentage(self, pts, fga, fta):
        return pts / (2 * (fga + (0.44 * fta)))

    def _calculate_efficiency_stats(self, logs_df, teams_df, teams_dict)\
        -> tuple[float, float, float]:
        opp_drtg_sum = 0
        opp_true_shooting_sum = 0
        for year in teams_dict:
            for opp_team in teams_dict[year]:
                logs_in_year = logs_df[logs_df['SEASON'] == year]
                logs_vs_team = logs_in_year[logs_in_year['MATCHUP'] == opp_team]
                opp_drtg_sum += (float(teams_df[teams_df['TEAM'] == opp_team].DRTG.values[0]) *
                                logs_vs_team.shape[0])
                teams_in_year = teams_df[teams_df['SEASON'] == year]
                opp_true_shooting_sum += (float(teams_in_year[teams_in_year['TEAM'] == opp_team]
                                                .OPP_TS.values[0]) * logs_vs_team.shape[0])
        opp_drtg = round((opp_drtg_sum / logs_df.shape[0]), 1)
        opp_true_shooting = (opp_true_shooting_sum / logs_df.shape[0]) * 100
        player_true_shooting = self._true_shooting_percentage(
            logs_df.PTS.sum(), logs_df.FGA.sum(), logs_df.FTA.sum()) * 100
        relative_true_shooting = round(player_true_shooting - opp_true_shooting, 1)
        return (opp_drtg, player_true_shooting, relative_true_shooting)

    def _bball_ref_add_possessions(
        self,
        _name,
        logs_df,
        _team_dict,
        _season_type
    ):
        total_poss = 0
        logs_df["DATE"] = pd.to_datetime(logs_df["DATE"])
        logs_df["GAME_SUFFIX"] = ""
        for i in tqdm(range(len(logs_df)), desc='Loading player possessions...', ncols=75):
            suffix = self._get_game_suffix(logs_df.iloc[i]["DATE"], logs_df.iloc[i]["TEAM"],
                                                        logs_df.iloc[i]["MATCHUP"])
            url = f'https://www.basketball-reference.com{suffix}'
            response = Request(url=url).get_wrapper()
            response = response.text.replace("<!--","").replace("-->","")
            soup = BeautifulSoup(response, features="lxml")
            pace = soup.find("td", attrs={"data-stat":"pace"}).text
            total_poss += (logs_df.iloc[i]["MIN"] / 48) * float(pace)
        logs_df = logs_df.drop(columns=["GAME_SUFFIX"])
        return total_poss

    # Credit to https://github.com/vishaalagartha for the following function

    def _get_game_suffix(self, date, team1, team2):
        url = "https://www.basketball-reference.com/boxscores/index.fcgi?year=" + \
                f"{date.year}&month={date.month}&day={date.day}"
        response = Request(function=requests.get, url=url).get_wrapper()
        if response.status_code != 200:
            return None

        suffix = None
        soup = BeautifulSoup(response.content, 'html.parser')
        for table in soup.find_all('table', attrs={'class': 'teams'}):
            for anchor in table.find_all('a'):
                if 'boxscores' in anchor.attrs['href'] and \
                    (team1 in anchor.attrs['href'] or team2 in anchor.attrs['href']):
                    suffix = anchor.attrs['href']
        return suffix

    def _nba_stats_add_possessions(
        self,
        _name,
        logs_df,
        team_dict,
        season_type
    ):

        total_poss = 0
        teams_list = [(year, opp_team) for year in team_dict for opp_team in team_dict[year]]
        for year, opp_team in tqdm(teams_list, desc="Loading player possessions...", ncols=75):
            opp_id = 1610612700 + int(constants.teams()[opp_team])
            url = 'https://stats.nba.com/stats/leaguedashplayerstats'
            per_poss_df = Request(url, opp_id=opp_id, year=self._format_year(year), \
                                  season_type=season_type).get_response()
            if per_poss_df.empty:
                break
            per_poss_df = per_poss_df.query('PLAYER_NAME == @_name')
            min_per_poss = per_poss_df.iloc[0]['MIN']
            filtered_logs = logs_df.query('SEASON == @year').query('MATCHUP == @opp_team')
            min_played = filtered_logs['MIN'].sum()
            poss = min_played / min_per_poss
            total_poss += round(poss)
        return total_poss
