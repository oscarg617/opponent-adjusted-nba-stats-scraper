'''Finding teams within a defensive rating range from basketball reference.'''
import pandas as pd
from tqdm import tqdm
try:
    from utils.constants import _team_to_team_abbr
    from bball_ref.utils import _get_dataframe
except ModuleNotFoundError:
    from opponent_adjusted_nba_scraper.utils.constants import _team_to_team_abbr
    from opponent_adjusted_nba_scraper.bball_ref.utils import _get_dataframe

def teams_within_drtg(_drtg_range, year_range, season_type='Regular Season'):
    '''
    Returns a Pandas Dataframe of teams in a range of years within a range
    of defensive strength.
    '''
    dfs = []
    for curr in tqdm(range(year_range[0], year_range[1] + 1),
                     desc="Loading opponents' stats...", ncols=75):
        if season_type == "Regular Season":
            url = f'https://www.basketball-reference.com/leagues/NBA_{curr}.html'
        else:
            url = f'https://www.basketball-reference.com/playoffs/NBA_{curr}.html'
        true_shooting = _get_dataframe(url, "totals-opponent")
        data_pd = _get_dataframe(url, "advanced-team")
        true_shooting = true_shooting[["Team", "FGA", "FTA", "PTS"]]
        data_pd = data_pd[["Team", "DRtg"]]
        data_pd = data_pd.rename(columns={"Team": "TEAM", "DRtg": "DRTG"})
        true_shooting = true_shooting.astype({
            'Team': 'string',
            'FGA': 'int32',
            'FTA': 'int32',
            'PTS': 'int32'})
        data_pd = data_pd.astype({'TEAM': 'string', 'DRTG': 'float64'})
        data_pd["OPP_TS"] = true_shooting["PTS"] / \
            (2 * (true_shooting["FGA"] + (0.44 * true_shooting["FTA"])))
        data_pd = data_pd.query("DRTG >= @_drtg_range[0] and DRTG < @_drtg_range[1]")
        pd.options.mode.chained_assignment = None
        data_pd = data_pd.replace(r'\*','',regex=True).astype(str)
        data_pd = data_pd[(data_pd["TEAM"].str.contains("League Average") is False)]
        data_pd["TEAM"] = data_pd["TEAM"].str.upper().map(_team_to_team_abbr())
        data_pd["SEASON"] = curr
        dfs.append(data_pd)
    result = pd.concat(dfs)
    result = result.reset_index(drop=True)
    result.index += 1
    return result.iloc[:,[3, 0, 1, 2]]
