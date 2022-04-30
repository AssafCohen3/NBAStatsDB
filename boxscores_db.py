import csv
import re
import sqlite3
import os
from pathlib import Path
import pandas as pd
import requests
from bs4 import BeautifulSoup
from numpy import int32, int64
import argparse
from datetime import datetime
#  very important for pbp. fix some issues
import pbp.Patcher
from requests import HTTPError

import EventMaker
from Handlers import OddsCacheHandler
from Handlers.BREFSeasonDraftHandler import BREFSeasonDraftHandler
from Handlers.BREFSeasonStatsHandler import BREFSeasonStatsHandler
from Handlers.BRPlayoffsSummaryHandler import BRPlayoffsSummaryHandler
from Handlers.OddsCacheHandler import OddsCacheHandler
from Handlers.PBPCacheHandler import PBPCacheHandler
from Handlers.PlayerAwardsHandler import PlayerAwardsHandler
from Handlers.PlayerProfileHandler import PlayerProfileHandler
from Handlers.TeamDetailsHandler import TeamDetailsHandler
from PlayersCover import get_teams_cover
from Handlers.PlayersHandler import PlayersHandler
from Handlers.TeamRosterHandler import TeamRosterHandler
from constants import *
from Handlers.BoxScoreCacheHandler import BoxScoreCacheHandler


class DatabaseHandler:
    def __init__(self, use_cache=False, to_cache_missing_files=False):
        sqlite3.register_adapter(int64, int)
        sqlite3.register_adapter(int32, int)
        self.conn = self.get_connection()
        self.use_cache = use_cache
        self.to_cache_missing_files = to_cache_missing_files
        self.create_folders()
        self.current_teams = None
        self.bref_seasons = None
        self.bref_drafts = None
        if self.to_cache_missing_files:
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
        team_ids = df.groupby('GAME_ID')['TEAM_ID']
        # a = team_ids.loc[team_ids['TEAM_ID'].idxmin()]['TEAM_ID', 'TEAM_NAME']
        # b = team_ids.loc[team_ids['TEAM_ID'].idxmin()]['TEAM_NAME', 'TEAM_NAME']
        df['TeamAId'] = team_ids.transform(lambda x: df.loc[x.idxmin(), 'TEAM_ID'])
        df['TeamAName'] = team_ids.transform(lambda x: df.loc[x.idxmin(), 'TEAM_NAME'])
        df['TeamBId'] = team_ids.transform(lambda x: df.loc[x.idxmax(), 'TEAM_ID'])
        df['TeamBName'] = team_ids.transform(lambda x: df.loc[x.idxmax(), 'TEAM_NAME'])

    def collect_teams(self):
        if self.current_teams is not None:
            return self.current_teams
        boxscore_teams_table = self.conn.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='BoxScoreT'""").fetchall()
        if len(boxscore_teams_table):
            sql = """with
            TEAMS_SEASONS as (
                select SEASON, TEAM_ID, TEAM_ABBREVIATION, TEAM_NAME from BoxScoreT
                group by SEASON, TEAM_ID, TEAM_NAME, TEAM_ABBREVIATION
            ),
            WITH_PREVIOUS_SEASON as (
                select SEASON, TEAM_ID, TEAM_NAME, TEAM_ABBREVIATION,
                    row_number() over (partition by TEAM_ID, TEAM_NAME, TEAM_ABBREVIATION order by SEASON) as SEASON_NUMBER
                from TEAMS_SEASONS
            )
            select TEAM_ID, TEAM_ABBREVIATION, TEAM_NAME, min(SEASON) as FirstSeason, max(SEASON) as LastSeason
            from WITH_PREVIOUS_SEASON
            group by TEAM_ID, TEAM_ABBREVIATION, TEAM_NAME, SEASON - SEASON_NUMBER
            order by FirstSeason
            """
            res = self.conn.execute(sql).fetchall()
            self.current_teams = res
            return res
        return []

    # creating cache and database folders
    def create_folders(self):
        if self.use_cache or self.to_cache_missing_files:
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
        self.conn.executemany(f"""insert or ignore into PlayoffSerieSummary (Season, TeamAId, TeamAName, TeamBId, TeamBName, TeamAWins, TeamBWins, WinnerId, WinnerName, LoserId, LoserName, SerieOrder, LevelTitle)
        values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", summeries)
        self.conn.commit()

    def insert_players(self, players):
        self.conn.executemany(f"""insert or ignore into Player (PlayerId, FirstName, LastName, PlayerSlug, Active, Position, Height, Weight, College, Country, DraftYear, DraftRound, DraftNumber, BirthDate, UpdatedAtSeason) 
        values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", players)
        self.conn.commit()

    def insert_awards(self, awards):
        self.conn.executemany(f"""insert or ignore into Awards (PlayerId, FullName, Jersey, Position, TeamId, TeamName, Description, AllNBATeamNumber, Season, DateAwarded, Confrence, AwardType, SubTypeA, SubTypeB, SubTypeC)
        values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", awards)
        self.conn.commit()

    def insert_bref_season_stats(self, players_stats):
        self.conn.executemany("""insert or ignore into BREFPlayerSeason (PlayerId, PlayerName, Season, LeagueName) VALUES (?, ?, ?, ?)""", players_stats)
        self.conn.commit()

    def insert_bref_draft_picks(self, draft_picks):
        self.conn.executemany("""insert or ignore into BREFDraftPick (PlayerId, PlayerName, Season, LeagueName, RoundNumber, PickNumber) VALUES (?, ?, ?, ?, ?, ?)""", draft_picks)
        self.conn.commit()

    def insert_players_mapping(self, players_mapping):
        self.conn.executemany("""insert or ignore into PlayerMapping (PlayerNbaId, PlayerNbaName, PlayerNbaBirthDate, PlayerBrefId, PlayerBrefName, PlayerBrefBirthDate) VALUES (?, ?, ?, ?, ?, ?)""", players_mapping)
        self.conn.commit()

    def update_players_table(self, players):
        self.conn.executemany(f"""update Player set FirstName=?, LastName=?, PlayerSlug=?, Active=?, Position=?, Height=?, Weight=?, College=?, Country=?, DraftYear=?, DraftRound=?, DraftNumber=?, UpdatedAtSeason=? 
        where PlayerId=?""", players)
        self.conn.commit()

    def update_players_birthdate(self, players_birthdates):
        self.conn.executemany(f"""update Player set BirthDate=? 
        where PlayerId=?""", players_birthdates)
        self.conn.commit()

    def save_odds_dataframe(self, df):
        self.insert_odds(list(df.to_records(index=False)))

    def save_boxscores(self, rows, headers, table_type):
        if not rows:
            return
        to_save = pd.DataFrame(data=rows, columns=headers)
        self.transform_boxscores(to_save)
        self.insert_boxscores(to_save.columns, list(to_save.to_records(index=False)), table_type)

    def save_pbps(self, rows, headers):
        self.insert_pbps(headers, rows)

    def save_summeries(self, summeries):
        self.insert_series_summary(summeries)

    def save_players(self, players):
        self.insert_players(players)

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
                TeamAId           integer,
                TeamAName         text,
                TeamBId           integer,
                TeamBName         text,
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
                TeamAId           integer,
                TeamAName         text,
                TeamBId           integer,
                TeamBName         text,
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
                TeamAId integer,
                TeamAName text,
                TeamBId integer,
                TeamBName text,
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
                ShotValue real,
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
                RealPossesionNumber integer,
                primary key (GameId, EventNumber)
            );""")
        self.conn.commit()

    def create_series_levels_table(self):
        self.conn.execute("""
            create table if not exists PlayoffSerieSummary
            (
                Season integer,
                TeamAId integer,
                TeamAName text,
                TeamBId integer,
                TeamBName text,
                TeamAWins integer,
                TeamBWins integer,
                WinnerId integer,
                WinnerName text,
                LoserId integer,
                LoserName text,
                SerieOrder integer,
                LevelTitle text,
                primary key (SEASON, TeamAId, TeamBId)
            )
        """)

    def create_players_table(self):
        self.conn.execute("""
            create table if not exists Player
            (
                PlayerId integer primary key,
                FirstName text,
                LastName text,
                FullName text generated always as ( FirstName || ' ' || LastName ) VIRTUAL,
                PlayerSlug text,
                Active integer,
                Position text,
                Height text,
                Weight text,
                College text,
                Country text,
                DraftYear integer,
                DraftRound integer,
                DraftNumber integer,
                BirthDate datetime,
                UpdatedAtSeason integer
            )
        """)
        self.conn.commit()

    def create_awards_and_honors_table(self):
        self.conn.execute("""
            create table if not exists Awards
            (
                PlayerId integer,
                FullName text,
                Jersey text,
                Position text,
                TeamId integer,
                TeamName text,
                Description text,
                AllNBATeamNumber integer,
                Season integer,
                DateAwarded datetime,
                Confrence text,
                AwardType text,
                SubTypeA text,
                SubTypeB text,
                SubTypeC text,
                unique (PlayerId, FullName, Position, Jersey, TeamId, Season, Description, DateAwarded)
            )
        """)
        self.conn.commit()

    def create_bref_season_player_stats_table(self):
        self.conn.execute("""
            create table if not exists BREFPlayerSeason
            (
                PlayerId text,
                PlayerName text,
                Season integer,
                LeagueName text,
                primary key (PlayerId, Season)
            )
        """)
        self.conn.commit()

    def create_bref_draft_table(self):
        self.conn.execute("""
            create table if not exists BREFDraftPick
            (
                PlayerId text,
                PlayerName text,
                Season integer,
                LeagueName text,
                RoundNumber integer,
                PickNumber integer,
                primary key (Season, RoundNumber, PickNumber),
                unique (PlayerId)
            )
        """)
        self.conn.commit()

    def create_players_ids_mapping(self):
        self.conn.execute("""
            create table if not exists PlayerMapping
            (
                PlayerNbaId integer primary key,
                PlayerNbaName text,
                PlayerNbaBirthDate date,
                PlayerBrefId text,
                PlayerBrefName text,
                PlayerBrefBirthDate
            )
        """)
        self.conn.commit()

    # returns the last saved date of some box score type plus 1 day(empty string if none found)
    def get_last_game_date(self, seaseon_type_code, table_type):
        tables = self.conn.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name=?""", [f'BoxScore{table_type}']).fetchall()
        if len(tables):
            res = self.conn.execute(f"""select {"GAME_DATE"} from {'BoxScore' + table_type} where {"SEASON_TYPE"}=? order by {"GAME_DATE"} desc limit 1""", [seaseon_type_code]).fetchall()
            return res[0][0] if res else ''
        return ''

    # returns the last saved year of odds plus 1 year(empty string if none found)
    def get_last_odds_year(self):
        tables = self.conn.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='Odds'""").fetchall()
        if tables:
            res = self.conn.execute(f"""select SEASON+1 from Odds order by SEASON desc limit 1""").fetchall()
            return res[0][0] if res else FIRST_ODDS_SEASON
        return FIRST_ODDS_SEASON

    def is_players_updated(self):
        tables = self.conn.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='Player'""").fetchall()
        if tables:
            res = self.conn.execute(f"""select UpdatedAtSeason from Player order by UpdatedAtSeason desc limit 1""").fetchall()
            if len(res) > 0:
                if res[0][0] >= LAST_SEASON:
                    return 2
                return 1
        return 0

    def get_games_without_events(self, season_type_code):
        tables = self.conn.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name=? or name=?""", [f'Event', 'BoxScoreT']).fetchall()
        if len(tables) > 1:
            res = self.conn.execute(f"""
            select distinct
                   BoxScoreT.GAME_ID,
                   first_value(TEAM_ID) over W1 as TeamAId,
                   first_value(TEAM_NAME) over W1 as TeamAName,
                   last_value(TEAM_ID) over W1 as TeamBId,
                   last_value(TEAM_NAME) over W1 as TeamBName
            from BoxScoreT
            left join Event on Event.GameId = BoxScoreT.GAME_ID
            where Event.GameId is null and BoxScoreT.SEASON_TYPE=? and ((SEASON_TYPE in (2, 4, 5) and SEASON >= 1996) or (SEASON_TYPE=3 and (SEASON=1997 or SEASON>=2003))) and WL is not null
            window W1 as (partition by GAME_ID order by TEAM_ID rows between unbounded preceding and unbounded following)""",
                                    [season_type_code]).fetchall()
            return res
        return []

    def fetch_br_seasons_links(self):
        if self.bref_seasons is not None:
            return self.bref_seasons
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
            to_ret.append([season_number, season_link, league_id])
        self.bref_seasons = to_ret
        return to_ret

    def fetch_br_drafts_links(self):
        if self.bref_drafts is not None:
            return self.bref_drafts
        url = 'https://www.basketball-reference.com/draft/'
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        seasons_rows = soup.select('#first_overall tr')
        seasons_rows = [s for s in seasons_rows if not s.has_attr('class')]
        to_ret = []
        for s in seasons_rows:
            season = s.select('[data-stat=\"draft\"] a')[0]
            season_number = int(season.getText())
            season_link = season['href']
            league_id = s.select('[data-stat=\"lg_id\"] a')[0].getText()
            to_ret.append([season_number, season_link, league_id])
        self.bref_drafts = to_ret
        return to_ret

    # download the resource represented by the handler
    def handle_cache(self, cache_handler):
        file_name = cache_handler.get_filename()
        if self.use_cache and os.path.isfile(CACHE_PATH + file_name):
            print(f"found {file_name} in cache.")
            with open(CACHE_PATH + file_name, "rb") as f:
                to_ret = cache_handler.load_file(f)
        else:
            if self.to_cache_missing_files and file_name in self.missing_files:
                print(f"file {file_name} is missing. skipping.")
                return None
            try:
                print(f'Downloading {file_name}...')
                to_ret = cache_handler.downloader()
                # time.sleep(1)
                print(f"Downloaded {file_name}.")
                if self.use_cache and cache_handler.to_cache(to_ret):
                    with open(CACHE_PATH + file_name, "w") as f2:
                        cache_handler.cache(to_ret, f2)
                    print(f"Cached {file_name}.")
            except ValueError:
                print(f'failed downloading {file_name}')
                self.cache_missing_file(file_name)
                return None
        return to_ret

    def cache_missing_file(self, file_name):
        if self.to_cache_missing_files:
            with open(CACHE_PATH + MISSING_FILES_FILE, "a") as f:
                f.write(file_name + "\n")

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
            game_date_index = headers.index("GAME_DATE")
            wl_index = headers.index('WL')
            if len(results) >= API_COUNT_THRESHOLD:
                count = 0
                last_date = results[-1][game_date_index]
                while results[-1][game_date_index] == last_date:
                    results.pop()
                    count = count+1
                print(f"popped last {count} items.")
                date_from = last_date
            else:
                continue_loop = False
            # take only boxscores that occured in the past(5 days should be enough i guess) or finished(WL is not null)
            results = [r for r in results if r[wl_index] is not None or (datetime.now() - datetime.strptime(r[game_date_index], '%Y-%m-%d')).days >= 5]

            self.save_boxscores(results, headers, box_score_type)

    # download and saves all events of a game
    def collect_all_game_events(self, game_id, teamaid, teamaname, teambid, teambname):
        handler = PBPCacheHandler(game_id)
        data = self.handle_cache(handler)
        if not data:
            return
        elif not data['resultSets'][0]['rowSet']:
            self.cache_missing_file(handler.get_filename())
            return
        try:
            transformed_events = EventMaker.transform_game_events(game_id, teamaid, teamaname, teambid, teambname, data)
        except HTTPError as e:
            print(f'failed transforming {game_id} events. try again later. error: {str(e)}')
            return
        headers = [
            'GameId',
            'TeamAId',
            'TeamAName',
            'TeamBId',
            'TeamBName',
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
            'EventOrder',
            'RealPossesionNumber'
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
        for gid, teamaid, teamaname, teambid, teambname in games_missing_events:
            print(f'updating events of game {gid}...')
            self.collect_all_game_events(gid, teamaid, teamaname, teambid, teambname)

    def update_all_missing_events(self):
        for season_type in SEASON_TYPES:
            self.update_missing_events(season_type)

    # updates(starts from the last saved date) all box scores of all season types of box score type
    def update_playoff_summary(self, season, season_link, current_teams):
        data = self.handle_cache(BRPlayoffsSummaryHandler(season, season_link, current_teams))
        self.save_summeries(data)

    def update_playoffs_summeries(self):
        current_teams = self.collect_teams()
        sql = """
            select Season, min(SerieOrder) as MaxLevel from PlayoffSerieSummary 
            group by Season
        """
        fetched_seasons = self.conn.execute(sql).fetchall()
        for s, order in fetched_seasons:
            if order > 1:
                self.conn.execute("""delete from PlayoffSerieSummary where Season=?""", [s])
                self.conn.commit()
        fetched_seasons = [s[0] for s in fetched_seasons if s[1] == 1]
        seasons = self.fetch_br_seasons_links()
        for season, season_link, league_id in seasons:
            if (league_id == 'BAA' or league_id == 'NBA') and season not in fetched_seasons:
                self.update_playoff_summary(season, season_link, current_teams)

    def update_players(self):
        data = self.handle_cache(PlayersHandler(LAST_SEASON))
        data = data['resultSets'][0]['rowSet']
        self.insert_players([[p[0], p[2], p[1], p[3], 1 if p[19] else 0, p[11], p[12], p[13], p[14], p[15], p[16], p[17], p[18], None, LAST_SEASON] for p in data])

    def update_players_birthdates(self):
        # this for some reason exist only in the player profile endpoint and the team roster endpoint.
        # instead of making a request for each player try to find a set of teams rosters which contains all players
        # this reduce the request to something around 1000(instead of 4000)
        teams_cover = get_teams_cover(self.conn)
        print(f'{len(teams_cover)} teams to cover...')
        for (season, tid), expected_players in teams_cover:
            handler = TeamRosterHandler(season, tid)
            data = self.handle_cache(handler)
            data = data['resultSets'][0]['rowSet']
            # players_ids = set([p[14] for p in data])
            # # print('expected ids: ', players_ids.intersection(expected_players))
            # # print('unexpected ids: ', players_ids - expected_players)
            # # print('expected and not found ids: ', expected_players - players_ids)
            players = [(datetime.strptime(p[10], '%b %d, %Y').isoformat(), p[14]) for p in data]
            self.update_players_birthdate(players)
        uncovered_players = self.conn.execute("""select PlayerId from Player where BirthDate is null""").fetchall()
        print(f'{len(uncovered_players)} players not covered. starting profile requests...')
        for pid in uncovered_players:
            handler = PlayerProfileHandler(pid)
            data = self.handle_cache(handler)
            data = data['resultSets'][0]['rowSet']
            self.update_players_birthdate([(data[0][7], data[0][0])])

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
        to_ret['Team'] = to_ret['Team'].map(ODDS_TEAM_NAMES).fillna(df['Team'])
        self.save_odds_dataframe(to_ret)

    def collect_hofs_and_retires(self):
        team_ids = self.conn.execute("""select distinct TEAM_ID from Teams""").fetchall()
        for (tid, ) in team_ids:
            handler = TeamDetailsHandler(tid)
            data = self.handle_cache(handler)
            data = data['resultSets']
            hof_data = data[6]['rowSet']
            retired_data = data[7]['rowSet']
            hof_awards = [[p[0] if p[0] else 0,
                           p[1],
                           '#',
                           '#',
                           0,
                           None,
                           'Hall of Fame Inductee',
                           None,
                           p[5] if p[5] else 0,
                           '',
                           None, 'Award', 'Hall of Fame', None, None] for p in hof_data]
            retired_honors = [[p[0] if p[0] else 0,
                               p[1],
                               p[3] if p[3] else '#',
                               p[2] if p[2] else '#',
                               tid,
                               None,
                               'Retired Jersey',
                               None,
                               p[5] if p[5] else 0,
                               '',
                               None, 'Honor', 'Retired Jersey', None, None] for p in retired_data]
            self.insert_awards(hof_awards + retired_honors)

    def collect_awards(self):
        self.collect_teams()

        def transform_award(award_row):
            full_name = award_row[1] + ' ' + award_row[2]
            season = int(award_row[6].split('-')[0]) if award_row[6] else 0
            team_id = [t[0] for t in self.current_teams if t[2] == award_row[3] and t[3] <= season <= t[4]] if award_row[3] else 0
            if award_row[3]:
                if len(team_id) == 0:
                    print(f'****************************************{award_row[3]} - {season}******************************')
                    team_id = award_row[3]
                else:
                    team_id = team_id[0]
            date_awarded = datetime.strptime(award_row[7], '%m/%d/%Y').isoformat() if award_row[7] else (award_row[8] if award_row[8] else '')
            return [award_row[0],
                    full_name,
                    '#',
                    '#',
                    team_id,
                    award_row[3],
                    award_row[4] if award_row[4] else '',
                    int(award_row[5]) if award_row[5] and award_row[5] != '(null)' else None,
                    season,
                    date_awarded,
                    award_row[9], award_row[10], award_row[11], award_row[12], award_row[13]]
        player_ids = self.conn.execute("""select distinct PlayerId from Player""").fetchall()
        for (pid, ) in player_ids:
            handler = PlayerAwardsHandler(pid)
            data = self.handle_cache(handler)
            data = data['resultSets'][0]['rowSet']
            awards = [transform_award(p) for p in data]
            self.insert_awards(awards)

    def collect_bref_players_single_season_stats(self, season, league_id):
        data = self.handle_cache(BREFSeasonStatsHandler(season, league_id))
        self.insert_bref_season_stats(data)

    def collect_bref_players_season_stats(self):
        self.fetch_br_seasons_links()
        sql = """
            select distinct Season, LeagueName from BREFPlayerSeason
        """
        fetched_seasons = self.conn.execute(sql).fetchall()
        seasons = self.fetch_br_seasons_links()
        for season, season_link, league_id in seasons:
            if (season, league_id) not in fetched_seasons:
                self.collect_bref_players_single_season_stats(season, league_id)

    def collect_bref_single_draft(self, season, league_id):
        data = self.handle_cache(BREFSeasonDraftHandler(season, league_id))
        self.insert_bref_draft_picks(data)

    def collect_bref_drafts(self):
        self.fetch_br_drafts_links()
        sql = """
            select distinct Season, LeagueName from BREFDraftPick
        """
        fetched_seasons = self.conn.execute(sql).fetchall()
        seasons = self.fetch_br_drafts_links()
        for season, season_link, league_id in seasons:
            if (season, league_id) not in fetched_seasons:
                self.collect_bref_single_draft(season, league_id)

    # updates(start form last saved year) odds
    def update_odds(self):
        last_saved_season = self.get_last_odds_year()
        print(f'updating odds... current last saved season: {last_saved_season if last_saved_season else "None"}')
        for i in range(last_saved_season, LAST_SEASON):
            print(f'downloading odds of season {i}...')
            self.collect_season_odds(i)

    def load_players_ids_mapping(self):
        sql = """select * from PlayerMapping limit 1"""
        res = self.conn.execute(sql).fetchall()
        if not res:
            with open('players_ids/players.csv', encoding='ISO-8859-1') as f:
                csvreader = csv.reader(f,)
                headers = next(csvreader)
                bref_id_idx = headers.index('BBRefID')
                bref_name_idx = headers.index('BBRefName')
                bref_birthdate_idx = headers.index('BBRefBirthDate')
                nba_id_idx = headers.index('NBAID')
                nba_name_idx = headers.index('NBAName')
                nba_birthdate_idx = headers.index('NBABirthDate')
                to_insert = []
                for p in csvreader:
                    if p[bref_id_idx] != 'NA' and p[nba_id_idx] != 'NA':
                        to_insert.append([int(p[nba_id_idx]),
                                          p[nba_name_idx] if p[nba_name_idx] != 'NA' else None,
                                          p[nba_birthdate_idx] if p[nba_birthdate_idx] != 'NA' else None,
                                          p[bref_id_idx],
                                          p[bref_name_idx] if p[bref_name_idx] != 'NA' else None,
                                          p[bref_birthdate_idx] if p[bref_birthdate_idx] != 'NA' else None])
                self.insert_players_mapping(to_insert)

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

    # the basic and common update
    def update_base(self):
        print('setting players table...')
        self.create_players_table()
        self.update_players()
        print('setting boxscore tables...')
        self.create_players_boxscores_table()
        self.create_teams_boxscores_table()
        self.update_boxscores_table('P')
        self.update_boxscores_table('T')
        print('setting playoff series table...')
        self.create_series_levels_table()
        self.update_playoffs_summeries()
        print('setting players mapping table...')
        self.create_players_ids_mapping()
        self.load_players_ids_mapping()

    def update_odds_database(self):
        print('setting odds table...')
        self.create_odds_table()
        self.update_odds()

    def update_hof_database(self):
        print('setting awards table...')
        self.create_awards_and_honors_table()
        self.collect_hofs_and_retires()

    def update_awards_database(self):
        print('setting awards table...')
        self.create_awards_and_honors_table()
        self.collect_awards()

    def update_events_database(self, option):
        print('setting pbps table')
        self.create_pbp_table()
        if option == 'all':
            self.update_all_missing_events()
        elif option == 'playoff':
            self.update_missing_events(SEASON_TYPES[2])
        elif option == 'regular':
            self.update_missing_events(SEASON_TYPES[0])
        elif option == 'allstar':
            self.update_missing_events(SEASON_TYPES[1])
        elif option == 'playin':
            self.update_missing_events(SEASON_TYPES[3])

    def update_bref_players_database(self):
        print('setting bref players tables...')
        self.create_bref_draft_table()
        self.create_bref_season_player_stats_table()
        self.collect_bref_players_season_stats()
        self.collect_bref_drafts()


def main():
    pbp.Patcher.foo()  # just for making sure formatter wont optimize out the Patcher import
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--cache', help='Cache downloaded files', default=False, action='store_true')
    parser.add_argument('-m', '--missing', help='Cache and ignore missing files', default=False, action='store_true')
    parser.add_argument('-o', '--odds', help='Update Odds table', default=False, action='store_true')
    parser.add_argument('-e', '--events', help='Update Events table', nargs='?', default=None, action='store', const='all')
    parser.add_argument('-b', '--birthdates', help='Update Players birthdates', default=False, action='store_true')
    parser.add_argument('-hof', '--hof', help='Update Hall of fame inductees and retired jersys players', default=False, action='store_true')
    parser.add_argument('-aw', '--awards', help='Update Players awards', default=False, action='store_true')
    parser.add_argument('-brefp', '--bref_players', help='Update BREF Players data', default=False, action='store_true')
    parser.add_argument('-lv', '--views_in', type=str, help='Load views from file(override other options)')
    parser.add_argument('-wv', '--views_out', type=str, help='Write views to file(override other options)')
    args = parser.parse_args()
    handler = DatabaseHandler(use_cache=args.cache, to_cache_missing_files=args.missing)
    if args.views_in is not None:
        handler.load_views(args.views_in)
    elif args.views_out is not None:
        handler.save_views(args.views_out)
    else:
        handler.update_base()
        if args.odds:
            handler.update_odds_database()
        if args.events:
            handler.update_events_database(args.events)
        if args.birthdates:
            handler.update_players_birthdates()
        if args.hof:
            handler.update_hof_database()
        if args.awards:
            handler.update_awards_database()
        if args.bref_players:
            handler.update_bref_players_database()

    # handler.fix_abbrs()


if __name__ == '__main__':
    main()
