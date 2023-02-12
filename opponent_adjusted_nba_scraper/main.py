from bball_ref.br_players import player_game_logs
from utils.util import get_player_suffix
from utils.lookup import lookup
from bball_ref.br_players import player_stats
from bball_ref.br_utils import add_possessions

name = "Stephen Curry"
first_year = 2015
last_year = 2015
min_drtg = 105
max_drtg = 110
steph = player_game_logs(name, first_year, last_year)
print(steph)
steph = add_possessions(name, steph, 3)
print(steph)


# player_stats(_name=name, first_year=first_year, last_year=last_year, min_drtg=min_drtg, max_drtg=max_drtg)

# name = "Bill Russell"
# first_year = 1967
# last_year = 1967
# suffix = get_player_suffix(name)
# name = lookup(name, ask_matches=False)
# print(player_game_logs(name, first_year, last_year, season_type="Playoffs"))

# min_drtg = 100
# max_drtg = 110
# first_year = 2011
# last_year = 2011

# bball_start = time.time()
# print(bball_teams(min_drtg, max_drtg, first_year, last_year, season_type="Regular Season"))
# bball_end = time.time()
# nba_start = time.time()
# print(nba_teams(min_drtg, max_drtg, first_year, last_year, season_type="Regular Season"))
# nba_end = time.time()

# print("bball time: ", bball_end - bball_start)
# print("nba_time: ", nba_end - nba_start)
