'''Dataclasses used for parameters.'''
from dataclasses import dataclass

@dataclass
class DataFormat:
    '''
    Class for choosing stat modes.
    '''

    per_game = "PerGame"
    per_100_poss = "Per100Poss"
    pace_adj = "PaceAdjusted"
    opp_adj = "OpponentAdjusted"
    opp_pace_adj = "OpponentAndPaceAdjusted"

    default = per_game

@dataclass
class SeasonType:
    '''
    Class for choosing season types.
    '''

    regular_season = "Regular Season"
    playoffs = "Playoffs"

    default = regular_season

@dataclass
class Site:
    '''
    Class for choosing site to collect data from.
    '''

    basketball_reference = "Basketball Reference"
    nba_stats = "NBA Stats"

    default = basketball_reference
