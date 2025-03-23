'''Testing team methods.'''
import unittest

from ..opponent_adjusted_nba_scraper.teams import teams_within_drtg
from ..opponent_adjusted_nba_scraper.players import player_game_logs
from ..opponent_adjusted_nba_scraper.util import _teams_df_to_dict, \
    _filter_logs_through_teams, _filter_teams_through_logs
from ..opponent_adjusted_nba_scraper.library.constants import SeasonType

class TestTeamStats(unittest.TestCase):
    '''Tests for each method in opponent_adjusted_nba_scraper.bball_ref.players'''
    def _test_team_within_drtg(self):
        teams_df = teams_within_drtg([105, 110], [2019, 2022], SeasonType.default)
        self.assertEqual(teams_df.shape[0], 42)

        expected_columns = ['SEASON_YEAR', 'TEAM_ABBR', 'DEF_RATING', 'OPP_TS_PERCENT']
        self.assertListEqual(list(teams_df.columns), expected_columns)

    def _test_filter_logs_through_teams(self):
        teams_df = teams_within_drtg([105, 110], [2019, 2022], SeasonType.default)
        teams_dict = _teams_df_to_dict(teams_df)
        logs_df = player_game_logs("Jimmy Butler", [2019, 2022], SeasonType.playoffs)

        logs_df = _filter_logs_through_teams(logs_df, teams_dict)
        self.assertEqual(logs_df.shape[0], 30)

    def _test_filter_teams_through_logs(self):
        teams_df = teams_within_drtg([105, 110], [2019, 2022], SeasonType.default)
        logs_df = player_game_logs("Jimmy Butler", [2019, 2022], SeasonType.playoffs)

        teams_df = _filter_teams_through_logs(logs_df, teams_df)
        self.assertEqual(teams_df.shape[0], 5)

if __name__ == '__main__':
    unittest.main()
