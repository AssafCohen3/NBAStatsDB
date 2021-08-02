import datetime
import sqlite3

import pandas as pd
import requests
import matplotlib.pyplot as plt

url_address = "https://data.nba.net/prod/v1/%s/schedule.json"


def transform_row(season, row, home_or_visitor):
    game_date = datetime.datetime.strptime(row['startTimeUTC'], '%Y-%m-%dT%H:%M:%S.%fZ')
    return season, row['gameId'], game_date, row['hTeam' if home_or_visitor else 'vTeam']["teamId"], row['vTeam' if home_or_visitor else 'hTeam']["teamId"]


def create_data_frame(data):
    return pd.DataFrame(data=data, columns=['season', 'game_id', 'start_time', 'teamid', 'vsteamid'])


def collect_season_playoff_games(season, df):
    to_send = url_address % season
    print(to_send)
    data = requests.get(to_send).json()
    data = data["league"]['standard']
    to_add = [transform_row(season, row, b) for row in data if row['seasonStageId'] == 4 and row['statusNum'] == 3 for b in (True, False)]
    print(f"found {len(to_add)} in season {season}")
    new_df = create_data_frame(to_add)
    return pd.concat([df, new_df], ignore_index=True)


def collect_teams():
    to_send = 'http://data.nba.net/prod/v1/2020/teams.json'
    print(to_send)
    data = requests.get(to_send).json()
    data = data["league"]['standard']
    return pd.DataFrame(data)


def collect_seasons():
    df = create_data_frame([])
    for i in range(2015, 2021):
        df = collect_season_playoff_games(i, df)
    return df


def create_games_table(conn):
    playoff_games_df = collect_seasons()
    playoff_games_df.to_sql('PlayoffGame', conn, if_exists='append', index=False)


def create_teams_table(conn):
    teams_df = collect_teams()
    teams_df.to_sql('Team', conn, if_exists='append', index=False)


def create_database():
    conn = sqlite3.connect("Database/playoff_games_database.sqlite")
    create_teams_table(conn)
    create_games_table(conn)
    conn.commit()


def get_rests_avg(conn, start_round, end_round, min_rounds):
    statement = """select season, team_name, count(distinct playoff_round) as rounds, count(*) as games, (count(*) * 1.0) / count(distinct playoff_round) as game_per_round, avg(rest_hours) as avg_rest from PlayoffGameWithRestInSeries 
                    where playoff_round >= ?  and playoff_round <= ? group by season, team_name having count(distinct playoff_round) >= ?
                    order by avg_rest
"""
    cur = conn.cursor()
    cur.execute(statement, (start_round, end_round, min_rounds))
    rows = cur.fetchall()
    return rows


def plot_rests(rows):
    points = [(row[4], row[5]) for row in rows]
    print(points)
    plt.scatter(*zip(*points))
    plt.show()


conn = sqlite3.connect("Database/playoff_games_database.sqlite")
res_rows = get_rests_avg(conn, 1, 4, 2)
plot_rests(res_rows)