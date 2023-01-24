## Teams

Usage

```
from opponent_adjusted_nba_scraper.teams import teams_within_drtg, filter_teams_through_logs, filter_logs_through_teams
```

### `teams_within_drtg(min_drtg, max_drtg, first_year, last_year, season_type='Playoffs')`

Parameters:
  - `min_drtg` - Minimum opponent defensive-rating (e.g. `95`, `105`)
  - `max_drtg` - Maximum opponent defensive-rating (e.g. `105`, `115`)
  - `first_year` - Desired end year of first season (e.g. `1998`, `2012`)
  - `last_year` - Desired end year of last season (e.g. `2004`, `2019`)
  - `season_type` - One of `'Regular Season'|'Playoffs'`. Default value is `'Playoffs'`

Returns:

  A Pandas Dataframe of every team from `first_year` to `last_year` with a defensive rating between `min_drtg` and `max_drtg`, containing the following columns:

  ```
  ['SEASON_YEAR', 'TEAM_ABBR', 'DEF_RATING', 'OPP_TS_PCT']
  ```

## Players

Usage

```
from basketball_reference_scraper.players import player_game_logs, player_stats
```

### `player_game_logs(name, first_year, last_year, season_type='Playoffs')`

Parameters:
  - `name` - Player full name (e.g. `'Anthony Edwards'`)
  - `first_year` - Desired end year of first season (e.g. `2007`, `2020`)
  - `last_year` - Desired end year of last season (e.g. `2003`, `2015`)
  - `season_type` - One of `'Regular Season'|'Playoffs'`. Default value is `'Playoffs'`

Returns:

  A Pandas Dataframe of the player's game logs from `first_year` to `last_year` against teams with a defensive rating between `min_drtg` and `max_drtg`, containing the following columns:

  ```
  ['SEASON_YEAR', 'PLAYER_NAME', 'TEAM_ABBREVIATION', 'TEAM_NAME', 'MATCHUP', 'WL', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT','FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'PTS']
  ```

### `player_stats(name, first_year, last_year, min_drtg, max_drtg, data_format="OPP_INF", season_type="Playoffs", printStats=True)`

Parameters:
  - `name` - Player full name (e.g. `'Giannis Antetokounmpo'`)
  - `first_year` - Desired end year of first season (e.g. `2007`, `2020`)
  - `last_year` - Desired end year of last season (e.g. `2003`, `2015`)
  - `min_drtg` - Minimum opponent defensive-rating (e.g. `95`, `105`)
  - `max_drtg` - Maximum opponent defensive-rating (e.g. `105`, `115`)
  - `data_format` - One of `'PER_GAME'|'PER_POSS'|'OPP_ADJ'|'OPP_INF'`. `'OPP_ADJ'`: opponent-adjusted per game; `'OPP_INF'`: opponent and inflation-adjusted per game. Default value is `'OPP_INF'`
  - `season_type` - One of `'Regular Season'|'Playoffs'`. Default value is `'Playoffs'`
  - `printStats` - One of `True|False`. Default value is `True`

Returns:

  A list containing the player's stats, with the first three stats dependent on `data_format`:

  ```
  [points, rebounds, assists, true shooting percentage, relative true shooting percentage, opponent defensive rating]
  ```
  