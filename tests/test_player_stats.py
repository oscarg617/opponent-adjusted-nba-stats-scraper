'''Testing player methods.'''
import unittest

from ..opponent_adjusted_nba_scraper.players import player_game_logs, player_stats
from ..opponent_adjusted_nba_scraper.library.constants import Mode, SeasonType

class TestPlayerStats(unittest.TestCase):
    '''Tests for each method in opponent_adjusted_nba_scraper.bball_ref.players'''
    def _test_player_game_logs(self):
        logs = player_game_logs("Stephen Curry", [2015, 2017], season_type=SeasonType.playoffs)
        self.assertEqual(logs['PTS'].sum(), 1523)

        expected_columns = ['SEASON_YEAR', 'PLAYER_NAME', 'TEAM_ABBREVIATION', 'TEAM_NAME',
                            'MATCHUP', 'WL', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A',
                            'FG3_PCT','FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST',
                            'TOV', 'STL', 'BLK', 'PTS']
        self.assertListEqual(list(logs.columns), expected_columns)

    def _test_player_stats(self):
        per_game_stats = player_stats("Kobe Bryant", [2003, 2003], [90, 100], Mode.default,
                                      SeasonType.playoffs)
        per_poss_stats = player_stats("Kobe Bryant", [2001, 2003], [90, 100], Mode.per_100_poss,
                                      SeasonType.playoffs)
        self.assertEqual(per_game_stats[0], '32.3 points per game')
        self.assertEqual(per_poss_stats[0], '34.1 points per 100 possessions')

if __name__ == '__main__':
    unittest.main()
