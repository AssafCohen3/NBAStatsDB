import re
from requests import get
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3


def get_season_players(season_num, league_name):
    url = f"https://www.basketball-reference.com/leagues/{league_name}_{season_num}_per_game.html"
    testt = f"https://widgets.sports-reference.com/wg.fcgi?css=1&site=bbr&url=%2Fleagues%2F{league_name}_{season_num}_per_game.html&div=div_per_game_stats"
    r = get(url)
    df = None

    if r.status_code == 200:
        soup = BeautifulSoup(r.content, 'html.parser')
        table = soup.find('table')
        df = pd.read_html(str(table))[0]
        player_ids = [col.get('data-append-csv') for row in table.find_all('tr', {'class': 'full_table'}) for col in row.find_all('td', {'data-stat': 'player'})]
        player_names = [str(col.find("a").get_text(strip=True)) for row in table.find_all('tr', {'class': 'full_table'}) for col in row.find_all('td', {'data-stat': 'player'})]
        years = [season_num] * len(player_ids)
        leagues = [league_name] * len(player_ids)
        # get rid of multiple teams in one seasons for one player
        df.drop_duplicates(['Rk'], inplace=True)
        # drop rank
        df.drop(['Rk'], inplace=True, axis=1)
        # drop Player row
        df.drop(df[df.G == 'G'].index, inplace=True)
        # replace names
        df['Player'] = player_names
        # insert player_ids
        df.insert(loc=1, column='Player_ID', value=player_ids)
        # insert year
        df.insert(loc=2, column='Year', value=years)
        # insert league
        df.insert(loc=3, column='League', value=leagues)

        return df


def create_player_season_table(conn):
    seasons = get_seasons()
    for season, league in seasons:
        season_num = int(season[:4]) + 1
        season_df = get_season_players(season_num, league)
        season_df.to_sql('PlayerSeason', conn, if_exists='append', index=False)
        print(f'added season {season_num}, {league} to the database.\n')
    print('created player season table\n')


def create_tables(conn):
    create_player_season_table(conn)
    print('finished creating tables\n')


def create_career_length_view(conn):
    c = conn.cursor()
    c.execute("""CREATE VIEW PlayerCareer as
                select Player, Player_ID, min(Year) as Start_Year, max(Years_Experience) as Career_Length from PlayerSeasonWithExperience group by Player_ID;""")
    print('created career length view\n')


def create_experience_view(conn):
    c = conn.cursor()
    c.execute("""CREATE VIEW PlayerSeasonWithExperience as 
                select dense_rank() over (partition by Player_ID order by Year) as Years_Experience, rank() over (partition by Player_ID, League order by Year) as Years_Experience_League, * from PlayerSeason;""")
    print('created experience view\n')


def create_views(conn):
    create_experience_view(conn)
    create_career_length_view(conn)
    print('finished creating views\n')


def create_just_tables():
    conn = sqlite3.connect('Database/nba_database.sqlite')
    create_tables(conn)
    conn.commit()


def create_just_views():
    conn = sqlite3.connect('Database/nba_database.sqlite')
    create_views(conn)
    conn.commit()


def create_whole_database():
    conn = sqlite3.connect('Database/nba_database.sqlite')
    create_tables(conn)
    create_views(conn)
    conn.commit()


def test_single_season(league_name, season_num):
    conn = sqlite3.connect('player_seasons_test.sqlite')
    season_df = get_season_players(season_num, league_name)
    season_df.to_sql('PlayerSeason', conn, if_exists='append', index=False)
    print(f'added season {season_num} to the database.\n')


def get_seasons():
    url = f"https://www.basketball-reference.com/leagues/"
    print(f'{url = }\n')
    r = get(url)
    df = None
    if r.status_code == 200:
        soup = BeautifulSoup(r.content, 'html.parser')
        table = soup.find('table')
        df = pd.read_html(str(table))[0]

        return [list(row[:2]) for row in df.values]


create_just_views()