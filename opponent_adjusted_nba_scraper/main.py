'''Example'''
try:
    from nba_stats.players import player_stats
    from utils.constants import Mode, SeasonType
except ModuleNotFoundError:
    from opponent_adjusted_nba_scraper.bball_ref.players import  player_stats
    from opponent_adjusted_nba_scraper.utils.constants import Mode, SeasonType

s = player_stats("Kobe Bryant", [2005, 2006], [90, 100], \
                 data_format=Mode.opp_pace_adj, season_type=SeasonType.default)
print(s)
