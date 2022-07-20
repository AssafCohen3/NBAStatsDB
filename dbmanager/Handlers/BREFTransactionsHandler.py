from dbmanager.Handlers.HandlerAbs import HandlerAbs
from dbmanager.MainRequestsSession import requests_session as requests
from dbmanager.constants import *
from dbmanager.transactions.TransactionCreator import TransactionsCreator
from dbmanager.transactions.TransactionsAnalayzer import TransactionsAnalyzer
from dbmanager.transactions.TransactionsParser import TransactionsParser
from dbmanager.transactions.TransactionsScrapper import TransactionsScrapper


class BREFTransactionsHandler(HandlerAbs):
    def __init__(self, league, season, all_players_with_mapping):
        self.league = league
        self.season = season
        self.scrapper = TransactionsScrapper()
        self.parser = TransactionsParser()
        self.analyzer = TransactionsAnalyzer(all_players_with_mapping)
        self.creator = TransactionsCreator()
        self.resp = None

    def get_filename(self):
        return BREF_TRANSACTIONS_FILE_TEMPLATE % (self.league, self.season)

    def load_file(self, f):
        return self.from_html(f.read())

    def downloader(self):
        to_send = BREF_TRANSACTIONS_ENDPOINT % (self.league, self.season + 1)
        r = requests.get(to_send)
        self.resp = r.text
        return self.from_html(r.text)

    def from_html(self, html_resp):
        to_ret = []
        scrapped_transactions = self.scrapper.scrap_transactions(html_resp)
        for transaction_year, transaction_month, transaction_day, transaction_number, transaction_text, transaction_to_find in scrapped_transactions:
            transaction_type, parsed_transaction = self.parser.parse_transaction(transaction_text)
            if transaction_type is None:
                continue
            analyzed_transaction = self.analyzer.analyze_transaction(self.season, parsed_transaction, transaction_type, transaction_to_find)
            transactions_to_add = self.creator.create_transaction(analyzed_transaction, transaction_text, transaction_type, self.season, transaction_year, transaction_month, transaction_day, transaction_number)
            to_ret.extend(transactions_to_add)
        self.ensure_no_duplicates(to_ret)
        self.ensure_no_nulls(to_ret)
        to_ret = [[
            t['season'],
            t['year'],
            t['month'],
            t['day'],
            t['transaction_number'],
            t['team_a_nba_id'],
            t['team_a_nba_name'],
            t['team_a_bref_abbr'],
            t['team_a_bref_name'],
            t['team_b_nba_id'],
            t['team_b_nba_name'],
            t['team_b_bref_abbr'],
            t['team_b_bref_name'],
            t['player_nba_id'],
            t['player_nba_name'],
            t['player_bref_id'],
            t['player_bref_name'],
            t['person_bref_id'],
            t['person_bref_name'],
            t['person_role'],
            t['transaction_type'],
            t['action_type'],
            t['sub_type_a'],
            t['sub_type_b'],
            t['sub_type_c'],
            1 if t['on_team_a_after'] else 0,
            1 if t['on_team_b_after'] else 0,
            t['pick_year'],
            t['pick_round'],
            t['picks_number'],
            t['tradee_type'],
            t['additional']
        ] for t in to_ret]
        return to_ret

    def ensure_no_duplicates(self, transactions):
        dups = {}
        for t in transactions:
            key = self.get_transaction_key(t)
            if key not in dups:
                dups[key] = 0
            dups[key] = dups[key] + 1
        fail = False
        for t in transactions:
            key = self.get_transaction_key(t)
            if dups[key] > 1:
                print(t)
                print(dups[key])
                fail = True
        if fail:
            raise Exception('duplicate transactions')

    def ensure_no_nulls(self, transactions):
        fail = False
        for t in transactions:
            t_non_nulls = self.get_non_nulls(t)
            t_nulls = [nn for nn in t_non_nulls if nn is None]
            if t_nulls:
                print(f'{t} contains nulls: {t_nulls}')
                fail = True
        if fail:
            raise Exception('non null is null')

    @staticmethod
    def get_transaction_key(t):
        return t['season'], t['year'], t['month'], t['day'], t['transaction_number'], t['team_a_bref_abbr'], t['team_b_bref_abbr'], \
               t['player_bref_id'], t['player_bref_name'], t['person_bref_id'], t['person_bref_name'], t['transaction_type'], t['pick_year'], t['pick_round'], t['tradee_type'], t['additional']

    @staticmethod
    def get_non_nulls(t):
        return t['season'], t['year'], t['month'], t['day'], t['transaction_number'], \
               t['team_a_nba_id'], t['team_a_bref_abbr'], t['team_a_bref_name'], t['team_b_nba_id'], t['team_b_bref_abbr'], t['team_b_bref_name'], \
               t['player_nba_id'],\
               t['player_bref_id'], t['player_bref_name'], t['person_bref_id'], t['person_bref_name'], t['transaction_type'], \
               t['action_type'], t['sub_type_a'], t['on_team_a_after'], t['on_team_b_after'], \
               t['pick_year'], t['pick_round'], t['picks_number'], t['tradee_type'], t['additional']

    def to_cache(self, data):
        return True

    def cache(self, data, f):
        f.write(self.resp)
