import datetime
import re
import sqlite3
import json
import os
import pandas as pd
import requests
import matplotlib.pyplot as plt

url_address = "https://stats.nba.com/stats/leaguegamelog?Counter=1000&DateFrom=&DateTo=&Direction=ASC&LeagueID=00&PlayerOrTeam=P&Season=%s&SeasonType=%s&Sorter=DATE"
url_address_date = "https://stats.nba.com/stats/leaguegamelog?Counter=1000&DateFrom=%s&DateTo=&Direction=ASC&LeagueID=00&PlayerOrTeam=P&Season=ALLTIME&SeasonType=%s&Sorter=DATE"

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
    "Playoffs",
    "All+Star"
]
DATABASE_NAME = "boxscores_full_database"
API_COUNT_THRESHOLD = 30000
files_tempplate = "cache/boxscore_%s_%s.json"
files_tempplate_quick = "quick_cache/boxscore_%s_%s.json"

def create_data_frame(data, headers):
    return pd.DataFrame(data=data, columns=headers)


def get_boxscores(season, season_type_index):
    file_name = files_tempplate % (season, season_type_index)
    if os.path.isfile(file_name):
        print(f"found {file_name} in cache.")
        with open(file_name, "rb") as f:
            to_ret = json.load(f)
    else:
        to_send = url_address % (f"{season}-{str(season + 1)[-2:]}", SEASON_TYPES[season_type_index])
        to_ret = requests.get(to_send, headers=STATS_HEADERS).json()
        with open(file_name, "w") as f2:
            json.dump(to_ret, f2)
        print(f"Downloaded and cached {file_name}.")
    return to_ret


def get_cached_boxscores_quick(date_from, season_type_index):
    date_tmp = date_from
    if date_tmp == "":
        date_tmp = "first"
    file_name = files_tempplate_quick % (date_tmp.replace("/", ""), season_type_index)
    if os.path.isfile(file_name):
        print(f"found {file_name} in cache.")
        with open(file_name, "rb") as f:
            to_ret = json.load(f)
    else:
        to_send = url_address_date % (date_from, SEASON_TYPES[season_type_index])
        to_ret = requests.get(to_send, headers=STATS_HEADERS).json()
        data = to_ret["resultSets"][0]
        results = data["rowSet"]
        print(f"Downloaded {file_name}.")
        if len(results) >= API_COUNT_THRESHOLD:
            with open(file_name, "w") as f2:
                json.dump(to_ret, f2)
            print(f"Cached {file_name}.")
    return to_ret


def collect_seasongames(season, season_type_index):
    data = get_boxscores(season, season_type_index)
    data = data["resultSets"][0]
    headers = data["headers"]
    results = data["rowSet"]
    print(f"found {len(results)} games in {SEASON_TYPES[season_type_index].replace('+', ' ')} of season {season}")
    new_df = create_data_frame(results, headers)
    new_df['SEASON'] = season
    new_df['SEASON_TYPE'] = season_type_index
    return new_df


def collect_seasons_quick(season_type_index):
    df = None
    date_from = ""
    continue_loop = True
    while continue_loop:
        data = get_cached_boxscores_quick(date_from, season_type_index)
        data = data["resultSets"][0]
        headers = data["headers"]
        results = data["rowSet"]
        print(f"found {len(results)} games in {SEASON_TYPES[season_type_index].replace('+', ' ')} from date {date_from}")
        if len(results) >= API_COUNT_THRESHOLD:
            game_date_index = headers.index("GAME_DATE")
            count = 0
            last_date = results[-1][game_date_index]
            while results[-1][game_date_index] == last_date:
                results.pop()
                count = count+1
            print(f"popped last {count} items.")
            date_from = last_date
        else:
            continue_loop = False
        new_df = create_data_frame(results, headers)
        new_df['SEASON_TYPE'] = season_type_index
        df = new_df if df is None else pd.concat([df, new_df], ignore_index=True)
    return df


def collect_seasons(season_type_index):
    df = None
    for i in range(1946, 2021):
        df = collect_seasongames(i, season_type_index) if df is None else pd.concat([df, collect_seasongames(i, season_type_index)], ignore_index=True)
        print(f"{len(df)=}")
    return df


def test_collections():
    df1 = collect_seasons(0)
    df2 = collect_seasons_quick(0)
    print(f"{len(df1) = }")
    print(f"{len(df2) = }")
    df1.drop(columns=["SEASON"],inplace=True)
    print(df1)
    print(df2)
    df11 = df1.sort_values(by=df1.columns.tolist()).reset_index(drop=True)
    df21 = df2.sort_values(by=df2.columns.tolist()).reset_index(drop=True)
    print("*****************************")
    print(df11["PLAYER_ID"].equals(df21["PLAYER_ID"]))


def create_boxscores_table(conn):
    playoff_boxscores_df = collect_seasons(1)
    regular_boxscores_df = collect_seasons(0)
    all_boxscores_df = pd.concat([regular_boxscores_df, playoff_boxscores_df], ignore_index=True)
    all_boxscores_df.to_sql('BoxScore', conn, if_exists='replace', index=False)


def get_connection():
    return sqlite3.connect(f"Database/{DATABASE_NAME}.sqlite")


def create_database():
    conn = get_connection()
    create_boxscores_table(conn)
    conn.commit()


def get_most_seasons_avg(conn, seasons_range, min_career, max_season):
    statement = """select (PC.FirstYear/ :range * :range) as season, round(avg(SeasonsAt), 2) as AverageMostSeasonsAtTeam
                    from PlayerTeamMostSeasons PTMS join PlayerCareer PC on PTMS.PLAYER_ID = PC.PLAYER_ID
                    where PC.CareerLength >= :min_career and season <= :max_season group by PC.FirstYear/:range * :range
"""
    cur = conn.cursor()
    cur.execute(statement, {"range": seasons_range, "min_career": min_career, "max_season": max_season})
    rows = cur.fetchall()
    return rows


def get_adjusted_teams_avg(conn, seasons_range, min_career, max_season):
    statement = """select (FirstYear / :range) * :range as SEASON, round(avg(AdjustedTeamNumber), 2) as AverageAdjustedTeamsNumber from PlayerAdjustedTeamsNumber
                    where SEASON <= :max_season and CareerLength >= :min_career
                    group by (FirstYear / :range) * :range
"""

    cur = conn.cursor()
    cur.execute(statement, {"range": seasons_range, "min_career": min_career, "max_season": max_season})
    rows = cur.fetchall()
    return rows


def get_teams_avg(conn, seasons_range, min_career, max_season):
    statement = """select (FirstYear / :range) * :range as SEASON, round(avg(PlayerTeamNumber), 2) as AverageAdjustedTeamsNumber from PlayerAdjustedTeamsNumber
                    where SEASON <= :max_season and CareerLength >= :min_career
                    group by (FirstYear / :range) * :range
"""

    cur = conn.cursor()
    cur.execute(statement, {"range": seasons_range, "min_career": min_career, "max_season": max_season})
    rows = cur.fetchall()
    return rows


def plot_average_most_seasons():
    conn = get_connection()
    res_rows = get_most_seasons_avg(conn, 5, 5, 2010)
    points = [(row[0], row[1]) for row in res_rows]
    print(points)
    plt.scatter(*zip(*points))
    plt.ylim(0, 10)
    plt.show()


def plot_average_player_teams_number():
    conn = get_connection()
    average_teams_number = get_teams_avg(conn, 5, 5, 2005)
    adjusted_average_teams_number = get_adjusted_teams_avg(conn, 5, 5, 2005)
    average_teams_points = [(row[0], row[1]) for row in average_teams_number]
    adjusted_average_teams_points = [(row[0], row[1]) for row in adjusted_average_teams_number]
    print(f"{average_teams_points=}")
    print(f"{adjusted_average_teams_points=}")
    plt.scatter(*zip(*average_teams_points), color='blue', label="regular average")
    plt.scatter(*zip(*adjusted_average_teams_points), color='red', label="adjusted average")
    plt.legend()
    plt.ylim(0, 10)
    plt.show()


def find_first_year(max_year=datetime.datetime.now().year-1):
    high = max_year
    low = 0
    while low <= high:
        middle = (high + low) // 2
        season_str = f"{middle}-{str(middle + 1)[-2:]}"
        to_send = url_address % season_str
        data = requests.get(to_send, headers=STATS_HEADERS)
        if data and data.json()["resultSets"][0]["rowSet"]:
            high = middle - 1
        else:
            low = middle + 1
    return high + 1


def differ(list1, list2):
    differ_list = [x for x in list2 if x not in list1]
    print(differ_list)

print("Boxscore DB: Select algorithm")
test_collections()