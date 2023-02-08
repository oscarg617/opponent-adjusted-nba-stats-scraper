from src.nba_stats.ns_players import player_game_logs, player_stats

df = player_game_logs('LeBron James', 2012, 2014, season_type="Playoffs")
print(df)

stats_list = player_stats('Kawhi Leonard', 2019, 2021, 100, 110, data_format='PER_GAME', season_type='Playoffs', printStats=False)
print(stats_list)

stats_list = player_stats('Kevin Durant', 2017, 2019, 105, 110, data_format='OPP_INF', season_type='Playoffs', printStats=False)
print(stats_list)

from src.nba_stats.ns_teams import teams_within_drtg, filter_teams_through_logs, filter_logs_through_teams

teams_df = teams_within_drtg(90, 102, 2001, 2004, season_type="Regular Season")
print(teams_df)

logs_df = player_game_logs("Kevin Garnett", 2001, 2004)
filtered_teams_df = filter_teams_through_logs(logs_df, teams_df)
print(filtered_teams_df)

from src.utils.util import teams_df_to_dict

teams_dict = teams_df_to_dict(filtered_teams_df)
print(teams_dict)

filtered_logs_df = filter_logs_through_teams(logs_df, teams_dict)
print(filtered_logs_df)
