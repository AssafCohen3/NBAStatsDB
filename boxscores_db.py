import datetime
import sqlite3

import pandas as pd
import requests
import matplotlib.pyplot as plt

url_address = "https://stats.nba.com/stats/leaguegamelog?Counter=1000&DateFrom=&DateTo=&Direction=ASC&LeagueID=00&PlayerOrTeam=P&Season=%s&SeasonType=Regular+Season&Sorter=DATE"

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


def create_data_frame(data, headers):
    return pd.DataFrame(data=data, columns=headers)


def collect_seasongames(season):
    to_send = url_address % f"{season}-{str(season+1)[-2:]}"
    print(to_send)
    data = requests.get(to_send, headers=STATS_HEADERS).json()
    data = data["resultSets"][0]
    headers = data["headers"]
    results = data["rowSet"]
    print(f"found {len(results)} games in season {season}")
    new_df = create_data_frame(results, headers)
    new_df['SEASON'] = season
    return new_df


def collect_seasons():
    df = None
    for i in range(1946, 2021):
        df = collect_seasongames(i) if df is None else pd.concat([df, collect_seasongames(i)], ignore_index=True)
        print(f"{len(df)=}")
    return df


def create_boxscores_table(conn):
    boxscores_df = collect_seasons()
    boxscores_df.to_sql('BoxScore', conn, if_exists='replace', index=False)


def get_connection():
    return sqlite3.connect("Database/boxscores_database.sqlite")


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


def plot_average_most_seasons():
    conn = get_connection()
    res_rows = get_most_seasons_avg(conn, 10, 5, 2010)
    points = [(row[0], row[1]) for row in res_rows]
    print(points)
    plt.scatter(*zip(*points))
    plt.show()



plot_average_most_seasons()