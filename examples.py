'''Examples of usage.'''

from dans.endpoints.playerlogs import PlayerLogs
from dans.endpoints.playerstats import PlayerStats
from dans.endpoints.teams import Teams
from dans.library.arguments import DataFormat, SeasonType

logs_df = PlayerLogs('LeBron James', [2012, 2014], season_type=SeasonType.playoffs).bball_ref()
print(logs_df)

stats_list = PlayerStats('Kawhi Leonard', [2019, 2021], [100, 110], \
                            season_type=SeasonType.playoffs).nba_stats()
print(stats_list)

stats_list = PlayerStats('Kevin Durant', [2017, 2019], [105, 110], data_format=\
                         DataFormat.opp_pace_adj, season_type=SeasonType.playoffs).nba_stats()
print(stats_list)

teams_df = Teams([2010, 2020], [105, 110]).bball_ref()
print(teams_df)
