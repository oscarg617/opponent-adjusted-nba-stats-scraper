import unittest
from src.team_stats import teams_within_drtg, filter_logs_through_teams, filter_teams_through_logs
from src.player_stats import player_game_logs
from src.utils import teams_df_to_dict

class TestTeamStats(unittest.TestCase):
    def test_team_within_drtg(self):
        teams_df = teams_within_drtg(105, 110, 2019, 2022, season_type="Regular Season")
        self.assertEqual(teams_df.shape[0], 42)

        expected_columns = ['SEASON_YEAR', 'TEAM_ABBR', 'DEF_RATING', 'OPP_TS_PERCENT']
        self.assertListEqual(list(teams_df.columns), expected_columns)

    def test_filter_logs_through_teams(self):
        teams_df = teams_within_drtg(105, 110, 2019, 2022, season_type="Regular Season")
        teams_dict = teams_df_to_dict(teams_df)
        logs_df = player_game_logs("Jimmy Butler", 2019, 2022, season_type="Playoffs")

        logs_df = filter_logs_through_teams(logs_df, teams_dict)
        self.assertEqual(logs_df.shape[0], 30)

    def test_filter_teams_through_logs(self):
        teams_df = teams_within_drtg(105, 110, 2019, 2022, season_type="Regular Season")
        logs_df = player_game_logs("Jimmy Butler", 2019, 2022, season_type="Playoffs")

        teams_df = filter_teams_through_logs(logs_df, teams_df)
        self.assertEqual(teams_df.shape[0], 5)

if __name__ == '__main__':
    unittest.main()
