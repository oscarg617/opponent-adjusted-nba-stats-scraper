import pandas as pd
from requests import get
import time

try: 
    from utils import true_shooting_percentage, format_year, total_possessions, teams_df_to_dict
    from teams import teams_within_drtg, filter_teams_through_logs, filter_logs_through_teams
    import request_constants as rc
except:
    from opponent_adjusted_nba_scraper.utils import true_shooting_percentage, format_year, total_possessions, teams_df_to_dict
    from opponent_adjusted_nba_scraper.teams import teams_within_drtg, filter_teams_through_logs, filter_logs_through_teams
    import opponent_adjusted_nba_scraper.request_constants as rc

def player_game_logs(name, first_year, last_year, season_type="Playoffs"):
    curr_year = first_year
    frames = []
    while curr_year <= last_year:
        year = format_year(curr_year)
        url = 'https://stats.nba.com/stats/playergamelogs'
        response = get(url, headers=rc.STANDARD_HEADER, params=rc.player_logs_params(year, season_type), stream=True)
        time.sleep(.600)
        response_json = response.json()
        frame = pd.DataFrame(response_json['resultSets'][0]['rowSet'])
        frame.columns = response_json['resultSets'][0]['headers']
        frame = frame[frame['PLAYER_NAME'] == name]
        frame = frame[['SEASON_YEAR', 'PLAYER_NAME', 'TEAM_ABBREVIATION', 'TEAM_NAME', 'MATCHUP', 'WL', 'MIN', 'FGM', 'FGA', 'FG_PCT', 
        'FG3M', 'FG3A', 'FG3_PCT','FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'PTS']]
        def last_three_char(string):
            return string[-3:]
        ds = frame['MATCHUP'].apply(last_three_char)
        new_df = ds.to_frame()
        frame = frame.assign(MATCHUP=new_df['MATCHUP'])
        frame = frame[::-1]
        frames.append(frame)
        curr_year += 1
    result = pd.concat(frames)
    return result

def player_stats(name, first_year, last_year, min_drtg, max_drtg, data_format="OPP_ADJ", season_type="Playoffs", printStats=True):
    logs = player_game_logs(name, first_year, last_year, season_type)
    teams_df = teams_within_drtg(min_drtg, max_drtg, first_year, last_year, "Regular Season")
    teams_df = filter_teams_through_logs(logs, teams_df)
    teams_dict = teams_df_to_dict(teams_df)
    logs = filter_logs_through_teams(logs, teams_dict)
    opp_drtg_sum = 0
    opp_true_shooting_sum = 0
    for year in teams_dict:
        for opp_team in teams_dict[year]:
            logs_in_year = logs[logs['SEASON_YEAR'] == year]
            logs_vs_team = logs_in_year[logs_in_year['MATCHUP'] == opp_team]
            opp_drtg_sum += ((teams_df[teams_df['TEAM_ABBR'] == opp_team].DEF_RATING.values[0]) * logs_vs_team.shape[0])
            teams_in_year = teams_df[teams_df['SEASON_YEAR'] == year]
            opp_true_shooting_sum += ((teams_in_year[teams_in_year['TEAM_ABBR'] == opp_team].OPP_TS_PCT.values[0]) * logs_vs_team.shape[0])
    opp_drtg = round((opp_drtg_sum / logs.shape[0]), 1)
    opp_true_shooting = (opp_true_shooting_sum / logs.shape[0]) * 100
    player_true_shooting = true_shooting_percentage(logs.PTS.sum(), logs.FGA.sum(), logs.FTA.sum()) * 100
    relative_true_shooting = round(player_true_shooting - opp_true_shooting, 1)
    if data_format == 'PER_GAME':
        points = f"{round(logs['PTS'].mean(), 1)} points per game"
        rebounds = f"{round(logs['REB'].mean(), 1)} rebounds per game"
        assists = f"{round(logs['AST'].mean(), 1)} assists per game"
    elif data_format == 'PER_POSS':
        possessions = total_possessions(name, logs, teams_dict)
        points = f"{round((logs['PTS'].sum() / possessions) * 100, 1)} points per 100 possessions"
        rebounds = f"{round((logs['REB'].sum() / possessions) * 100, 1)} rebounds per 100 possessions"
        assists = f"{round((logs['AST'].sum() / possessions) * 100, 1)} assists per 100 possessions"
    elif data_format == 'OPP_ADJ':
        points = f"{round((logs['PTS'].mean() * (110 / opp_drtg)), 1)} opponent-adjusted points per game"
        rebounds = f"{round(logs['REB'].mean(), 1)} rebounds per game"
        assists = f"{round(logs['AST'].mean(), 1)} assists per game"
    elif data_format == 'OPP_INF':
        possessions = total_possessions(name, logs, teams_dict)
        points_per_100 = (logs['PTS'].sum() / possessions) * 100
        points = f"{round(((logs['MIN'].mean() / 48) * points_per_100 * (110 / opp_drtg)), 1)} opponent and inflation-adjusted points per game"
        rebounds = f"{round(logs['REB'].mean(), 1)} rebounds per game"
        assists = f"{round(logs['AST'].mean(), 1)} assists per game"
    if printStats:
        if first_year == last_year:
            print(f'In {first_year}, {name} averaged:')
        else:
            print(f'From {first_year} to {last_year}, {name} averaged:')
        print(points + "\n" + rebounds + '\n' + assists)
        if relative_true_shooting > 0:
            print(f'on {round(player_true_shooting, 1)} TS% (+{relative_true_shooting} rTS%)')
        else:
            print(f'on {round(player_true_shooting, 1)} TS% ({relative_true_shooting} rTS%)')
        print(f'Opponent DRTG: {opp_drtg}')
    return [points, rebounds, assists, player_true_shooting, relative_true_shooting, opp_drtg]
