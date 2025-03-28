'''Constants.'''
from dans.library.arguments import Site

def teams() -> dict:
    '''Offset for each team in determining team id for nba-stats'''
    return {"ATL":'37', "BOS":'38', "BKN":'51', "CHA":'66', "CHI":'41', "CLE":'39', "DAL":'42',
            "DEN":'43', "DET":'65', "GSW":'44', "HOU":'45', "IND":'54', "LAC":'46', "LAL":'47',
            "MEM":'63', "MIA":'48', "MIL":'49', "MIN":'50', "NOP":'40', "NYK":'52', "OKC":'60',
            "ORL":'53', "PHI":'55', "PHX":'56', "POR":'57', "SAC":'58', "SAS":'59', "TOR":'61',
            "UTA":'62', "WAS":'64', "NJN":"51", "CHO":"66", "VAN":"63", "NOH":"40", "SEA":"60",
            "NOK":'40'}

def team_to_team_abbr(site=Site.default) -> dict:
    '''Dictionary for mapping teams to tricodes'''
    if site == Site.basketball_reference:
        phoenix_suns = "PHO"
    else:
        phoenix_suns = "PHX"

    return {
        'ATLANTA HAWKS': 'ATL',
        'BOSTON CELTICS': 'BOS',
        'BALTIMORE BULLETS': 'BAL',
        'BROOKLYN NETS': 'BKN',
        'BUFFALO BRAVES': 'BUL',
        'NEW JERSEY NETS' : 'NJN',
        'CAPITAL BULLETS': 'CAP',
        'CINCINNATI ROYALS': 'CIN',
        'CHICAGO BULLS': 'CHI',
        'CHARLOTTE HORNETS': 'CHO',
        'CHARLOTTE BOBCATS' : 'CHA',
        'CLEVELAND CAVALIERS': 'CLE',
        'DALLAS MAVERICKS': 'DAL',
        'DENVER NUGGETS': 'DEN',
        'DETROIT PISTONS': 'DET',
        'GOLDEN STATE WARRIORS': 'GSW',
        'HOUSTON ROCKETS': 'HOU',
        'INDIANA PACERS': 'IND',
        'LOS ANGELES CLIPPERS': 'LAC',
        'LA CLIPPERS': 'LAC',
        'LOS ANGELES LAKERS': 'LAL',
        'LA LAKERS': 'LAL',
        'KANSAS CITY KINGS': 'KCK',
        'KANSAS CITY-OHAMA KINGS': 'KCO',
        'MEMPHIS GRIZZLIES': 'MEM',
        'MIAMI HEAT': 'MIA',
        'MILWAUKEE BUCKS': 'MIL',
        'MINNESOTA TIMBERWOLVES': 'MIN',
        'NEW ORLEANS PELICANS' : 'NOP',
        'NEW ORLEANS HORNETS' : 'NOH',
        'NEW ORLEANS/OKLAHOMA CITY HORNETS': 'NOK',
        'NEW YORK KNICKS' : 'NYK',
        'NEW YORK NETS': 'NYN',
        'OKLAHOMA CITY THUNDER' : 'OKC',
        'SAN DIEGO CLIPPERS': 'SDC',
        'SAN DIEGO ROCKETS': 'SDR',
        'SAN FRANCISCO WARRIORS': 'SFW',
        'SEATTLE SUPERSONICS' : 'SEA',
        'ORLANDO MAGIC' : 'ORL',
        'PHILADELPHIA 76ERS' : 'PHI',
        'PHOENIX SUNS' : phoenix_suns,
        'PORTLAND TRAIL BLAZERS' : 'POR',
        'SACRAMENTO KINGS' : 'SAC',
        'SAN ANTONIO SPURS' : 'SAS',
        'TORONTO RAPTORS' : 'TOR',
        'UTAH JAZZ' : 'UTA',
        'NEW ORLEANS JAZZ' : 'NOJ',
        'VANCOUVER GRIZZLIES': 'VAN',
        'WASHINGTON BULLETS': 'WSB',
        'WASHINGTON WIZARDS' : 'WAS',
    }
