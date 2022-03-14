import re
import sqlite3
import os
from pathlib import Path
import pandas as pd
import requests
from bs4 import BeautifulSoup
from numpy import int32, int64
import argparse
#  very important for pbp. fix some issues
from requests import HTTPError

import pbp.Patcher
import EventMaker
import OddsCacheHandler
from BRPlayoffsSummaryHandler import BRPlayoffsSummaryHandler
from OddsCacheHandler import OddsCacheHandler
from PBPCacheHandler import PBPCacheHandler
from constants import *
from BoxScoreCacheHandler import BoxScoreCacheHandler


class DatabaseHandler:
    def __init__(self, use_cache=False, cache_missing_files=False, download_odds=False, download_pbps=False):
        sqlite3.register_adapter(int64, int)
        sqlite3.register_adapter(int32, int)
        self.conn = self.get_connection()
        self.use_cache = use_cache
        self.cache_missing_files = cache_missing_files
        self.download_odds = download_odds
        self.download_pbps = download_pbps
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

    def insert_pbps(self, headers, events):
        aaa = f"""insert or ignore into Event ({', '.join(h for h in headers)}) values ({', '.join('?' for _ in headers)})"""
        self.conn.executemany(aaa, events)
        self.conn.commit()

    def insert_odds(self, odds):
        self.conn.executemany(f"""insert or ignore into Odds (Team, odd, ROUND, SEASON) values (?, ?, ?, ?)""", odds)
        self.conn.commit()

    def insert_series_summary(self, summeries):
        self.conn.executemany(f"""insert or ignore into PlayoffSerieSummary (Season, TeamAAbbrevation, TeamBAbbrevation, TeamAWins, TeamBWins, WinnerAbbrevation, LoserAbbrevation, SerieOrder, LevelTitle)
        values (?, ?, ?, ?, ?, ?, ?, ?, ?)""", summeries)
        self.conn.commit()

    def save_odds_dataframe(self, df):
        self.insert_odds(list(df.to_records(index=False)))

    def save_boxscores(self, rows, headers, table_type):
        to_save = pd.DataFrame(data=rows, columns=headers)
        self.transform_boxscores(to_save)
        self.insert_boxscores(to_save.columns, list(to_save.to_records(index=False)), table_type)

    def save_pbps(self, rows, headers):
        self.insert_pbps(headers, rows)

    def save_summeries(self, summeries):
        self.insert_series_summary(summeries)

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

    def create_pbp_table(self):
        self.conn.execute("""
            create table if not exists Event
            (
                GameId text,
                EventNumber integer,
                EventType integer,
                EventActionType integer,
                Period integer,
                RealTime text,
                Clock text,
                RemainingSeconds real,
                Description text,
                TeamAScore integer,
                TeamBScore integer,
                ScoreMargin integer,
                ShotValue integer,
                PersonAType integer,
                PlayerAId integer,
                PlayerATeamId integer,
                PersonBType integer,
                PlayerBId integer,
                PlayerBTeamId integer,
                PersonCType integer,
                PlayerCId integer,
                PlayerCTeamId integer,
                VideoAvailable integer,
                CountAsPossession integer,
                IsPossessionEndingEvent integer,
                SecondsSincePreviousEvent real,
                TeamALineupIds text,
                TeamBLineupIds text,
                TeamAFoulsToGive integer,
                TeamBFoulsToGive integer,
                PreviousEventNumber integer,
                NextEventNumber integer,
                EventOrder integer,
                primary key (GameId, EventNumber)
            );""")
        self.conn.commit()

    def create_series_levels_table(self):
        self.conn.execute("""
            create table if not exists PlayoffSerieSummary
            (
                Season integer,
                TeamAAbbrevation text,
                TeamBAbbrevation text,
                TeamAWins integer,
                TeamBWins integer,
                WinnerAbbrevation text,
                LoserAbbrevation text,
                SerieOrder integer,
                LevelTitle text,
                primary key (SEASON, TeamAAbbrevation, TeamBAbbrevation)
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

    def get_games_without_events(self, season_type_code):
        tables = self.conn.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name=? or name=?""", [f'Event', 'BoxScoreT']).fetchall()
        if len(tables) > 1:
            res = self.conn.execute(f"""select BoxScoreT.GAME_ID, max(iif(TEAM_ABBREVIATION=MATCHUP_TEAM1, TEAM_ID, null)), max(iif(TEAM_ABBREVIATION=MATCHUP_TEAM2, TEAM_ID, null)) from BoxScoreT left join Event e on e.GameId = BoxScoreT.GAME_ID where e.GameId is null and BoxScoreT.SEASON_TYPE=? and SEASON >= ? group by BoxScoreT.GAME_ID""", [season_type_code, PBP_FIRST_SEASON]).fetchall()
            return res
        return []

    def get_br_seasons_links(self):
        sql = """
            select Season from PlayoffSerieSummary group by Season
        """
        fetched_seasons = self.conn.execute(sql).fetchall()
        fetched_seasons = [s[0] for s in fetched_seasons]
        url = 'https://www.basketball-reference.com/leagues/'
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        seasons_rows = soup.select('.stats_table tr')
        seasons_rows = [s for s in seasons_rows if not s.has_attr('class')]
        to_ret = []
        for s in seasons_rows:
            season = s.select('[data-stat=\"season\"] a')[0]
            season_number = int(re.findall(r'^(.+?)-', season.getText())[0])
            season_link = season['href']
            league_id = s.select('[data-stat=\"lg_id\"] a')[0].getText()
            if season_number not in fetched_seasons and (league_id == 'BAA' or league_id == 'NBA'):
                to_ret.append([season_number, season_link])
        return to_ret

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

    # download and saves all events of a game
    def collect_all_game_events(self, game_id, teamaid, teambid):
        data = self.handle_cache(PBPCacheHandler(game_id))
        if not data:
            return
        try:
            transformed_events = EventMaker.transform_game_events(game_id, teamaid, teambid, data)
        except HTTPError as e:
            print(f'failed transforming {game_id} events. try again later. error: {str(e)}')
            return
        headers = [
            'GameId',
            'EventNumber',
            'EventType',
            'EventActionType',
            'Period',
            'RealTime',
            'Clock',
            'RemainingSeconds',
            'Description',
            'TeamAScore',
            'TeamBScore',
            'ScoreMargin',
            'ShotValue',
            'PersonAType',
            'PlayerAId',
            'PlayerATeamId',
            'PersonBType',
            'PlayerBId',
            'PlayerBTeamId',
            'PersonCType',
            'PlayerCId',
            'PlayerCTeamId',
            'VideoAvailable',
            'CountAsPossession',
            'IsPossessionEndingEvent',
            'SecondsSincePreviousEvent',
            'TeamALineupIds',
            'TeamBLineupIds',
            'TeamAFoulsToGive',
            'TeamBFoulsToGive',
            'PreviousEventNumber',
            'NextEventNumber',
            'EventOrder'
        ]
        self.save_pbps(transformed_events, headers)

    # updates(starts from the last saved date) all box scores of all season types of box score type
    def update_boxscores_table(self, box_score_type):
        print(f'updating boxscores of type {box_score_type}')
        for i in range(0, len(SEASON_TYPES)):
            last_date = self.get_last_game_date(SEASON_TYPES[i]['code'], box_score_type)
            print(f'updating boxscores of type {box_score_type} and season type {SEASON_TYPES[i]["name"]}... current last saved date: {last_date if last_date else "None"}')
            self.collect_all_boxscores(i, box_score_type, start_date=last_date)

    # updates(starts from the last saved date) all box scores of all season types of box score type
    def update_missing_events(self, season_type):
        print(f'updating missing events from {season_type["name"]}')
        games_missing_events = self.get_games_without_events(season_type["code"])
        for gid, teamaid, teambid in games_missing_events:
            print(f'updating events of game {gid}...')
            self.collect_all_game_events(gid, teamaid, teambid)

    def update_all_missing_events(self):
        for season_type in SEASON_TYPES:
            self.update_missing_events(season_type)

    # updates(starts from the last saved date) all box scores of all season types of box score type
    def update_playoff_summary(self, season, season_link):
        data = self.handle_cache(BRPlayoffsSummaryHandler(season, season_link))
        self.save_summeries(data)

    def update_playoffs_summeries(self):
        seasons = self.get_br_seasons_links()
        for season, season_link in seasons:
            self.update_playoff_summary(season, season_link)

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
        self.create_series_levels_table()
        self.update_boxscores_table('P')
        self.update_boxscores_table('T')
        self.update_playoffs_summeries()
        if self.download_pbps:
            print('setting pbps table')
            self.create_pbp_table()
            self.update_missing_events(SEASON_TYPES[2])  # for now update only playoffs
            #  self.update_all_missing_events()
        if self.download_odds:
            print('setting odds table...')
            self.create_odds_table()
            self.update_odds()

    def fix_abbrs(self):
        all_series = self.conn.execute("""select Season, TeamAAbbrevation, TeamBAbbrevation, WinnerAbbrevation, LoserAbbrevation from PlayoffSerieSummary""")
        to_fix = set()
        for s in all_series:
            try:
                self.conn.execute("""update PlayoffSerieSummary set TeamAAbbrevation=?, TeamBAbbrevation=?, WinnerAbbrevation=?, LoserAbbrevation=?
                where Season=? and TeamAAbbrevation=? and TeamBAbbrevation = ? and WinnerAbbrevation = ? and LoserAbbrevation = ?""",
                                  [BR_ABBR_TO_NBA_ABBR[s[1]],
                                   BR_ABBR_TO_NBA_ABBR[s[2]],
                                   BR_ABBR_TO_NBA_ABBR[s[3]],
                                   BR_ABBR_TO_NBA_ABBR[s[4]],
                                   *s
                                   ])
                self.conn.commit()
            except Exception as e:
                to_fix.add(str(e))
        print('\n'.join(sorted(to_fix)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--cache', help='Cache downloaded files', default=False, action='store_true')
    parser.add_argument('-m', '--missing', help='Cache and ignore missing files', default=False, action='store_true')
    parser.add_argument('-o', '--odds', help='Update Odds table', default=False, action='store_true')
    parser.add_argument('-e', '--events', help='Update Events table', default=False, action='store_true')
    parser.add_argument('-lv', '--views_in', type=str, help='Load views from file(override other options)')
    parser.add_argument('-wv', '--views_out', type=str, help='Write views to file(override other options)')
    args = parser.parse_args()
    handler = DatabaseHandler(use_cache=args.cache, cache_missing_files=args.missing, download_odds=args.odds, download_pbps=args.events)
    if args.views_in is not None:
        handler.load_views(args.views_in)
    elif args.views_out is not None:
        handler.save_views(args.views_out)
    else:
        handler.create_database()
    # handler.fix_abbrs()


if __name__ == '__main__':
    main()



