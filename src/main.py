from bball_ref.br_players import player_game_logs
import re

name = "Kendrick Perkins"
first_year = 2013
last_year = 2013
print(player_game_logs(name, first_year, last_year, season_type="Playoffs"))

from nba_stats.ns_players import player_game_logs as nba_games_logs

#print(nba_games_logs(name, first_year, last_year, season_type="Playoffs"))