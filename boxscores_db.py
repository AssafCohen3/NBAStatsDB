import sqlite3
import os
from pathlib import Path
import pandas as pd
from numpy import int32, int64
import argparse

import OddsCacheHandler
from OddsCacheHandler import OddsCacheHandler
from constants import *
from BoxScoreCacheHandler import BoxScoreCacheHandler


class DatabaseHandler:
    def __init__(self, use_cache=False, cache_missing_files=False, download_odds=True):
        sqlite3.register_adapter(int64, int)
        sqlite3.register_adapter(int32, int)
        self.conn = self.get_connection()
        self.use_cache = use_cache
        self.cache_missing_files = cache_missing_files
        self.download_odds = download_odds
        self.create_folders()
        if self.cache_missing_files:
            self.missing_files = self.get_missing_files()

    @staticmethod
    def get_connection():
        return sqlite3.connect(DATABASE_PATH + DATABASE_NAME + '.sqlite')

    # get list of cached missing files
    @staticmethod
    def get_missing_files():
        if os.path.isfile(CACHE_PATH + MISSING_FILES_FILE):
            with open(CACHE_PATH + MISSING_FILES_FILE, "r+") as f:
                return [line.strip() for line in f.readlines()]
        return []

    # add some data to every boxscore
    @staticmethod
    def transform_boxscores(df):
        matchup_re_str = r'(.*) (?:@|vs.) (.*)'
        a = df['MATCHUP'].str.extract(matchup_re_str)
        a = a.to_numpy()
        a.sort(axis=1)
        a = pd.DataFrame(data=a, columns=["team1", "team2"])
        df["MATCHUP_TEAM1"] = a["team1"]
        df["MATCHUP_TEAM2"] = a["team2"]
        season_and_type = df["SEASON_ID"].str.extract(r'(\d)(\d*)')
        df["SEASON_TYPE"] = season_and_type[0]
        df["SEASON"] = season_and_type[1]

    # creating cache and database folders
    def create_folders(self):
        if self.use_cache or self.cache_missing_files:
            Path(CACHE_PATH).mkdir(parents=True, exist_ok=True)
        Path(DATABASE_PATH).mkdir(parents=True, exist_ok=True)

    def insert_boxscores(self, headers, boxscores, table_type):
        aaa = f"""insert or ignore into {'BoxScore' + table_type} ({', '.join(h for h in headers)}) values ({', '.join('?' for _ in headers)})"""
        self.conn.executemany(aaa, boxscores)
        self.conn.commit()

    def insert_odds(self, odds):
        self.conn.executemany(f"""insert or ignore into Odds (Team, odd, ROUND, SEASON) values (?, ?, ?, ?)""", odds)
        self.conn.commit()

    def save_odds_dataframe(self, df):
        self.insert_odds(list(df.to_records(index=False)))

    def save_boxscores(self, rows, headers, table_type):
        to_save = pd.DataFrame(data=rows, columns=headers)
        self.transform_boxscores(to_save)
        self.insert_boxscores(to_save.columns, list(to_save.to_records(index=False)), table_type)

    def create_players_boxscores_table(self):
        self.conn.execute("""
            create table if not exists BoxScoreP
            (
                SEASON_ID         TEXT,
                SEASON_TYPE       TEXT,
                SEASON            integer,
                PLAYER_ID         integer,
                PLAYER_NAME       TEXT,
                TEAM_ID           integer,
                TEAM_ABBREVIATION TEXT,
                TEAM_NAME         TEXT,
                GAME_ID           TEXT,
                GAME_DATE         datetime,
                MATCHUP           TEXT,
                MATCHUP_TEAM1     TEXT,
                MATCHUP_TEAM2     TEXT,
                WL                TEXT,
                MIN               integer,
                FGM               integer,
                FGA               integer,
                FG_PCT            real,
                FG3M              integer,
                FG3A              integer,
                FG3_PCT           real,
                FTM               integer,
                FTA               integer,
                FT_PCT            REAL,
                OREB              integer,
                DREB              integer,
                REB               integer,
                AST               integer,
                STL               integer,
                BLK               integer,
                TOV               integer,
                PF                integer,
                PTS               integer,
                PLUS_MINUS        integer,
                FANTASY_PTS       REAL,
                VIDEO_AVAILABLE   INTEGER,
                primary key (GAME_ID, PLAYER_ID, TEAM_ID)
            );""")
        self.conn.commit()

    def create_teams_boxscores_table(self):
        self.conn.execute("""
            create table if not exists BoxScoreT
            (
                SEASON_ID         TEXT,
                SEASON_TYPE       TEXT,
                SEASON            integer,
                TEAM_ID           integer,
                TEAM_ABBREVIATION TEXT,
                TEAM_NAME         TEXT,
                GAME_ID           TEXT,
                GAME_DATE         datetime,
                MATCHUP           TEXT,
                MATCHUP_TEAM1     TEXT,
                MATCHUP_TEAM2     TEXT,
                WL                TEXT,
                MIN               integer,
                FGM               integer,
                FGA               integer,
                FG_PCT            real,
                FG3M              integer,
                FG3A              integer,
                FG3_PCT           real,
                FTM               integer,
                FTA               integer,
                FT_PCT            REAL,
                OREB              integer,
                DREB              integer,
                REB               integer,
                AST               integer,
                STL               integer,
                BLK               integer,
                TOV               integer,
                PF                integer,
                PTS               integer,
                PLUS_MINUS        integer,
                VIDEO_AVAILABLE   INTEGER,
                primary key (GAME_ID, TEAM_ID)
            );""")
        self.conn.commit()

    def create_odds_table(self):
        self.conn.execute("""
            create table if not exists Odds
            (
                Team   TEXT,
                odd    REAL,
                ROUND  INTEGER,
                SEASON INTEGER,
                primary key (SEASON, ROUND, Team)
            )
        """)

    # returns the last saved date of some box score type plus 1 day(empty string if none found)
    def get_last_game_date(self, seaseon_type_code, table_type):
        tables = self.conn.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name=?""", [f'BoxScore{table_type}']).fetchall()
        if len(tables):
            res = self.conn.execute(f"""select strftime('%Y-%m-%d', datetime({"GAME_DATE"}, '+1 day')) from {'BoxScore' + table_type} where {"SEASON_TYPE"}=? order by {"GAME_DATE"} desc limit 1""", [seaseon_type_code]).fetchall()
            return res[0][0] if res else ''
        return ''

    # returns the last saved year of odds plus 1 year(empty string if none found)
    def get_last_odds_year(self):
        tables = self.conn.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='Odds'""").fetchall()
        if tables:
            res = self.conn.execute(f"""select SEASON+1 from Odds order by SEASON desc limit 1""").fetchall()
            return res[0][0] if res else FIRST_ODDS_SEASON
        return FIRST_ODDS_SEASON

    # download the resource represented by the handler
    def handle_cache(self, cache_handler):
        file_name = cache_handler.get_filename()
        if self.use_cache and os.path.isfile(CACHE_PATH + file_name):
            print(f"found {file_name} in cache.")
            with open(CACHE_PATH + file_name, "rb") as f:
                to_ret = cache_handler.load_file(f)
        else:
            if self.cache_missing_files and file_name in self.missing_files:
                print(f"file {file_name} is missing. skipping.")
                return None
            try:
                to_ret = cache_handler.downloader()
                print(f"Downloaded {file_name}.")
                if self.use_cache and cache_handler.to_cache(to_ret):
                    with open(CACHE_PATH + file_name, "w") as f2:
                        cache_handler.cache(to_ret, f2)
                    print(f"Cached {file_name}.")
            except ValueError:
                print(f'failed downloading {file_name}')
                if self.cache_missing_files:
                    with open(CACHE_PATH + MISSING_FILES_FILE, "a") as f:
                        f.write(file_name + "\n")
                return None
        return to_ret

    # download and saves all box scores of a type from a date or from the begining
    def collect_all_boxscores(self, season_type_index, box_score_type, start_date=''):
        date_from = start_date
        continue_loop = True
        while continue_loop:
            data = self.handle_cache(BoxScoreCacheHandler(date_from, season_type_index, box_score_type))
            if not data:
                break
            data = data["resultSets"][0]
            headers = data["headers"]
            results = data["rowSet"]
            print(f"found {len(results)} games in {SEASON_TYPES[season_type_index]['name'].replace('+', ' ')} of type {box_score_type} from date {date_from}")
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
            self.save_boxscores(results, headers, box_score_type)

    # updates(starts from the last saved date) all box scores of all season types of box score type
    def update_boxscores_table(self, box_score_type):
        print(f'updating boxscores of type {box_score_type}')
        for i in range(0, len(SEASON_TYPES)):
            last_date = self.get_last_game_date(SEASON_TYPES[i]['code'], box_score_type)
            print(f'updating boxscores of type {box_score_type} and season type {SEASON_TYPES[i]["name"]}... current last saved date: {last_date if last_date else "None"}')
            self.collect_all_boxscores(i, box_score_type, start_date=last_date)

    # download and saves odds for a season
    def collect_season_odds(self, season):
        df = self.handle_cache(OddsCacheHandler(season))
        if df is None:
            return
        to_ret = None
        for j, odds_round in enumerate(ODDS_TYPES):
            round_df = df["Team"].join(df["Playoffs,prior to..."][odds_round]).dropna().rename(columns={odds_round: "odd"})
            round_df["ROUND"] = j
            round_df["SEASON"] = season
            to_ret = round_df if to_ret is None else pd.concat([to_ret, round_df], ignore_index=True)
        self.save_odds_dataframe(to_ret)

    # updates(start form last saved year) odds
    def update_odds(self):
        last_saved_season = self.get_last_odds_year()
        print(f'updating odds... current last saved season: {last_saved_season if last_saved_season else "None"}')
        for i in range(last_saved_season, LAST_SEASON):
            print(f'downloading odds of season {i}...')
            self.collect_season_odds(i)

    def load_views(self, views_file):
        with open(views_file, 'r') as f:
            cmd = f.read()
        self.conn.executescript(cmd)
        self.conn.commit()
        print(f'loaded successfully {cmd.count("CREATE VIEW IF NOT EXISTS")} views.')

    def save_views(self, file_name):
        sqls = self.conn.execute("""select sql || ';' from sqlite_master where type = 'view'""").fetchall()
        output = '\n'.join(row[0].replace('CREATE VIEW', 'CREATE VIEW IF NOT EXISTS') for row in sqls)
        with open(file_name, 'w') as f:
            f.write(output)
        print(f'written successfully {len(sqls)} views.')

    # create the whole database
    def create_database(self):
        print('setting boxscore tables...')
        self.create_players_boxscores_table()
        self.create_teams_boxscores_table()
        self.update_boxscores_table('P')
        self.update_boxscores_table('T')
        if self.download_odds:
            print('setting odds table...')
            self.create_odds_table()
            self.update_odds()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--cache', help='Cache downloaded files', default=False, action='store_true')
    parser.add_argument('-m', '--missing', help='Cache and ignore missing files', default=False, action='store_true')
    parser.add_argument('-o', '--odds', help='Update Odds table', default=False, action='store_true')
    parser.add_argument('-lv', '--views_in', type=str, help='Load views from file(override other options)')
    parser.add_argument('-wv', '--views_out', type=str, help='Write views to file(override other options)')
    args = parser.parse_args()
    handler = DatabaseHandler(use_cache=args.cache, cache_missing_files=args.missing, download_odds=args.odds)
    if args.views_in is not None:
        handler.load_views(args.views_in)
    elif args.views_out is not None:
        handler.save_views(args.views_out)
    else:
        handler.create_database()


if __name__ == '__main__':
    main()
