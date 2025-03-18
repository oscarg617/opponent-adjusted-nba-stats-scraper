'''Examples of usage.'''
try:
    from nba_stats.players import player_game_logs, player_stats
    from nba_stats.teams import teams_within_drtg
    from utils.constants import Mode, SeasonType
except ModuleNotFoundError:
    from opponent_adjusted_nba_scraper.nba_stats.players import player_game_logs, player_stats
    from opponent_adjusted_nba_scraper.nba_stats.teams import teams_within_drtg
    from opponent_adjusted_nba_scraper.constants import Mode, SeasonType

df = player_game_logs('LeBron James', [2012, 2014], season_type=SeasonType.playoffs)
print(df)

stats_list = player_stats('Kawhi Leonard', [2019, 2021], [100, 110], \
                          data_format=Mode.default, season_type=SeasonType.playoffs)
print(stats_list)

stats_list = player_stats('Kevin Durant', [2017, 2019], [105, 110], \
                          data_format=Mode.opp_pace_adj,season_type=SeasonType.playoffs)
print(stats_list)

teams_df = teams_within_drtg([90, 102], [2001, 2004], season_type=SeasonType.default)
print(teams_df)
