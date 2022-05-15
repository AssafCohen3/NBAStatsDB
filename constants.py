BOXSCORES_ENDPOINT = "https://stats.nba.com/stats/leaguegamelog?Counter=1000&DateFrom=%s&DateTo=&Direction=ASC&LeagueID=00&PlayerOrTeam=%s&Season=ALLTIME&SeasonType=%s&Sorter=DATE"
PBP_ENDPOINT = 'https://stats.nba.com/stats/playbyplayv2?GameId=%s&StartPeriod=0&EndPeriod=14'
ODDS_ENDPOINT = "https://www.sportsoddshistory.com/nba-main/?y=%s&sa=nba&a=finals&o=r"
PLAYERS_INDEX_ENDPOINT = 'https://stats.nba.com/stats/playerindex?Historical=1&LeagueID=00&Season=%s&SeasonType=Regular+Season'
TEAM_ROSTER_ENDPOINT = 'https://stats.nba.com/stats/commonteamroster?LeagueID=00&Season=%s&TeamID=%s'
PLAYER_PROFILE_ENDPOINT = 'http://stats.nba.com/stats/commonplayerinfo/?playerId=%s'
PLAYER_AWARDS_ENDPOINT = 'https://stats.nba.com/stats/playerawards?PlayerID=%s'
TEAM_DETAILS_ENDPOINT = 'http://stats.nba.com/stats/teamdetails/?teamId=%s'
BREF_SEASON_STATS_ENDPOINT = 'https://www.basketball-reference.com/leagues/%s_%s_per_game.html'
BREF_PLAYERS_ENDPOINT = 'https://www.basketball-reference.com/players/%s'
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
BREF_PLAYERS_FILE_TEMPLATE = 'bref_players_%s.html'
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
    1610612751: [[1967, 1967, 'NJA'], [1968, 1975, 'NYA'], [1976, 1976, 'NYN'], [1977, 2011, 'NJN'],
                 [2012, 3000, 'BRK']],
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
    1610612758: [[1948, 1956, 'ROC'], [1957, 1971, 'CIN'], [1972, 1974, 'KCO'], [1975, 1984, 'KCK'],
                 [1985, 3000, 'SAC']],
    1610612759: [[1967, 1969, 'DLC'], [1970, 1970, 'TEX'], [1971, 1972, 'DLC'], [1973, 1975, 'SAA'],
                 [1976, 3000, 'SAS']],
    1610612761: [[1995, 3000, 'TOR']],
    1610612762: [[1974, 1978, 'NOJ'], [1979, 3000, 'UTA']],
    1610612764: [[1961, 1961, 'CHP'], [1962, 1962, 'CHZ'], [1963, 1972, 'BAL'], [1973, 1973, 'CAP'],
                 [1974, 1996, 'WSB'], [1997, 3000, 'WAS']]
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
    "Toronto Raptors": 1610612761, "Utah Jazz": 1610612762, "Washington Wizards": 1610612764,
}

BREF_DEFUNCT_TEAM_NAME_NBA_ID = {
    "Waterloo Hawks": 1610610037, "Washington Capitols": 1610610036, "Toronto Huskies": 1610610035,
    "St. Louis Bombers": 1610610034, "Sheboygan Red Skins": 1610610033, "Providence Steam Rollers": 1610610032,
    "Pittsburgh Ironmen": 1610610031, "Indianapolis Olympians": 1610610030, "Indianapolis Jets": 1610610029,
    "Detroit Falcons": 1610610028, "Cleveland Rebels": 1610610026, "Chicago Stags": 1610610025,
    "Baltimore Bullets": 1610610024, "Anderson Packers": 1610610023, "Denver Nuggets": 1610610027
}

BREF_ABBREVATION_TO_NBA_TEAM_ID = {
    'CLR': [[1946, 1946, 1610610026]], 'DTF': [[1946, 1946, 1610610028]], 'PIT': [[1946, 1946, 1610610031]],
    'TRH': [[1946, 1946, 1610610035]], 'PRO': [[1946, 1948, 1610610032]], 'CHS': [[1946, 1949, 1610610025]],
    'STB': [[1946, 1949, 1610610034]], 'WSC': [[1946, 1950, 1610610036]], 'PHW': [[1946, 1961, 1610612744]],
    'BOS': [[1946, 2999, 1610612738]], 'NYK': [[1946, 2999, 1610612752]], 'BLB': [[1947, 1954, 1610610024]],
    'INJ': [[1948, 1948, 1610610029]], 'ROC': [[1948, 1956, 1610612758]], 'FTW': [[1948, 1956, 1610612765]],
    'MNL': [[1948, 1959, 1610612747]], 'AND': [[1949, 1949, 1610610023]], 'DNN': [[1949, 1949, 1610610027]],
    'SHE': [[1949, 1949, 1610610033]], 'WAT': [[1949, 1949, 1610610037]], 'TRI': [[1949, 1950, 1610612737]],
    'INO': [[1949, 1952, 1610610030]], 'SYR': [[1949, 1962, 1610612755]], 'MLH': [[1951, 1954, 1610612737]],
    'STL': [[1955, 1967, 1610612737]], 'CIN': [[1957, 1971, 1610612758]], 'DET': [[1957, 2999, 1610612765]],
    'LAL': [[1960, 2999, 1610612747]], 'CHP': [[1961, 1961, 1610612764]], 'CHZ': [[1962, 1962, 1610612764]],
    'SFW': [[1962, 1970, 1610612744]], 'BAL': [[1963, 1972, 1610612764]], 'PHI': [[1963, 2999, 1610612755]],
    'CHI': [[1966, 2999, 1610612741]], 'SDR': [[1967, 1970, 1610612745]], 'SEA': [[1967, 2007, 1610612760]],
    'ATL': [[1968, 2999, 1610612737]], 'MIL': [[1968, 2999, 1610612749]], 'PHO': [[1968, 2999, 1610612756]],
    'BUF': [[1970, 1977, 1610612746]], 'CLE': [[1970, 2999, 1610612739]], 'POR': [[1970, 2999, 1610612757]],
    'GSW': [[1971, 2999, 1610612744]], 'HOU': [[1971, 2999, 1610612745]], 'KCO': [[1972, 1974, 1610612758]],
    'CAP': [[1973, 1973, 1610612764]], 'NOJ': [[1974, 1978, 1610612762]], 'WSB': [[1974, 1996, 1610612764]],
    'KCK': [[1975, 1984, 1610612758]], 'NYN': [[1976, 1976, 1610612751]], 'DEN': [[1976, 2999, 1610612743]],
    'IND': [[1976, 2999, 1610612754]], 'SAS': [[1976, 2999, 1610612759]], 'NJN': [[1977, 2011, 1610612751]],
    'SDC': [[1978, 1983, 1610612746]], 'UTA': [[1979, 2999, 1610612762]], 'DAL': [[1980, 2999, 1610612742]],
    'LAC': [[1984, 2999, 1610612746]], 'SAC': [[1985, 2999, 1610612758]], 'CHH': [[1988, 2001, 1610612766]],
    'MIA': [[1988, 2999, 1610612748]], 'MIN': [[1989, 2999, 1610612750]], 'ORL': [[1989, 2999, 1610612753]],
    'VAN': [[1995, 2000, 1610612763]], 'TOR': [[1995, 2999, 1610612761]], 'WAS': [[1997, 2999, 1610612764]],
    'MEM': [[2001, 2999, 1610612763]], 'NOH': [[2002, 2004, 1610612740], [2007, 2012, 1610612740]],
    'CHA': [[2004, 2013, 1610612766]], 'NOK': [[2005, 2006, 1610612740]], 'OKC': [[2008, 2999, 1610612760]],
    'BRK': [[2012, 2999, 1610612751]], 'NOP': [[2013, 2999, 1610612740]], 'CHO': [[2014, 2999, 1610612766]]
}

TEAM_NBA_ID_TO_NBA_NAME = {
    1610610023: "Anderson Packers", 1610610024: "Baltimore Bullets", 1610610025: "Chicago Stags",
    1610610026: "Cleveland Rebels", 1610610027: "Denver Nuggets", 1610610028: "Detroit Falcons",
    1610610029: "Indianapolis Jets", 1610610030: "Indianapolis Olympians", 1610610031: "Pittsburgh Ironmen",
    1610610032: "Providence Steamrollers", 1610610033: "Sheboygan Redskins", 1610610034: "St. Louis Bombers",
    1610610035: "Toronto Huskies", 1610610036: "Washington Capitols", 1610610037: "Waterloo Hawks",
    1610612737: "Atlanta Hawks", 1610612738: "Boston Celtics", 1610612739: "Cleveland Cavaliers",
    1610612740: "New Orleans Pelicans", 1610612741: "Chicago Bulls", 1610612742: "Dallas Mavericks",
    1610612743: "Denver Nuggets", 1610612744: "Golden State Warriors", 1610612745: "Houston Rockets",
    1610612746: "LA Clippers", 1610612747: "Los Angeles Lakers", 1610612748: "Miami Heat",
    1610612749: "Milwaukee Bucks", 1610612750: "Minnesota Timberwolves", 1610612751: "Brooklyn Nets",
    1610612752: "New York Knicks", 1610612753: "Orlando Magic", 1610612754: "Indiana Pacers",
    1610612755: "Philadelphia 76ers", 1610612756: "Phoenix Suns", 1610612757: "Portland Trail Blazers",
    1610612758: "Sacramento Kings", 1610612759: "San Antonio Spurs", 1610612760: "Oklahoma City Thunder",
    1610612761: "Toronto Raptors", 1610612762: "Utah Jazz", 1610612763: "Memphis Grizzlies",
    1610612764: "Washington Wizards", 1610612765: "Detroit Pistons", 1610612766: "Charlotte Hornets",
    1610616833: "Team Durant", 1610616834: "Team LeBron"
}
