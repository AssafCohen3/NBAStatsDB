from abc import ABC
from typing import Optional, List, Union, Type

from sqlalchemy import delete, insert
from sqlalchemy.orm import scoped_session

from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.BREFTransaction import BREFTransaction
from dbmanager.Downloaders.BREFTransactionsDownloader import BREFTransactionsDownloader
from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc
from dbmanager.Resources.ActionSpecifications.BREFTransactionsActionSpecs import DownloadAllTransactions, \
    DownloadTransactionsInSeasonsRange
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.SharedData.BREFSeasonsLinks import BREFSeasonLink, bref_seasons_links
from dbmanager.SharedData.LiveBREFPlayersIndex import live_bref_players_index
from dbmanager.transactions.TransactionCreator import TransactionsCreator
from dbmanager.transactions.TransactionsAnalayzer import TransactionsAnalyzer, BREFPlayerMinimal
from dbmanager.transactions.TransactionsParser import TransactionsParser
from dbmanager.transactions.TransactionsScrapper import TransactionsScrapper
from dbmanager.utils import iterate_with_next


def get_transaction_key(t):
    return t['season'], t['year'], t['month'], t['day'], t['transaction_number'], t['team_a_bref_abbr'], t[
        'team_b_bref_abbr'], \
           t['player_bref_id'], t['player_bref_name'], t['person_bref_id'], t['person_bref_name'], t[
               'transaction_type'], t['pick_year'], t['pick_round'], t['tradee_type'], t['additional']


def get_non_nulls(t):
    return t['season'], t['year'], t['month'], t['day'], t['transaction_number'], \
           t['team_a_nba_id'], t['team_a_bref_abbr'], t['team_a_bref_name'], t['team_b_nba_id'], t['team_b_bref_abbr'], \
           t['team_b_bref_name'], \
           t['player_bref_id'], t['player_bref_name'], t['person_bref_id'], t['person_bref_name'], t[
               'transaction_type'], \
           t['action_type'], t['sub_type_a'], t['on_team_a_after'], t['on_team_b_after'], \
           t['pick_year'], t['pick_round'], t['picks_number'], t['tradee_type'], t['additional']


def ensure_no_duplicates(transactions):
    dups = {}
    for t in transactions:
        key = get_transaction_key(t)
        if key not in dups:
            dups[key] = 0
        dups[key] = dups[key] + 1
    fail = False
    for t in transactions:
        key = get_transaction_key(t)
        if dups[key] > 1:
            print(t)
            print(dups[key])
            fail = True
    if fail:
        raise Exception('duplicate transactions')


def ensure_no_nulls(transactions):
    fail = False
    for t in transactions:
        t_non_nulls = get_non_nulls(t)
        t_nulls = [nn for nn in t_non_nulls if nn is None]
        if t_nulls:
            print(f'{t} contains nulls: {t_nulls}')
            fail = True
    if fail:
        raise Exception('non null is null')


class GeneralDownloadTransactionsAction(ActionAbc, ABC):
    def __init__(self, session: scoped_session, start_season: Optional[int], end_season: Optional[int]):
        super().__init__(session)
        self.start_season = start_season
        self.end_season = end_season
        self.seasons_to_collect: List[BREFSeasonLink] = bref_seasons_links.get_nba_seasons_in_range(start_season, end_season)
        self.current_season: Optional[BREFSeasonLink] = self.seasons_to_collect[0] if self.seasons_to_collect else None
        self.scrapper = TransactionsScrapper()
        self.parser = TransactionsParser()
        self.analyzer = TransactionsAnalyzer(self.get_bref_player_by_id, self.get_bref_player_by_name_and_season)
        self.creator = TransactionsCreator()

    def get_bref_player_by_id(self, player_id: str) -> Optional[BREFPlayerMinimal]:
        res = live_bref_players_index.get_bref_player_by_id(self.session, player_id)
        return BREFPlayerMinimal(res.player_id, res.player_name) if res else None

    def get_bref_player_by_name_and_season(self, player_name: str, season: int) -> List[BREFPlayerMinimal]:
        res = live_bref_players_index.get_bref_player_by_name_and_season(self.session, player_name, season)
        return [BREFPlayerMinimal(p.player_id, p.player_name) for p in res]

    def insert_transactions(self, season: int, transactions: List[dict]):
        delete_stmt = delete(BREFTransaction).where(BREFTransaction.Season == season)
        self.session.execute(delete_stmt)
        if transactions:
            stmt = insert(BREFTransaction)
            self.session.execute(stmt, transactions)
        self.session.commit()
        self.update_resource()

    def collect_season_transactions(self, season: BREFSeasonLink):
        to_insert = []
        downloader = BREFTransactionsDownloader(season.leagu_id, season.season)
        transactions_html = downloader.download()
        scrapped_transactions = self.scrapper.scrap_transactions(transactions_html)
        try:
            for transaction_year, transaction_month, transaction_day, transaction_number, transaction_text, transaction_to_find in scrapped_transactions:
                if transaction_month == 9:
                    a = 555
                transaction_type, parsed_transaction = self.parser.parse_transaction(transaction_text)
                if transaction_type is None:
                    continue
                analyzed_transaction = self.analyzer.analyze_transaction(season.season, parsed_transaction, transaction_type, transaction_to_find)
                transactions_to_add = self.creator.create_transaction(analyzed_transaction, transaction_text, transaction_type, season.season, transaction_year, transaction_month, transaction_day, transaction_number)
                to_insert.extend(transactions_to_add)
        except Exception as e:
            raise e
        ensure_no_duplicates(to_insert)
        ensure_no_nulls(to_insert)
        transactions_to_insert = [{
            'Season': t['season'],
            'Year': t['year'],
            'Month': t['month'],
            'Day': t['day'],
            'TransactionNumber': t['transaction_number'],
            'TeamANBAId': t['team_a_nba_id'],
            'TeamANBAName': t['team_a_nba_name'],
            'TeamABREFAbbr': t['team_a_bref_abbr'],
            'TeamABREFName': t['team_a_bref_name'],
            'TeamBNBAId': t['team_b_nba_id'],
            'TeamBNBAName': t['team_b_nba_name'],
            'TeamBBREFAbbr': t['team_b_bref_abbr'],
            'TeamBBREFName': t['team_b_bref_name'],
            'PlayerBREFId': t['player_bref_id'],
            'PlayerBREFName': t['player_bref_name'],
            'PersonBREFId': t['person_bref_id'],
            'PersonBREFName': t['person_bref_name'],
            'PersonRole': t['person_role'],
            'TransactionType': t['transaction_type'],
            'ActionType': t['action_type'],
            'SubTypeA': t['sub_type_a'],
            'SubTypeB': t['sub_type_b'],
            'SubTypeC': t['sub_type_c'],
            'OnTeamAAfter': 1 if t['on_team_a_after'] else 0,
            'OnTeamBAfter': 1 if t['on_team_b_after'] else 0,
            'PickYear': t['pick_year'],
            'PickRound': t['pick_round'],
            'PicksNumber': t['picks_number'],
            'TradeeType': t['tradee_type'],
            'Additional': t['additional'],
        } for t in to_insert]
        self.insert_transactions(season.season, transactions_to_insert)

    async def action(self):
        for season, next_season in iterate_with_next(self.seasons_to_collect):
            self.collect_season_transactions(season)
            self.current_season = next_season
            await self.finish_subtask()

    def subtasks_count(self) -> Union[int, None]:
        return len(self.seasons_to_collect)

    def get_current_subtask_text_abs(self) -> str:
        # downloading {season} transactions
        return gettext('resources.bref_transactions.actions.download_transactions.downloading_transactions',
                       season=self.current_season.season if self.current_season else '')


class DownloadAllTransactionsAction(GeneralDownloadTransactionsAction):
    def __init__(self, session: scoped_session):
        super().__init__(session, None, None)

    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return DownloadAllTransactions


class DownloadTransactionsInSeasonsRangeAction(GeneralDownloadTransactionsAction):
    def __init__(self, session: scoped_session, start_season: int, end_season: int):
        super().__init__(session, start_season, end_season)

    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return DownloadTransactionsInSeasonsRange
