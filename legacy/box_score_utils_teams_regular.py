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


def collect_season_regular_games(season, df):
    to_send = url_address % season
    print(to_send)
    data = requests.get(to_send).json()
    data = data["league"]['standard']
    to_add = [transform_row(season, row, b) for row in data if row['seasonStageId'] == 2 and row['statusNum'] == 3 for b in (True, False)]
    print(f"found {len(to_add)} in season {season}")
    new_df = create_data_frame(to_add)
    return pd.concat([df, new_df], ignore_index=True)



def blah(season):
    to_send = url_address % season
    print(to_send)
    data = requests.get(to_send).json()
    data = data["league"]['standard']
    to_add = [transform_row(season, row, b) for row in data if row['seasonStageId'] == 2 and row['statusNum'] == 3 for b in (True, False)]
    print(f"found {len(to_add)} in season {season}")


def collect_teams():
    to_send = 'http://data.nba.net/prod/v1/2020/teams.json'
    print(to_send)
    data = requests.get(to_send).json()
    data = data["league"]['standard']
    return pd.DataFrame(data)


def collect_seasons():
    df = create_data_frame([])
    for i in range(2015, 2021):
        df = collect_season_regular_games(i, df)
    return df


def create_games_table(conn):
    playoff_games_df = collect_seasons()
    playoff_games_df.to_sql('RegularGame', conn, if_exists='append', index=False)


def create_teams_table(conn):
    teams_df = collect_teams()
    teams_df.to_sql('Team', conn, if_exists='append', index=False)


def create_database():
    conn = sqlite3.connect("Database/regular_games_database.sqlite")
    create_teams_table(conn)
    create_games_table(conn)
    conn.commit()


blah(2020)