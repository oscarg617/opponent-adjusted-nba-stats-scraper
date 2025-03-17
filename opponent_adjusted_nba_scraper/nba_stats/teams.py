'''Finding teams within a defensive rating range from stats.nba.com.'''
import sys
import pandas as pd

try:
    from nba_stats.utils import _format_year, _get_dataframe
    from nba_stats.request_constants import _team_advanced_params, _standard_header
    from utils.constants import _team_to_team_abbr, SeasonType
except ModuleNotFoundError:
    from opponent_adjusted_nba_scraper.nba_stats.utils import _format_year, _get_dataframe
    from opponent_adjusted_nba_scraper.nba_stats.request_constants import _team_advanced_params, \
        _standard_header
    from opponent_adjusted_nba_scraper.utils.constants import _team_to_team_abbr, SeasonType

def _teams_within_drtg(drtg_range: list, year_range: list, season_type=SeasonType.default):
    '''
    Returns a Pandas Dataframe of teams in a range of years within a range
    of defensive strength.
    '''

    assert len(drtg_range) == 2
    assert len(year_range) == 2
    assert drtg_range[0] <= drtg_range[1]
    assert year_range[0] <= year_range[1]
    if year_range[0] < 1971:
        sys.exit("Opponent data is not avaiable for teams before the 1970-71 season.")

    curr_year = year_range[0]
    dfs = []
    while curr_year <= year_range[1]:
        year = _format_year(curr_year)
        url = 'https://stats.nba.com/stats/leaguedashteamstats'
        params = _team_advanced_params('Advanced', 'PerGame', year, season_type)
        data_df = _get_dataframe(url, _standard_header(), params)
        if not data_df.empty:
            data_df = data_df.query('DEF_RATING < @drtg_range[0] and DEF_RATING >= @drtg_range[1]')\
                [['TEAM_NAME', 'DEF_RATING']]
            data_df['TEAM'] = data_df['TEAM_NAME'].str.upper().map(_team_to_team_abbr())
            data_df = data_df.drop('TEAM_NAME', axis=1)
            data_df['SEASON'] = curr_year
            params = _team_advanced_params('Opponent', 'Totals', year, season_type)
            ts_df = _get_dataframe(url, _standard_header(), params)
            ts_df = ts_df[['TEAM_NAME', 'OPP_PTS', 'OPP_FGA', 'OPP_FTA']]
            ts_df['TEAM'] = ts_df['TEAM_NAME'].str.upper().map(_team_to_team_abbr())
            ts_df = (ts_df.drop('TEAM_NAME', axis=1)
                .query('TEAM.isin(@data_df.TEAM.values.tolist())'))
            data_df['OPP_TS'] = (ts_df['OPP_PTS']) / \
                (2 * (ts_df['OPP_FGA'] + (0.44 * ts_df['OPP_FTA'])))
            dfs.append(data_df)
        curr_year += 1
    result = pd.concat(dfs)
    result = result.iloc[:,[2, 1, 0, 3]].reset_index(drop=True)
    result['OPP_TS'] = result['OPP_TS'].astype('float16')
    result = result.rename(columns={"DEF_RATING": "DRTG", "OPP_TS_PCT": "OPP_TS"})
    return result
