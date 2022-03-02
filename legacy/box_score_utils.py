import matplotlib.pyplot as plt
import requests
import itertools


url_address = "https://stats.nba.com/stats/leaguegamefinder?GB=N&LeagueID=00&PlayerOrTeam=P&Season=%s&SeasonType=%s&StatCategory=PTS&"
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
SEASON_TYPES = [
    "Regular+Season",
    "Playoffs"
]


def get_url(seasons, season_types):
    types = [SEASON_TYPES[i] for i in season_types]
    seasons_str = ''.join(seasons)
    types_str = ','.join(types)
    return url_address % (seasons_str, types_str)


def gets_conds(init_categories, combination):
    return {value: value in combination for value in init_categories}


def win_percent_td(seasons, season_types):
    categories = ["PTS", "REB", "AST", "STL", "BLK"]
    total_td = 0
    total_wins = 0
    players_dict = {}
    for cat_num in range(3, 6):
        for combination in itertools.combinations(categories, cat_num):
            conditions_dict = gets_conds(categories, combination)
            cond_strs = ["%s=10" % (("gt" if val else "lt") + cat) for cat, val in conditions_dict.items()]
            cond_str = "&".join(cond_strs)
            to_send = get_url(seasons, season_types) + cond_str
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


def wins_percent_over_points(seasons, season_types, min_points, max_points, jump):
    for gt_points in range(min_points, max_points, jump):
        to_send = get_url(seasons, season_types) + f'gtPTS={gt_points}'
        data = requests.get(to_send, headers=STATS_HEADERS).json()
        data = data["resultSets"][0]
        headers = data["headers"]
        wl_index = headers.index("WL")
        results = data["rowSet"]
        total_games = len(results)
        total_wins = sum(1 for row in results if row[wl_index] == "W")
        total_loses = total_games - total_wins
        print("gt %d, total games %d, total wins %d, total loses %d, percentage %.02f\n" % (gt_points, total_games, total_wins, total_loses, total_wins/total_games if total_games else 0))


def player_playoff_shots(player_id):
    url_to_send = get_url([], [1]) + f'PlayerID={player_id}'
    data = requests.get(url_to_send, headers=STATS_HEADERS).json()
    data = data["resultSets"][0]
    headers = data["headers"]
    matchup_index = headers.index("MATCHUP")
    season_index = headers.index("SEASON_ID")
    fga_index = headers.index("FGA")
    fg3a_index = headers.index("FG3A")
    results = data["rowSet"]
    series = {}
    for row in results:
        matchup_splitted = row[matchup_index].split(' ')
        if matchup_splitted[0] == "OKC":
            continue
        matchup_key = row[season_index] + matchup_splitted[0] + matchup_splitted[2]
        if matchup_key in series:
            continue
        cur_fga, cur_fg3a = series.get(matchup_key, [0, 0])
        series[matchup_key] = [cur_fga + row[fga_index], cur_fg3a + row[fg3a_index]]

    for key, value in series.items():
        print(f'matchup: {key}, percent: {(value[0] - value[1]) / value[0]}')
    fig, ax = plt.subplots()

    xs = [i for i in range(1, len(series) + 1)]
    ys = [(value[0] - value[1]) / value[0] for value in series.values()]
    ys = ys[::-1]
    matchups = [key for key in series.keys()]
    matchups = matchups[::-1]
    ax.scatter(xs, ys)
    for i, txt in enumerate(matchups):
        ax.annotate(txt, (xs[i], ys[i]), fontSize=8)
    fig.show()


def player_playoff_last_game_3pt_pctg(player_id):
    url_to_send = get_url([], [1]) + f'PlayerID={player_id}'
    data = requests.get(url_to_send, headers=STATS_HEADERS).json()
    data = data["resultSets"][0]
    headers = data["headers"]
    matchup_index = headers.index("MATCHUP")
    season_index = headers.index("SEASON_ID")
    fg3a_index = headers.index("FG3A")
    fg3m_index = headers.index("FG3M")
    results = data["rowSet"][::-1]
    series = {}
    count = {}
    total_fg3a = 0
    total_fg3m = 0
    total_important_fg3a = 0
    total_important_fg3m = 0
    for row in results:
        matchup_splitted = row[matchup_index].split(' ')
        if matchup_splitted[0] == "OKC":
            continue
        total_fg3a += row[fg3a_index]
        total_fg3m += row[fg3m_index]
        matchup_key = row[season_index] + matchup_splitted[0] + matchup_splitted[2]
        count[matchup_key] = count.get(matchup_key, 0) + 1
        if count[matchup_key] >= 6:
            cur_fg3a, cur_fg3m = series.get(matchup_key, [0, 0])
            series[matchup_key] = [cur_fg3a + row[fg3a_index], cur_fg3m + row[fg3m_index]]
            total_important_fg3a += row[fg3a_index]
            total_important_fg3m += row[fg3m_index]

    for key, value in series.items():
        print(f'matchup: {key}, percent: {value[1] / value[0]}')

    print(f'total percentage: {total_fg3m / total_fg3a}')
    print(f'total important percentage: {total_important_fg3m / total_important_fg3a}')
    fig, ax = plt.subplots()

    xs = [i for i in range(1, len(series) + 1)]
    ys = [value[1] / value[0] for value in list(series.values())]
    matchups = [key for key in list(series.keys())]
    ax.scatter(xs, ys)
    for i, txt in enumerate(matchups):
        ax.annotate(txt, (xs[i], ys[i]), fontSize=8)
    fig.show()


player_playoff_last_game_3pt_pctg("201935")
