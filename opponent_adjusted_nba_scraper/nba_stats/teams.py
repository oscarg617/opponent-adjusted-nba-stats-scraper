import pandas as pd

try:
    from nba_stats.utils import _format_year, _get_dataframe
    import nba_stats.request_constants as rc
    from utils.constants import _TEAM_TO_TEAM_ABBR
except:
    from opponent_adjusted_nba_scraper.nba_stats.utils import _format_year, _get_dataframe
    import opponent_adjusted_nba_scraper.nba_stats.request_constants as rc
    from opponent_adjusted_nba_scraper.utils.constants import _TEAM_TO_TEAM_ABBR

def _teams_within_drtg(min_drtg, max_drtg, first_year, last_year, season_type='Playoffs'):
    curr_year = first_year
    dfs = []
    while curr_year <= last_year:
        year = _format_year(curr_year)
        url = 'https://stats.nba.com/stats/leaguedashteamstats'
        params = rc.team_advanced_params('Advanced', 'PerGame', year, season_type)
        df = _get_dataframe(url, rc._STANDARD_HEADER, params)
        if not df.empty:
            df = df.query('DEF_RATING < @max_drtg and DEF_RATING >= @min_drtg')[['TEAM_NAME', 'DEF_RATING']]
            df['TEAM'] = df['TEAM_NAME'].str.upper().map(_TEAM_TO_TEAM_ABBR)
            df = df.drop('TEAM_NAME', axis=1)
            df['SEASON'] = curr_year
            params = rc.team_advanced_params('Opponent', 'Totals', year, season_type)
            ts_df = _get_dataframe(url, rc.STANDARD_HEADER, params)
            ts_df = ts_df[['TEAM_NAME', 'OPP_PTS', 'OPP_FGA', 'OPP_FTA']]
            ts_df['TEAM'] = ts_df['TEAM_NAME'].str.upper().map(_TEAM_TO_TEAM_ABBR)
            ts_df = (ts_df.drop('TEAM_NAME', axis=1)
                .query('TEAM.isin(@df.TEAM.values.tolist())'))
            df['OPP_TS'] = (ts_df['OPP_PTS']) / (2 * (ts_df['OPP_FGA'] + (0.44 * ts_df['OPP_FTA'])))
            dfs.append(df)
        curr_year += 1
    result = pd.concat(dfs)
    result = result.iloc[:,[2, 1, 0, 3]].reset_index(drop=True)
    result['OPP_TS'] = result['OPP_TS'].astype('float16')
    result = result.rename(columns={"DEF_RATING": "DRTG", "OPP_TS_PCT": "OPP_TS"})
    return result

