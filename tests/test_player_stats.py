import unittest
from src.player_stats import player_game_logs, player_stats

class TestPlayerStats(unittest.TestCase):
    def test_player_game_logs(self):
        df = player_game_logs("Stephen Curry", 2015, 2017, season_type="Playoffs")
        self.assertEqual(df['PTS'].sum(), 1523)

        expected_columns = ['SEASON_YEAR', 'PLAYER_NAME', 'TEAM_ABBREVIATION', 'TEAM_NAME', 'MATCHUP', 'WL', 'MIN', 'FGM', 'FGA', 
        'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT','FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'PTS']
        self.assertListEqual(list(df.columns), expected_columns)

    def test_print_stats(self):
        per_game_stats = player_stats("Kobe Bryant", 2003, 2003, 90, 100, per_mode="PER_GAME", season_type="Playoffs", printStats=False)
        per_poss_stats = player_stats("Kobe Bryant", 2001, 2003, 90, 100, per_mode="PER_POSS", season_type="Playoffs", printStats=False)
        self.assertEqual(per_game_stats[0], '32.3 points per game')
        self.assertEqual(per_poss_stats[0], '34.1 points per 100 possessions')

if __name__ == '__main__':
    unittest.main()
