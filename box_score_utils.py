import urllib.request, json, datetime
import requests
import itertools


url_address = "https://stats.nba.com/stats/leaguegamefinder?Conference=&DateFrom=&DateTo=&Division=&DraftNumber=&DraftRound=&DraftYear=&GB=N&LeagueID=00&Location=&Outcome=&PlayerOrTeam=P&Season=%s&SeasonType=Regular+Season,Playoffs&StatCategory=PTS&TeamID=&VsConference=&VsDivision=&VsTeamID=&"
# Season can be empty(means all seasons)
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


def gets_conds(init_categories, combination):
    return {value: value in combination for value in init_categories}


def win_percent_td(seasons):
    categories = ["PTS", "REB", "AST", "STL", "BLK"]
    total_td = 0
    total_wins = 0
    players_dict = {}
    for cat_num in range(3, 6):
        for combination in itertools.combinations(categories, cat_num):
            conditions_dict = gets_conds(categories, combination)
            cond_strs = ["%s=10" % (("gt" if val else "lt") + cat) for cat, val in conditions_dict.items()]
            cond_str = "&".join(cond_strs)
            to_send = url_address % seasons + cond_str
            data = requests.get(to_send, headers=STATS_HEADERS).json()
            data = data["resultSets"][0]
            headers = data["headers"]
            wl_index = headers.index("WL")
            name_index = headers.index("PLAYER_NAME")
            results = data["rowSet"]
            total_games = len(results)
            print("conds: %s. recieved: %d games." % (cond_str, total_games))
            total_td += total_games
            for entry in results:
                val = 1 if entry[wl_index] == "W" else 0
                total_wins += val
                if entry[name_index] in players_dict:
                    (total, wins) = players_dict[entry[name_index]]
                    players_dict[entry[name_index]] = (total + 1, wins + val)
                else:
                    players_dict[entry[name_index]] = (1, val)

    print("total TD games: %d, total Wins: %d, percentage: %.02f" % (total_td, total_wins, total_wins/total_td))
    for player, (total, wins) in sorted(players_dict.items(), key=lambda item: item[1][0], reverse=True):
        print("total %s TD games: %d, total Wins: %d, percentage: %.02f" % (player, total, wins, wins / total))


def wins_percent_over_points(seasons, min_points, max_points, jump):
    for gt_points in range(min_points, max_points, jump):
        to_send = url_address % seasons + f'gtPTS={gt_points}'
        data = requests.get(to_send, headers=STATS_HEADERS).json()
        data = data["resultSets"][0]
        headers = data["headers"]
        wl_index = headers.index("WL")
        results = data["rowSet"]
        total_games = len(results)
        total_wins = sum(1 for row in results if row[wl_index] == "W")
        total_loses = total_games - total_wins
        print("gt %d, total games %d, total wins %d, total loses %d, percentage %.02f\n" % (gt_points, total_games, total_wins, total_loses, total_wins/total_games if total_games else 0))


wins_percent_over_points('', 30, 105, 5)
