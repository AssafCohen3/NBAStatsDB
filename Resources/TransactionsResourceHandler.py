from alive_progress import alive_it
from sqlalchemy import delete
from Database.Models.Transactions import Transactions
from Handlers.BREFTransactionsHandler import BREFTransactionsHandler
from Resources.ResourceAbc import ResourceAbc
from sqlalchemy.dialects.sqlite import insert


class TransactionsResourceHandler(ResourceAbc):

    def __init__(self, session, bref_players, br_seasons_links):
        self.bref_players = bref_players
        self.br_seasons_links = br_seasons_links
        self.transaction_headers = [
            'Season',
            'Year',
            'Month',
            'Day',
            'TransactionNumber',
            'TeamANBAId',
            'TeamANBAName',
            'TeamABREFAbbr',
            'TeamABREFName',
            'TeamBNBAId',
            'TeamBNBAName',
            'TeamBBREFAbbr',
            'TeamBBREFName',
            'PlayerNBAId',
            'PlayerNBAName',
            'PlayerBREFId',
            'PlayerBREFName',
            'PersonBREFId',
            'PersonBREFName',
            'PersonRole',
            'TransactionType',
            'ActionType',
            'SubTypeA',
            'SubTypeB',
            'SubTypeC',
            'OnTeamAAfter',
            'OnTeamBAfter',
            'PickYear',
            'PickRound',
            'PicksNumber',
            'TradeeType',
            'Additional'
        ]
        super().__init__(session)

    def insert_transactions(self, transactions):
        if not transactions:
            return
        stmt = insert(Transactions)
        self.session.execute(stmt, transactions)
        self.session.commit()

    def collect_bref_season_transactions(self, league_id, season):
        stmt = delete(Transactions).where(Transactions.Season == season)
        self.session.execute(stmt)
        self.session.commit()
        handler = BREFTransactionsHandler(league_id, season, self.bref_players)
        transactions = handler.downloader()
        transactions = [dict(zip(self.transaction_headers, t)) for t in transactions]
        self.insert_transactions(transactions)

    def collect_all_bref_transactions(self, seasons_to_collect=None):
        to_fetch = [(season, season_link, league_id) for season, season_link, league_id in self.br_seasons_links
                    if (league_id == 'BAA' or league_id == 'NBA') and (not seasons_to_collect or season in seasons_to_collect)]
        if len(to_fetch) == 0:
            return
        to_iterate = alive_it(to_fetch, force_tty=True, title="Fetching Transactions", enrich_print=False, dual_line=True)
        for season, season_link, league_id in to_iterate:
            to_iterate.text(f'-> Fetching {season} transactions...')
            self.collect_bref_season_transactions(league_id, season)
