'''Example'''
try:
    from nba_stats.players import player_stats
    from utils.constants import Mode, SeasonType
except ModuleNotFoundError:
    from opponent_adjusted_nba_scraper.nba_stats.players import  player_stats
    from opponent_adjusted_nba_scraper.utils.constants import Mode, SeasonType

s = player_stats("Kobe Bryant", [2001, 2001], [104, 110], \
                 data_format=Mode.default, season_type=SeasonType.playoffs)
print(s)
