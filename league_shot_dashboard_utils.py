import requests
url_address = "https://stats.nba.com/stats/leaguedashplayerptshot?LeagueID=00&Month=0&OpponentTeamID=0&PORound=0&PaceAdjust=N&PerMode=Totals&Period=0&Season=%s&SeasonType=%s&TeamID=0&"
season_types = ['Regular+Season', 'Playoffs', 'All-Star', 'Play-In']
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


def shotclock_percent(season, season_type, player_to_check):
    total = 0
    player_total = 0
    clocks = {"24-22": 0, "22-18 Very Early": 0, "18-15 Early": 0, "15-7 Average": 0, "7-4 Late": 0, "4-0 Very Late": 0}
    player_spec = clocks.copy()
    for key in clocks.keys():
        key_to_plus = key.replace(" ", "+")
        to_send = url_address % (season, season_types[season_type]) + f'ShotClockRange={key_to_plus}&'
        data = requests.get(to_send, headers=STATS_HEADERS).json()
        data = data["resultSets"][0]
        headers = data["headers"]
        attempted_index = headers.index("FGA")
        name_index = headers.index("PLAYER_NAME")
        results = data["rowSet"]
        number_of_shot_taken = sum(row[attempted_index] for row in results)
        number_of_player_fga = sum(row[attempted_index] for row in results if row[name_index] == player_to_check)
        clocks[key] = number_of_shot_taken
        player_spec[key] = number_of_player_fga
        total += number_of_shot_taken
        player_total += number_of_player_fga
    print("league total fga: %d" % total)
    print("%s total fga: %d\n" % (player_to_check, player_total))
    for key in clocks.keys():
        league_freq = clocks[key]/total
        player_freq = player_spec[key]/player_total
        print("game clock: %s:" % key)
        print("league total fga: %d, league freq: %.02f" % (clocks[key], league_freq))
        print("%s total fga: %d, %s freq: %.02f\n" % (player_to_check, player_spec[key], player_to_check, player_freq))


shotclock_percent('2020-21', 0, 'James Harden')
