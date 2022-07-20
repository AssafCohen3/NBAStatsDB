import string

from alive_progress import alive_it
from sqlalchemy import func
from sqlalchemy.sql import select

from dbmanager.Database.Models.BREFPlayer import BREFPlayer
from dbmanager.Database.Models.BoxScoreP import BoxScoreP
from dbmanager.Database.Models.PlayerMapping import PlayerMapping
from dbmanager.Handlers.BREFPlayers import BREFPlayerHandler
from dbmanager.Resources.ResourceAbc import ResourceAbc
from sqlalchemy.dialects.sqlite import insert


class BREFPlayerResourceHandler(ResourceAbc):

    def insert_bref_players(self, bref_players):
        if not bref_players:
            return
        insert_stmt = insert(BREFPlayer)
        stmt = insert_stmt.on_conflict_do_update(set_={
            c.name: c for c in insert_stmt.excluded
        })
        self.session.execute(stmt, bref_players)
        self.session.commit()

    def collect_bref_players_by_letter(self, letter):
        headers = [
            'PlayerId',
            'PlayerName',
            'FromYear',
            'ToYear',
            'Position',
            'Height',
            'Weight',
            'Birthdate',
            'Active',
            'HOF'
        ]
        handler = BREFPlayerHandler(letter)
        data = handler.downloader()
        data = [dict(zip(headers, p)) for p in data]
        self.insert_bref_players(data)

    def collect_bref_players(self):
        headers = [
            'PlayerId',
            'PlayerName',
            'FromYear',
            'ToYear',
            'Position',
            'Height',
            'Weight',
            'Birthdate',
            'Active',
            'HOF'
        ]
        for letter in string.ascii_lowercase:
            handler = BREFPlayerHandler(letter)
            data = handler.downloader()
            data = [dict(zip(headers, p)) for p in data]
            self.insert_bref_players(data)

    def complete_missing_players_data(self):
        missing_players_cte = (
            select(PlayerMapping.PlayerBREFId).
            outerjoin(BREFPlayer, PlayerMapping.PlayerBREFId == BREFPlayer.PlayerId).
            outerjoin(BoxScoreP, PlayerMapping.PlayerNBAId == BoxScoreP.PlayerId).
            where(BREFPlayer.PlayerId.is_(None)).
            group_by(PlayerMapping.PlayerNBAId).
            having(func.count(BoxScoreP.GameId) > 0).
            cte()
        )
        stmt = select(func.substring(missing_players_cte.c.PlayerBREFId, 1, 1)).distinct()
        missing_letters = self.session.execute(stmt).fetchall()
        print(f'{len(missing_letters)} players page to fetch')
        if len(missing_letters) == 0:
            return
        for (letter, ) in alive_it(missing_letters, force_tty=True, title='Fetching BREF Players pages', enrich_print=False):
            self.collect_bref_players_by_letter(letter)

    def update_bref_players_table(self):
        print('updating bref players table')
        self.complete_missing_players_data()
