import csv
import sqlite3
import subprocess
from builtins import RuntimeError

import dbmanager.MainRequestsSession
from dbmanager.MainRequestsSession import requests_session as requests
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session
from dbmanager.Database.Models.BREFPlayer import BREFPlayer
from dbmanager.Database.Models.BoxScoreT import BoxScoreT
from dbmanager.Database.Models.PlayerMapping import PlayerMapping
from dbmanager.Resources.AwardsResourceHandler import AwardsResourceHandler
from dbmanager.Resources.BREFPlayerResourceHandler import BREFPlayerResourceHandler
from dbmanager.Resources.EventResourceHandler import EventResourceHandler
from dbmanager.Resources.HonoursResourceHandler import HonoursResourceHandler
from dbmanager.Resources.OddsResourceHandler import OddsResourceHandler
from dbmanager.Resources.PlayerBirthdateResourceHandler import PlayerBirthdateResourceHandler
from dbmanager.Resources.PlayerBoxScoreResourceHandler import PlayerBoxScoreResourceHandler
from dbmanager.Resources.PlayerBoxScoreStartersResourceHandler import PlayerBoxScoreStartersResourceHandler
from dbmanager.Resources.PlayerMappingResourceHandler import PlayerMappingResourceHandler
from dbmanager.Resources.PlayerResourceHandler import PlayerResourceHandler
from dbmanager.Resources.PlayoffSerieSummaryResourceHandler import PlayoffSerieSummaryResourceHandler
from dbmanager.Resources.TeamBoxScoreResourceHandler import TeamBoxScoreResourceHandler
from dbmanager.Resources.TransactionsResourceHandler import TransactionsResourceHandler
from dbmanager.base import Base
import dbmanager.Database.Models
import re
from bs4 import BeautifulSoup
import argparse
#  very important for pbp. fix some issues
import dbmanager.pbp.Patcher
from dbmanager.constants import *
import dbmanager.RequestsLogger
import logging


class NbaStatsDB:
    def __init__(self):
        self.current_teams = None
        self.bref_seasons = None
        self.bref_drafts = None
        self.players_mapper = None
        self.bref_players = None
        self.engine = create_engine('sqlite:///' + 'dbmanager/' + DATABASE_PATH + DATABASE_NAME_NEW + '.sqlite')
        self.session = Session(self.engine)
        self.players_boxscores_handler = None
        self.players_boxscores_starters_handler = None
        self.teams_boxscores_handler = None
        self.event_handler = None
        self.odds_handler = None
        self.playoff_series_summary_handler = None
        self.players_handler = None
        self.players_birthdate_handler = None
        self.awards_handler = None
        self.honours_handler = None
        self.mappings_handler = None
        self.bref_players_handler = None
        self.transactions_handler = None

    def get_players_boxscores_handler(self):
        if not self.players_boxscores_handler:
            self.players_boxscores_handler = PlayerBoxScoreResourceHandler(self.session)
        return self.players_boxscores_handler

    def get_players_boxscores_starters_handler(self):
        if not self.players_boxscores_starters_handler:
            self.players_boxscores_starters_handler = PlayerBoxScoreStartersResourceHandler(self.session, self.map_players())
        return self.players_boxscores_starters_handler

    def get_teams_boxscores_handler(self):
        if not self.teams_boxscores_handler:
            self.teams_boxscores_handler = TeamBoxScoreResourceHandler(self.session)
        return self.teams_boxscores_handler

    def get_event_handler(self):
        if not self.event_handler:
            self.event_handler = EventResourceHandler(self.session)
        return self.event_handler

    def get_odds_handler(self):
        if not self.odds_handler:
            self.odds_handler = OddsResourceHandler(self.session)
        return self.odds_handler

    def get_playoff_series_summary_handler(self):
        if not self.playoff_series_summary_handler:
            self.playoff_series_summary_handler = PlayoffSerieSummaryResourceHandler(self.session, self.collect_teams(), self.fetch_br_seasons_links())
        return self.playoff_series_summary_handler

    def get_players_handler(self):
        if not self.players_handler:
            self.players_handler = PlayerResourceHandler(self.session)
        return self.players_handler

    def get_players_birthdate_handler(self):
        if not self.players_birthdate_handler:
            self.players_birthdate_handler = PlayerBirthdateResourceHandler(self.session)
        return self.players_birthdate_handler

    def get_awards_handler(self):
        if not self.awards_handler:
            self.awards_handler = AwardsResourceHandler(self.session, self.collect_teams())
        return self.awards_handler

    def get_honours_handler(self):
        if not self.honours_handler:
            self.honours_handler = HonoursResourceHandler(self.session)
        return self.honours_handler

    def get_mappings_handler(self):
        if not self.mappings_handler:
            self.mappings_handler = PlayerMappingResourceHandler(self.session)
        return self.mappings_handler

    def get_bref_players_handler(self):
        if not self.bref_players_handler:
            self.bref_players_handler = BREFPlayerResourceHandler(self.session)
        return self.bref_players_handler

    def get_transactions_handler(self):
        if not self.transactions_handler:
            self.transactions_handler = TransactionsResourceHandler(self.session, self.load_bref_players(), self.fetch_br_seasons_links())
        return self.transactions_handler

    def collect_teams(self):
        if self.current_teams is not None:
            return self.current_teams
        teams_seasons_cte = (
            select(BoxScoreT.Season, BoxScoreT.TeamId, BoxScoreT.TeamAbbreviation, BoxScoreT.TeamName).
            group_by(BoxScoreT.Season, BoxScoreT.TeamId, BoxScoreT.TeamName, BoxScoreT.TeamAbbreviation).
            cte()
        )
        teams_seasons_with_previous_season_cte = (
            select(teams_seasons_cte,
                   func.row_number().over(partition_by=[teams_seasons_cte.c.TeamId, teams_seasons_cte.c.TeamName, teams_seasons_cte.c.TeamAbbreviation],
                                          order_by=[teams_seasons_cte.c.Season]).label('SeasonNumber')).
            cte()
        )
        stmt = (
            select(teams_seasons_with_previous_season_cte.c.TeamId, teams_seasons_with_previous_season_cte.c.TeamAbbreviation, teams_seasons_with_previous_season_cte.c.TeamName,
                   func.min(teams_seasons_with_previous_season_cte.c.Season).label('FirstSeason'),
                   func.max(teams_seasons_with_previous_season_cte.c.Season).label('LastSeason')).
            group_by(teams_seasons_with_previous_season_cte.c.TeamId, teams_seasons_with_previous_season_cte.c.TeamAbbreviation, teams_seasons_with_previous_season_cte.c.TeamName,
                     teams_seasons_with_previous_season_cte.c.Season - teams_seasons_with_previous_season_cte.c.SeasonNumber).
            order_by('FirstSeason')
        )
        res = self.session.execute(stmt).fetchall()
        self.current_teams = res
        return res

    def map_players(self):
        if self.players_mapper is not None:
            return self.players_mapper
        stmt = select(PlayerMapping.PlayerBREFId, PlayerMapping.PlayerNBAId)
        res = self.session.execute(stmt).fetchall()
        res = {bref_id: nba_id for bref_id, nba_id in res}
        self.players_mapper = res
        return self.players_mapper

    def load_bref_players(self):
        if self.bref_players is not None:
            return self.bref_players
        stmt = (
            select(BREFPlayer.PlayerId, BREFPlayer.PlayerName, BREFPlayer.FromYear, BREFPlayer.ToYear,
                   func.coalesce(PlayerMapping.PlayerNBAId, 0), PlayerMapping.PlayerNBAName).
            outerjoin(PlayerMapping, PlayerMapping.PlayerBREFId == BREFPlayer.PlayerId)
        )
        res = self.session.execute(stmt).fetchall()
        self.bref_players = res
        return res

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

    def export_mappings(self, output_file):
        current_mappings = self.session.execute(Base.metadata.tables['PlayerMapping'].select()).fetchall()
        with open(output_file, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['PlayerNBAId', 'PlayerNBAName', 'PlayerNBABirthDate', 'PlayerBREFId', 'PlayerBREFName', 'PlayerBREFBirthDate'])
            writer.writerows(current_mappings)

    def run_base(self):
        self.get_players_boxscores_handler().update_boxscores_table()
        self.get_teams_boxscores_handler().update_boxscores_table()
        self.get_players_handler().update_players_table()
        self.get_playoff_series_summary_handler().update_playoffs_summeries()
        self.get_mappings_handler().update_mappings_table()
        self.get_bref_players_handler().update_bref_players_table()

    def run_events(self, option):
        event_resource_handler = self.get_event_handler()
        if option == 'all':
            event_resource_handler.update_all_missing_events()
        elif option == 'playoff':
            event_resource_handler.update_missing_events(SEASON_TYPES[2])
        elif option == 'regular':
            event_resource_handler.update_missing_events(SEASON_TYPES[0])
        elif option == 'allstar':
            event_resource_handler.update_missing_events(SEASON_TYPES[1])
        elif option == 'playin':
            event_resource_handler.update_missing_events(SEASON_TYPES[3])

    def run_transactions(self, season):
        if season == 'all':
            self.get_transactions_handler().collect_all_bref_transactions()
        else:
            season = int(season)
            self.get_transactions_handler().collect_all_bref_transactions([season])

    def run_awards(self, award_arg):
        if award_arg == 'all':
            self.get_awards_handler().collect_all_awards()
        elif award_arg == 'active':
            self.get_awards_handler().collect_active_awards()
        else:
            try:
                player_id = int(award_arg)
                self.get_awards_handler().collect_player_awards(player_id)
            except ValueError:
                print(f'{award_arg} is not a valid player id')

    def run(self, args):
        if args.debug_requests:
            # this will log every request
            logging.getLogger('urllib3.connectionpool').addHandler(dbmanager.RequestsLogger.MyLoggingHandler())
            logging.getLogger('urllib3.connectionpool').setLevel(logging.DEBUG)
        print('setting tables...')
        Base.metadata.create_all(self.engine)
        if args.browse:
            p = subprocess.Popen(['sqlite_web', 'Database/boxscores_full_database_new.sqlite'])
            _, _ = p.communicate()
        elif args.export_mappings:
            self.export_mappings(args.export_mappings)
        elif args.views_in:
            self.load_views(args.views_in)
        elif args.views_out:
            self.save_views(args.views_out)
        else:
            self.run_base()
            if args.events:
                self.run_events(args.events)
            if args.odds:
                self.get_odds_handler().update_odds()
            if args.birthdates:
                self.get_players_birthdate_handler().update_players_birthdates()
            if args.hof:
                self.get_honours_handler().collect_hofs_and_retires()
            if args.awards:
                self.run_awards(args.awards)
            if args.transactions:
                self.run_transactions(args.transactions)
            if args.starters:
                self.get_players_boxscores_starters_handler().collect_bref_starters()

    def load_views(self, views_file):
        with open(views_file, 'r') as f:
            cmd = f.read()
        self.session.connection().connection.connection.executescript(cmd)
        self.session.commit()
        print(f'loaded successfully {cmd.count("CREATE VIEW IF NOT EXISTS")} views.')

    def save_views(self, file_name):
        sqls = self.session.execute("""select sql || ';' from sqlite_master where type = 'view'""").fetchall()
        output = '\n'.join(row[0].replace('CREATE VIEW', 'CREATE VIEW IF NOT EXISTS') for row in sqls)
        with open(file_name, 'w') as f:
            f.write(output)
        print(f'written successfully {len(sqls)} views.')

    def finish(self):
        self.session.close()


def validate_sqlite():
    sqlite_version = sqlite3.sqlite_version
    sqlite_version = tuple([int(p) for p in sqlite_version.split('.')])
    if sqlite_version < SQLITE_MIN_VERSION:
        raise RuntimeError(f'sqlite3 version should be 3.31 or higher. your version: {sqlite_version}')


def main():
    validate_sqlite()
    dbmanager.pbp.Patcher.foo()  # just for making sure formatter wont optimize out the Patcher import
    dbmanager.Database.Models.foo()  # just for making sure formatter wont optimize out the tables import
    dbmanager.MainRequestsSession.foo()  # just for making sure formatter wont optimize out the session import
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug_requests', help='log HTTP requests', default=False, action='store_true')
    parser.add_argument('-o', '--odds', help='Update Odds table', default=False, action='store_true')
    parser.add_argument('-e', '--events', help='Update Events table', nargs='?', default=None, action='store', const='all')
    parser.add_argument('-b', '--birthdates', help='Update Players birthdates', default=False, action='store_true')
    parser.add_argument('-hof', '--hof', help='Update Hall of fame inductees and retired jersys players', default=False, action='store_true')
    parser.add_argument('-aw', '--awards', help='Update Players awards', nargs='?', default=None, action='store', const='all')
    parser.add_argument('-starters', '--starters', help='Update Starters data from BREF', default=False, action='store_true')
    parser.add_argument('-t', '--transactions', help='Update BREF Transactions table', nargs='?', default=None, action='store', const='all')
    parser.add_argument('-lv', '--views_in', type=str, help='Load views from file(override other options). Only Load Trusted files!!!')
    parser.add_argument('-wv', '--views_out', type=str, help='Write views to file(override other options)')
    parser.add_argument('-browse', '--browse', help='open sqlite browser(override other options)', default=False, action='store_true')
    parser.add_argument('-em', '--export_mappings', type=str, help='export current saved mappings to a file(override other options)')

    args = parser.parse_args()
    handler = NbaStatsDB()
    handler.run(args)
    handler.finish()


if __name__ == '__main__':
    main()
