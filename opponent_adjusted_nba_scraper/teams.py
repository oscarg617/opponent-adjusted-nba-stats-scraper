'''Finding teams within a defensive rating range from basketball reference.'''
import os
import time
import pandas as pd
from tqdm import tqdm

try:
    from bball_ref_utils import _bball_ref_get_dataframe
    from constants import _team_to_team_abbr, SeasonType, Site
    from nba_stats_request_constants import _team_advanced_params, _standard_header
    from nba_stats_utils import _format_year, _nba_stats_get_dataframe
    from util import _check_drtg_and_year_ranges
except ModuleNotFoundError:
    from opponent_adjusted_nba_scraper.bball_ref_utils import _bball_ref_get_dataframe
    from opponent_adjusted_nba_scraper.constants import _team_to_team_abbr, SeasonType, Site
    from opponent_adjusted_nba_scraper.nba_stats_request_constants import _team_advanced_params, \
        _standard_header
    from opponent_adjusted_nba_scraper.nba_stats_utils import _format_year, \
        _nba_stats_get_dataframe
    from opponent_adjusted_nba_scraper.util import _check_drtg_and_year_ranges

def teams_within_drtg(year_range: list, drtg_range: list, site=Site.default) -> pd.DataFrame:
    '''
    Returns a Pandas Dataframe of teams in a range of years within a range
    of defensive strength.
    '''

    _check_drtg_and_year_ranges(year_range, drtg_range, site)

    if site == Site.basketball_reference:
        path = os.path.join(os.path.dirname(__file__), 'data/bball-ref-teams.csv')
    else:
        path = os.path.join(os.path.dirname(__file__), 'data/nba-stats-teams.csv')
    teams_df = pd.read_csv(path)
    teams_df = teams_df[
        (teams_df["SEASON"] >= year_range[0]) &
        (teams_df["SEASON"] <= year_range[1]) &
        (teams_df["DRTG"] >= drtg_range[0]) &
        (teams_df["DRTG"] <= drtg_range[1])]

    return teams_df

def _bball_ref_teams_within_drtg(year_range, drtg_range, season_type: SeasonType) -> pd.DataFrame:

    _check_drtg_and_year_ranges(year_range, drtg_range, Site.basketball_reference)

    dfs = []
    for curr in tqdm(range(year_range[0], year_range[1] + 1),
                     desc="Loading opponents' stats...", ncols=75):
        if season_type == "Regular Season":
            url = f'https://www.basketball-reference.com/leagues/NBA_{curr}.html'
        else:
            url = f'https://www.basketball-reference.com/playoffs/NBA_{curr}.html'
        true_shooting = _bball_ref_get_dataframe(url, "totals-opponent")
        data_pd = _bball_ref_get_dataframe(url, "advanced-team")
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
        data_pd = data_pd.query("DRTG >= @drtg_range[0] and DRTG < @drtg_range[1]")
        pd.options.mode.chained_assignment = None
        data_pd = data_pd.replace(r'\*','',regex=True).astype(str)
        data_pd = data_pd[~(data_pd["TEAM"].str.contains("League Average"))]
        data_pd["TEAM"] = data_pd["TEAM"].str.upper().map(_team_to_team_abbr())
        data_pd["SEASON"] = curr
        dfs.append(data_pd)
        time.sleep(21)
    result = pd.concat(dfs)
    result = result.reset_index(drop=True)
    result.index += 1
    return result.iloc[:,[3, 0, 1, 2]]

def _nba_stats_teams_within_drtg(year_range: list, drtg_range: list, \
                                 season_type=SeasonType.default):
    '''
    Returns a Pandas Dataframe of teams in a range of years within a range
    of defensive strength.
    '''
    _check_drtg_and_year_ranges(year_range, drtg_range, Site.basketball_reference)

    dfs = []
    for curr in tqdm(range(year_range[0], year_range[1] + 1), \
                     desc="Loading opponents' stats...", ncols=75):
        year = _format_year(curr)
        url = 'https://stats.nba.com/stats/leaguedashteamstats'
        params = _team_advanced_params('Advanced', 'PerGame', year, season_type)
        data_df = _nba_stats_get_dataframe(url, _standard_header(), params)
        if not data_df.empty:
            data_df = data_df.query('DEF_RATING >= @drtg_range[0] and ' + \
                                    'DEF_RATING < @drtg_range[1]')[['TEAM_NAME', 'DEF_RATING']]
            data_df['TEAM'] = data_df['TEAM_NAME'].str.upper().map(_team_to_team_abbr())
            data_df = data_df.drop('TEAM_NAME', axis=1)
            data_df['SEASON'] = curr
            params = _team_advanced_params('Opponent', 'Totals', year, season_type)
            ts_df = _nba_stats_get_dataframe(url, _standard_header(), params)
            ts_df = ts_df[['TEAM_NAME', 'OPP_PTS', 'OPP_FGA', 'OPP_FTA']]
            ts_df['TEAM'] = ts_df['TEAM_NAME'].str.upper().map(_team_to_team_abbr())
            ts_df = (ts_df.drop('TEAM_NAME', axis=1)
                .query('TEAM.isin(@data_df.TEAM.values.tolist())'))
            data_df['OPP_TS'] = (ts_df['OPP_PTS']) / \
                (2 * (ts_df['OPP_FGA'] + (0.44 * ts_df['OPP_FTA'])))
            dfs.append(data_df)
    result = pd.concat(dfs)
    result = result.iloc[:,[2, 1, 0, 3]].reset_index(drop=True)
    result['OPP_TS'] = result['OPP_TS'].astype('float16')
    result = result.rename(columns={"DEF_RATING": "DRTG", "OPP_TS_PCT": "OPP_TS"})
    return result
