## Player Stats

Usage

```
from dans.endpoints.playerstats import PlayerStats
```

### `PlayerStats(name, year_range, drtg_range, data_format, season_type`

Parameters:
  - `name` - Player full name (e.g. `'Giannis Antetokounmpo'`)
  - `year_range (type: inclusive list)` - Range of years to search for logs (e.g. `[2019, 2021]`)
  - `drtg_range (type: exclusive list)` - Range of defensive strength in terms of Defensive Rating (e.g. `[107.5, 110]`)
  - `data_format` - One of `DataFormat.per_game` | `DataFormat.per_100_poss` | `DataFormat.opp_adj` | `DataFormat.pace_adj` | `DataFormat.opp_pace_adj` Default value is `DataFormat.per_game`
  - `season_type (type: SeasonType)` - One of `SeasonType.regular_season | SeasonType.playoffs`. Default value is `SeasonType.regular_season`

Returns:

  A Pandas Dataframe containing the player's basic averages, with the first three stats dependent on `data_format`:

  ```
  [points, rebounds, assists, true shooting percentage, relative true shooting percentage, opponent defensive rating]
  ```
  
## Player Logs

Usage

```
from dans.endpoints.playerlogs import PlayerLogs
```

### `PlayerLogs(name, year_range, season_type)`

Parameters:
  - `name (type: string)` - Player full name (e.g. `'Anthony Edwards'`)
  - `year_range (type: inclusive list)` - Range of years to search for logs (e.g. `[2020, 2024]`)
  - `season_type (type: SeasonType)` - One of `SeasonType.regular_season | SeasonType.playoffs`. Default value is `SeasonType.regular_season`

Returns:

  A Pandas Dataframe of the player's game logs in the seasons `year_range`, containing the following columns:

  ```
['SEASON', 'DATE', 'NAME', 'TEAM', 'HOME', 'MATCHUP', 'MIN', 'FG', 'FGA', 'FG%',
 '3P', '3PA', '3P%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK',
 'TOV', 'PF', 'PTS', '+/-',]
  ```

## Teams

Usage

```
from dans.endpoints.teams import Teams
```

### `Teams(year_range, drtg_range)`

Parameters:
  - `year_range (type: inclusive list)` Range of years to search for teams (e.g. `[1995, 2007]`)
  - `drtg_range (type: exclusive list)` - Range of defensive strength in terms of Defensive Rating (e.g. `[105, 110]`)

Returns:

  A Pandas Dataframe of every team in the seasons `year_range` with a defensive rating falling within `drtg_range` exclusive. The Dataframe contains the following columns:

  ```
  ['SEASON', 'TEAM', 'DRTG', 'OPP_TS']
  ```