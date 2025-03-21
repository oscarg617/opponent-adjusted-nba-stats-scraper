'''Finding teams within a defensive rating range from basketball reference.'''
import os
import pandas as pd
from tqdm import tqdm

try:
    from bball_ref_utils import _bball_ref_get_dataframe
    from constants import _team_to_team_abbr
    from nba_stats_request_constants import _team_advanced_params, _standard_header
    from nba_stats_utils import _format_year, _nba_stats_get_dataframe
    from parameters import SeasonType, Site
    from util import _check_drtg_and_year_ranges
except ModuleNotFoundError:
    from opponent_adjusted_nba_scraper.bball_ref_utils import _bball_ref_get_dataframe
    from opponent_adjusted_nba_scraper.constants import _team_to_team_abbr
    from opponent_adjusted_nba_scraper.nba_stats_request_constants import _team_advanced_params, \
        _standard_header
    from opponent_adjusted_nba_scraper.nba_stats_utils import _format_year, \
        _nba_stats_get_dataframe
    from opponent_adjusted_nba_scraper.parameters import SeasonType, Site
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

def _bball_ref_teams_within_drtg(year_range, drtg_range, season_type=SeasonType.default) \
    -> pd.DataFrame:

    # Setup
    _check_drtg_and_year_ranges(year_range, drtg_range, Site.basketball_reference)
    dfs = []
    for curr in tqdm(range(year_range[0], year_range[1] + 1),
                     desc="Loading opponents' stats...", ncols=75):

        # URL
        if season_type == "Regular Season":
            url = f'https://www.basketball-reference.com/leagues/NBA_{curr}.html'
        else:
            url = f'https://www.basketball-reference.com/playoffs/NBA_{curr}.html'

        # True Shooting
        opponent_totals_df = _bball_ref_get_dataframe(url, "totals-opponent")\
            [["Team", "FGA", "FTA", "PTS"]]\
            .replace(r'\*','',regex=True).astype(str)\
            .sort_values(by="Team", ascending=True, ignore_index=True)\
            .astype({
                'Team': 'string',
                'FGA': 'int32',
                'FTA': 'int32',
                'PTS': 'int32'
            })
        opponent_totals_df["OPP_TS"] = opponent_totals_df["PTS"] / \
            (2 * (opponent_totals_df["FGA"] + (0.44 * opponent_totals_df["FTA"])))

        # DRTG
        team_advanced_df = _bball_ref_get_dataframe(url, "advanced-team")\
            [["Team", "DRtg"]]\
            .rename(columns={"Team": "TEAM", "DRtg": "DRTG"})\
            .replace(r'\*','',regex=True).astype(str)\
            .sort_values(by="TEAM", ascending=True, ignore_index=True)\
            .astype({'TEAM': 'string', 'DRTG': 'float64'})
        team_advanced_df["TEAM"] = team_advanced_df["TEAM"]\
            .str.upper()\
            .map(_team_to_team_abbr(Site.basketball_reference))
        team_advanced_df["OPP_TS"] = opponent_totals_df['OPP_TS'].copy()

        # Filter
        team_advanced_df = team_advanced_df\
            .query("DRTG >= @drtg_range[0] and DRTG < @drtg_range[1]")
        team_advanced_df["SEASON"] = curr
        dfs.append(team_advanced_df)
    result = pd.concat(dfs)
    result = result.reset_index(drop=True)
    result.index += 1
    return result.iloc[:,[3, 0, 1, 2]]

def _nba_stats_teams_within_drtg(year_range: list, drtg_range: list, \
                                 season_type=SeasonType.default):

    # Setup
    _check_drtg_and_year_ranges(year_range, drtg_range, Site.basketball_reference)
    dfs = []
    for curr in tqdm(range(year_range[0], year_range[1] + 1), \
                     desc="Loading opponents' stats...", ncols=75):

        # URL
        year = _format_year(curr)
        url = 'https://stats.nba.com/stats/leaguedashteamstats'

        # True shooting
        params = _team_advanced_params('Opponent', 'Totals', year, season_type)
        opponent_totals_df = _nba_stats_get_dataframe(url, _standard_header(), params)\
            [['TEAM_NAME', 'OPP_PTS', 'OPP_FGA', 'OPP_FTA']]\
            .sort_values(by="TEAM_NAME", ascending=True, ignore_index=True)\
            .astype({
                'TEAM_NAME': 'string',
                'OPP_FGA': 'int32',
                'OPP_FTA': 'int32',
                'OPP_PTS': 'int32'
            })
        opponent_totals_df['OPP_TS'] = (opponent_totals_df['OPP_PTS']) / \
            (2 * (opponent_totals_df['OPP_FGA'] + (0.44 * opponent_totals_df['OPP_FTA'])))

        # DRTG
        params = _team_advanced_params('Advanced', 'PerGame', year, season_type)
        team_advanced_df = _nba_stats_get_dataframe(url, _standard_header(), params)\
            [['TEAM_NAME', 'DEF_RATING']]\
            .rename(columns={"TEAM_NAME": "TEAM", "DEF_RATING": "DRTG"})\
            .sort_values(by="TEAM", ascending=True, ignore_index=True)\
            .astype({'TEAM': 'string', 'DRTG': 'float64'})
        team_advanced_df['TEAM'] = team_advanced_df['TEAM']\
            .str.upper()\
            .map(_team_to_team_abbr(Site.nba_stats))
        team_advanced_df["OPP_TS"] = opponent_totals_df['OPP_TS'].copy()

        # Filter
        team_advanced_df = team_advanced_df\
            .query('DRTG >= @drtg_range[0] and DRTG < @drtg_range[1]')
        team_advanced_df['SEASON'] = curr
        dfs.append(team_advanced_df)
    result = pd.concat(dfs)
    result = result.reset_index(drop=True)
    result.index += 1
    result = result.iloc[:,[3, 0, 1, 2]]
    return result
