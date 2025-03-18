'''Example'''
import pandas as pd

try:
    from players import player_stats
    from teams import teams_within_drtg
    from constants import Mode, SeasonType
except ModuleNotFoundError:
    from opponent_adjusted_nba_scraper.players import  player_stats
    from opponent_adjusted_nba_scraper.teams import teams_within_drtg
    from opponent_adjusted_nba_scraper.constants import Mode, SeasonType

s = player_stats("Kobe Bryant", [2007, 2007], [90, 120], \
                 data_format=Mode.default, season_type=SeasonType.default)
print(s)

df = pd.DataFrame()
df = pd.concat([df, teams_within_drtg([1997, 1997], [0, 2000])])
print(df)
