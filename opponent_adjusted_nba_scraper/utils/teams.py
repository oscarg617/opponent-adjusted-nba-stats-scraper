'''Finding teams within a defensive rating range from basketball reference.'''
import os
import pandas as pd
try:
    from utils.constants import Site
except ModuleNotFoundError:
    from opponent_adjusted_nba_scraper.utils.constants import Site

def teams_within_drtg(drtg_range: list, year_range: list, site: Site) -> pd.DataFrame:
    '''
    Returns a Pandas Dataframe of teams in a range of years within a range
    of defensive strength.
    '''
    if site == Site.basketball_reference:
        path = os.path.join(os.path.dirname(__file__), 'bball-ref-teams.csv')
    else:
        path = os.path.join(os.path.dirname(__file__), 'nba-stats-teams.csv')
    teams_df = pd.read_csv(path)
    teams_df = teams_df[
        (teams_df["SEASON"] >= year_range[0]) &
        (teams_df["SEASON"] <= year_range[1]) &
        (teams_df["DRTG"] >= drtg_range[0]) &
        (teams_df["DRTG"] <= drtg_range[1])]
    return teams_df
