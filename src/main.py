from bball_ref.br_players import player_game_logs
from utils.util import get_player_suffix
from utils.lookup import lookup
import time

name = "Bill Russell"
first_year = 1967
last_year = 1967
suffix = get_player_suffix(name)
name = lookup(name, ask_matches=False)
print(player_game_logs(name, first_year, last_year, season_type="Playoffs"))

from bball_ref.br_teams import teams_within_drtg as bball_teams
from nba_stats.ns_teams import teams_within_drtg as nba_teams

min_drtg = 100
max_drtg = 110
first_year = 2011
last_year = 2011

bball_start = time.time()
#print(bball_teams(min_drtg, max_drtg, first_year, last_year, season_type="Regular Season"))
bball_end = time.time()
nba_start = time.time()
#print(nba_teams(min_drtg, max_drtg, first_year, last_year, season_type="Regular Season"))
nba_end = time.time()

print("bball time: ", bball_end - bball_start)
print("nba_time: ", nba_end - nba_start)
