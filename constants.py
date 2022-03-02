BOXSCORES_ENDPOINT = "https://stats.nba.com/stats/leaguegamelog?Counter=1000&DateFrom=%s&DateTo=&Direction=ASC&LeagueID=00&PlayerOrTeam=%s&Season=ALLTIME&SeasonType=%s&Sorter=DATE"
ODDS_ENDPOINT = "https://www.sportsoddshistory.com/nba-main/?y=%s&sa=nba&a=finals&o=r"
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
ODDS_FILE_TEMPLATE = "odds_%s.html"
MISSING_FILES_FILE = "missing_files.txt"
