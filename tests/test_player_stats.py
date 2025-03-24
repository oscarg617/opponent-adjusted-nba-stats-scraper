'''Testing player methods.'''
import unittest

from opponent_adjusted_nba_scraper.endpoints.playerstats import PlayerStats
from opponent_adjusted_nba_scraper.endpoints.playerlogs import PlayerLogs
from opponent_adjusted_nba_scraper.library.arguments import Mode, SeasonType

class TestPlayerStats(unittest.TestCase):
    '''Tests for each method in opponent_adjusted_nba_scraper.bball_ref.players'''
    def test_player_game_logs(self):
        logs = PlayerLogs("Stephen Curry", [2015, 2017],
                          season_type=SeasonType.playoffs).bball_ref()
        self.assertEqual(logs['PTS'].sum(), 1523)
        expected_columns = ['SEASON', 'DATE', 'NAME', 'TEAM', 'HOME', 'MATCHUP', 'MIN', 'FG',
                            'FGA', 'FG%', '3P', '3PA', '3P%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB',
                            'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'GmSc', '+/-']
        self.assertListEqual(list(logs.columns), expected_columns)

    def test_player_stats(self):
        per_game_stats = PlayerStats("Kobe Bryant", [2003, 2003], [90, 100], Mode.default,
                                      SeasonType.playoffs).bball_ref()
        # per_poss_stats = PlayerStats("Kobe Bryant", [2001, 2003], [90, 100], Mode.per_100_poss,
        #                               SeasonType.playoffs).bball_ref()
        self.assertEqual(per_game_stats["points"], '32.3 points per game')
        # self.assertEqual(per_poss_stats["points"], '34.1 points per 100 possessions')

if __name__ == '__main__':
    unittest.main()
