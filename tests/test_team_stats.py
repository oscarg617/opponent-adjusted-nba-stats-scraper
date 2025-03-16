'''Testing team methods.'''
import unittest

try:
    from bball_ref.teams import teams_within_drtg
    from bball_ref.players import player_game_logs
    from utils.util import _teams_df_to_dict, _filter_logs_through_teams, \
        _filter_teams_through_logs
except ModuleNotFoundError:
    from opponent_adjusted_nba_scraper.bball_ref.teams import teams_within_drtg
    from opponent_adjusted_nba_scraper.bball_ref.players import player_game_logs
    from opponent_adjusted_nba_scraper.utils.util import _teams_df_to_dict, \
        _filter_logs_through_teams, _filter_teams_through_logs

class TestTeamStats(unittest.TestCase):
    '''Tests for each method in opponent_adjusted_nba_scraper.bball_ref.players'''
    def _test_team_within_drtg(self):
        teams_df = teams_within_drtg(105, 110, 2019, 2022, season_type="Regular Season")
        self.assertEqual(teams_df.shape[0], 42)

        expected_columns = ['SEASON_YEAR', 'TEAM_ABBR', 'DEF_RATING', 'OPP_TS_PERCENT']
        self.assertListEqual(list(teams_df.columns), expected_columns)

    def _test_filter_logs_through_teams(self):
        teams_df = teams_within_drtg(105, 110, 2019, 2022, season_type="Regular Season")
        teams_dict = _teams_df_to_dict(teams_df)
        logs_df = player_game_logs("Jimmy Butler", 2019, 2022, season_type="Playoffs")

        logs_df = _filter_logs_through_teams(logs_df, teams_dict)
        self.assertEqual(logs_df.shape[0], 30)

    def _test_filter_teams_through_logs(self):
        teams_df = teams_within_drtg(105, 110, 2019, 2022, season_type="Regular Season")
        logs_df = player_game_logs("Jimmy Butler", 2019, 2022, season_type="Playoffs")

        teams_df = _filter_teams_through_logs(logs_df, teams_df)
        self.assertEqual(teams_df.shape[0], 5)

if __name__ == '__main__':
    unittest.main()
