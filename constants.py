BOXSCORES_ENDPOINT = "https://stats.nba.com/stats/leaguegamelog?Counter=1000&DateFrom=%s&DateTo=&Direction=ASC&LeagueID=00&PlayerOrTeam=%s&Season=ALLTIME&SeasonType=%s&Sorter=DATE"
PBP_ENDPOINT = 'https://stats.nba.com/stats/playbyplayv2?GameId=%s&StartPeriod=0&EndPeriod=14'
ODDS_ENDPOINT = "https://www.sportsoddshistory.com/nba-main/?y=%s&sa=nba&a=finals&o=r"
PLAYERS_INDEX_ENDPOINT = 'https://stats.nba.com/stats/playerindex?Historical=1&LeagueID=00&Season=%s&SeasonType=Regular+Season'
TEAM_ROSTER_ENDPOINT = 'https://stats.nba.com/stats/commonteamroster?LeagueID=00&Season=%s&TeamID=%s'
PLAYER_PROFILE_ENDPOINT = 'http://stats.nba.com/stats/commonplayerinfo/?playerId=%s'
PLAYER_AWARDS_ENDPOINT = 'https://stats.nba.com/stats/playerawards?PlayerID=%s'
TEAM_DETAILS_ENDPOINT = 'http://stats.nba.com/stats/teamdetails/?teamId=%s'
BREF_SEASON_STATS_ENDPOINT = 'https://www.basketball-reference.com/leagues/%s_%s_per_game.html'
BREF_DRAFT_ENDPOINT = 'https://www.basketball-reference.com/draft/%s_%s.html'
BREF_STARTERS_ENDPOINT = 'https://www.basketball-reference.com/teams/%s/%s_start.html'
STATS_HEADERS = {
    'Host': 'stats.nba.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'x-nba-stats-origin': 'stats',
    'x-nba-stats-token': 'true',
    'Connection': 'keep-alive',
    'Referer': 'https://stats.nba.com/',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache'}
SEASON_TYPES = [
    {
        'name': "Regular+Season",
        'code': 2
    },
    {
        'name': "All+Star",
        'code': 3
    },
    {
        'name': "Playoffs",
        'code': 4
    },
    {
        'name': "PlayIn",
        'code': 5
    },
]
ODDS_TYPES = [
    "Round 1",
    "ConfSemis",
    "ConfFinals",
    "Finals"
]
DATABASE_PATH = 'Database/'
CACHE_PATH = 'quick_cache/'
DATABASE_NAME = "boxscores_full_database"
API_COUNT_THRESHOLD = 30000
LAST_SEASON = 2021
FIRST_ODDS_SEASON = 1972
BOXSCORE_FILE_TEMPLATE = "boxscore_%s_%s_%s.json"
PBP_FILE_TEMPLATE = "pbp_%s.json"
ODDS_FILE_TEMPLATE = "odds_%s.html"
PLAYOFF_PAGE_FILE_TEMPLATE = "playoff_summery_%s.html"
PLAYERS_INDEX_FILE_TEMPLATE = "players_index_%s.json"
TEAM_ROSTER_FILE_TEMPLATE = 'team_roster_%s_%s.json'
PLAYER_PROFILE_FILE_TEMPLATE = 'player_profile_%s.json'
PLAYER_AWARDS_FILE_TEMPLATE = 'player_awards_%s.json'
TEAM_DETAILS_FILE_TEMPLATE = 'team_details_%s.json'
BREF_SEASON_STATS_FILE_TEMPLATE = 'bref_stats_%s_%s.html'
BREF_DRAFT_FILE_TEMPLATE = 'bref_draft_%s_%s.html'
BREF_STARTERS_FILE_TEMPLATE = "bref_starters_%s_%s.html"
MISSING_FILES_FILE = "missing_files.txt"
PBP_FIRST_SEASON = 1996

BR_ABBR_TO_NBA_ABBR = {
    'AND': 'AND',
    'ATL': 'ATL',
    'BAL': 'BAL',
    'BLB': 'BAL',
    'BOS': 'BOS',
    'BRK': 'BKN',
    'BUF': 'BUF',
    'CAP': 'CAP',
    'CHA': 'CHA',
    'CHH': 'CHH',
    'CHI': 'CHI',
    'CHO': 'CHA',
    'CHS': 'CHS',
    'CIN': 'CIN',
    'CLE': 'CLE',
    'CLR': 'CLR',
    'DAL': 'DAL',
    'DEN': 'DEN',
    'DET': 'DET',
    'FTW': 'FTW',
    'GSW': 'GSW',
    'HOU': 'HOU',
    'IND': 'IND',
    'INO': 'INO',
    'KCK': 'KCK',
    'KCO': 'KCK',
    'LAC': 'LAC',
    'LAL': 'LAL',
    'MEM': 'MEM',
    'MIA': 'MIA',
    'MIL': 'MIL',
    'MIN': 'MIN',
    'MNL': 'MNL',
    'NJN': 'NJN',
    'NOH': 'NOH',
    'NOP': 'NOP',
    'NYK': 'NYK',
    'OKC': 'OKC',
    'ORL': 'ORL',
    'PHI': 'PHI',
    'PHO': 'PHX',
    'PHW': 'PHW',
    'POR': 'POR',
    'ROC': 'ROC',
    'SAC': 'SAC',
    'SAS': 'SAS',
    'SDR': 'SDR',
    'SEA': 'SEA',
    'SFW': 'SFW',
    'SHE': 'SHE',
    'STB': 'BOM',
    'STL': 'STL',
    'SYR': 'SYR',
    'TRI': 'TCB',
    'UTA': 'UTA',
    'WAS': 'WAS',
    'WSB': 'WAS',
    'WSC': 'WAS',
    'TOR': 'TOR',
}

ODDS_TEAM_NAMES = {
    'Los Angeles Clippers': 'LA Clippers'
}

BREF_LEVEL_TITLE_TO_ORDER = {
    "Central Division Finals": [[1949, 2999, 3]],
    "Central Division Semifinals": [[1949, 2999, 4]],
    "Eastern Conference Finals": [[1970, 2999, 2]],
    "Eastern Conference First Round": [[1974, 2999, 4]],
    "Eastern Conference Semifinals": [[1970, 2999, 3]],
    "Eastern Division Finals": [[1948, 1948, 2], [1949, 1949, 3], [1950, 2999, 2]],
    "Eastern Division Semifinals": [[1948, 1948, 3], [1949, 1949, 4], [1950, 2999, 3]],
    "Finals": [[1946, 2999, 1]],
    "Quarterfinals": [[1946, 2999, 3]],
    "Semifinals": [[1946, 2999, 2]],
    "Western Conference Finals": [[1970, 2999, 2]],
    "Western Conference First Round": [[1974, 2999, 4]],
    "Western Conference Semifinals": [[1970, 2999, 3]],
    "Western Division Finals": [[1948, 1948, 2], [1949, 1949, 3], [1950, 2999, 2]],
    "Western Division Semifinals": [[1948, 1948, 3], [1949, 1949, 4], [1950, 2999, 3]]
}
TEAM_IDS_TO_BREF_ABBR = {
    1610612737: [[1949, 1950, 'TRI'], [1951, 1954, 'MLH'], [1955, 1967, 'STL'], [1968, 3000, 'ATL']],
    1610612738: [[1946, 3000, 'BOS']],
    1610612751: [[1967, 1967, 'NJA'], [1968, 1975, 'NYA'], [1976, 1976, 'NYN'], [1977, 2011, 'NJN'], [2012, 3000, 'BRK']],
    1610612766: [[1988, 2003, 'CHH'], [2004, 2013, 'CHA'], [2014, 3000, 'CHO']],
    1610612741: [[1966, 3000, 'CHI']],
    1610612739: [[1970, 3000, 'CLE']],
    1610612742: [[1980, 3000, 'DAL']],
    1610612743: [[1967, 1973, 'DNR'], [1974, 1975, 'DNA'], [1976, 3000, 'DEN']],
    1610612765: [[1948, 1956, 'FTW'], [1957, 3000, 'DET']],
    1610612744: [[1946, 1961, 'PHW'], [1962, 1970, 'SFW'], [1971, 3000, 'GSW']],
    1610612745: [[1967, 1970, 'SDR'], [1971, 3000, 'HOU']],
    1610612754: [[1967, 1975, 'INA'], [1976, 3000, 'IND']],
    1610612746: [[1970, 1977, 'BUF'], [1978, 1983, 'SDC'], [1984, 3000, 'LAC']],
    1610612747: [[1948, 1959, 'MNL'], [1960, 3000, 'LAL']],
    1610612763: [[1995, 2000, 'VAN'], [2001, 3000, 'MEM']],
    1610612748: [[1988, 3000, 'MIA']],
    1610612749: [[1968, 3000, 'MIL']],
    1610612750: [[1989, 3000, 'MIN']],
    1610612740: [[2002, 2004, 'NOH'], [2005, 2006, 'NOK'], [2007, 2012, 'NOH'], [2013, 3000, 'NOP']],
    1610612752: [[1946, 3000, 'NYK']],
    1610612760: [[1967, 2007, 'SEA'], [2008, 3000, 'OKC']],
    1610612753: [[1989, 3000, 'ORL']],
    1610612755: [[1949, 1962, 'SYR'], [1963, 3000, 'PHI']],
    1610612756: [[1968, 3000, 'PHO']],
    1610612757: [[1970, 3000, 'POR']],
    1610612758: [[1948, 1956, 'ROC'], [1957, 1971, 'CIN'], [1972, 1974, 'KCO'], [1975, 1984, 'KCK'], [1985, 3000, 'SAC']],
    1610612759: [[1967, 1969, 'DLC'], [1970, 1970, 'TEX'], [1971, 1972, 'DLC'], [1973, 1975, 'SAA'], [1976, 3000, 'SAS']],
    1610612761: [[1995, 3000, 'TOR']],
    1610612762: [[1974, 1978, 'NOJ'], [1979, 3000, 'UTA']],
    1610612764: [[1961, 1961, 'CHP'], [1962, 1962, 'CHZ'], [1963, 1972, 'BAL'], [1973, 1973, 'CAP'], [1974, 1996, 'WSB'], [1997, 3000, 'WAS']]
}

BREF_TEAM_NAME_TO_NBA_ID = {
    "Atlanta Hawks": 1610612737, "Brooklyn Nets": 1610612751, "Boston Celtics": 1610612738,
    "Charlotte Hornets": 1610612766, "Cleveland Cavaliers": 1610612739, "Chicago Bulls": 1610612741,
    "Dallas Mavericks": 1610612742, "Denver Nuggets": 1610612743, "Detroit Pistons": 1610612765,
    "Golden State Warriors": 1610612744, "Houston Rockets": 1610612745, "Indiana Pacers": 1610612754,
    "Los Angeles Clippers": 1610612746, "Los Angeles Lakers": 1610612747, "Memphis Grizzlies": 1610612763,
    "Miami Heat": 1610612748, "Milwaukee Bucks": 1610612749, "Minnesota Timberwolves": 1610612750,
    "New York Knicks": 1610612752, "New Orleans Pelicans": 1610612740, "Oklahoma City Thunder": 1610612760,
    "Orlando Magic": 1610612753, "Philadelphia 76ers": 1610612755, "Phoenix Suns": 1610612756,
    "Portland Trail Blazers": 1610612757, "San Antonio Spurs": 1610612759, "Sacramento Kings": 1610612758,
    "Toronto Raptors": 1610612761, "Utah Jazz": 1610612762, "Washington Wizards": 1610612764
}
