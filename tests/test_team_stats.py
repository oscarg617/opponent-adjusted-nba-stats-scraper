'''Testing team methods.'''
import unittest

from opponent_adjusted_nba_scraper.endpoints.teams import Teams
from opponent_adjusted_nba_scraper.library.arguments import SeasonType

class TestTeamStats(unittest.TestCase):
    '''Tests for each method in opponent_adjusted_nba_scraper.bball_ref.players'''
    def test_team_within_drtg(self):
        teams_df = Teams([2019, 2022], [105, 110]).bball_ref()
        self.assertEqual(teams_df.shape[0], 38)

        expected_columns = ['SEASON', 'TEAM', 'DRTG', 'OPP_TS']
        self.assertListEqual(list(teams_df.columns), expected_columns)


if __name__ == '__main__':
    unittest.main()
