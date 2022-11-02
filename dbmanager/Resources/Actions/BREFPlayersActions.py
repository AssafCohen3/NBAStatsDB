import datetime
import string
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Union, Type, List, Optional

from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import scoped_session
from unidecode import unidecode

from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.BREFPlayer import BREFPlayer
from dbmanager.Database.Models.PlayerMapping import PlayerMapping
from dbmanager.Downloaders.BREFPlayerPageDownloader import BREFPlayerPageDownloader
from dbmanager.Downloaders.BREFPlayersDownloader import BREFPlayersDownloader
from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc
from dbmanager.Resources.ActionSpecifications.BREFPlayersActionSpecs import UpdateBREFPlayers, RedownloadBREFPlayers
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.utils import iterate_with_next
from dbmanager.tasks.RetryManager import retry_wrapper


@dataclass
class PlayerToDownlad:
    player_nba_id: int
    player_bref_id: str
    player_nba_name: str


class UpdateBREFPlayersGeneralAction(ActionAbc, ABC):

    def __init__(self, session: scoped_session, complete_index: bool):
        super().__init__(session)
        self.complete_index = complete_index
        self.missing_letters: List[str] = []
        self.current_letter = ''
        self.missing_players: List[PlayerToDownlad] = []
        self.current_player: Optional[PlayerToDownlad] = None

    def init_task_data_abs(self) -> bool:
        self.missing_letters = self.get_letters_to_fetch()
        self.current_letter = self.missing_letters[0] if self.missing_letters else ''
        return len(self.missing_letters) > 0

    def insert_bref_players(self, bref_players):
        if not bref_players:
            return
        insert_stmt = insert(BREFPlayer)
        stmt = insert_stmt.on_conflict_do_update(set_={
            c.name: c for c in insert_stmt.excluded
        })
        self.session.execute(stmt, bref_players)
        self.session.commit()
        self.update_resource()

    def get_missing_players(self) -> List[PlayerToDownlad]:
        missing_players_stmt = (
            select(PlayerMapping.PlayerNBAId, PlayerMapping.PlayerBREFId, PlayerMapping.PlayerNBAName).
            outerjoin(BREFPlayer, PlayerMapping.PlayerBREFId == BREFPlayer.PlayerId).
            where(BREFPlayer.PlayerId.is_(None)).
            group_by(PlayerMapping.PlayerNBAId)
        )
        missing_players = self.session.execute(missing_players_stmt).fetchall()
        return [PlayerToDownlad(*p) for p in missing_players]

    @retry_wrapper
    async def collect_bref_player_from_page(self, player: PlayerToDownlad):
        downloader = BREFPlayerPageDownloader(player.player_bref_id)
        resp = downloader.download()
        soup = BeautifulSoup(resp, 'html.parser')
        meta_div = soup.select('#meta')[0]
        player_name = unidecode(meta_div.select('h1 span')[0].getText())
        per_game_links = soup.select('table#per_game tbody tr [data-stat="season"] a')
        from_season = int(per_game_links[0].getText().split('-')[0]) if per_game_links else None
        to_season = int(per_game_links[-1].getText().split('-')[0]) if per_game_links else None
        position_paragraph_idx = None
        paragraphs = meta_div.select('p')
        for i, p in enumerate(paragraphs):
            p_strong_first = p.select('strong')
            if p_strong_first:
                p_strong_first = p_strong_first[0]
                if p_strong_first.getText().strip() == 'Position:':
                    position_paragraph_idx = i
                    break
        position = None
        height = None
        weight = None
        if position_paragraph_idx:
            position_paragraph = paragraphs[position_paragraph_idx]
            position = position_paragraph.contents[2].getText().replace('▪', '').strip()
            body_paragraph = paragraphs[position_paragraph_idx + 1]
            body_spans = body_paragraph.select('span')
            height_components = body_spans[0].getText().split('-')
            height = int(height_components[0]) * 12 + int(height_components[1])
            weight = int(body_spans[1].getText()[:-2])

        birthdate_span = meta_div.select('span#necro-birth')
        if birthdate_span:
            birthdate = birthdate_span[0]['data-birth']
            birthdate = datetime.date.fromisoformat(birthdate)
        else:
            birthdate = None
        last_paragraph_strong = paragraphs[-1].select('strong')[0].getText()
        active = False
        if last_paragraph_strong == 'Experience:':
            active = True
        elif last_paragraph_strong != 'Career Length:':
            raise Exception('wtf')
        hof_blings = soup.select('#bling li.important.special a')
        hof_blings = [a for a in hof_blings if a.getText() == 'Hall of Fame']
        hof = len(hof_blings) > 0
        res = {
            'PlayerId': player.player_bref_id,
            'PlayerName': player_name,
            'FromYear': from_season,
            'ToYear': to_season,
            'Position': position,
            'Height': height,
            'Weight': weight,
            'Birthdate': birthdate,
            'Active': 1 if active else 0,
            'HOF': 1 if hof else 0,
        }
        self.insert_bref_players([res])

    @retry_wrapper
    async def collect_bref_players_by_letter(self, letter: str):
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
            'HOF',
        ]
        handler = BREFPlayersDownloader(letter)
        data = handler.download()
        data = [dict(zip(headers, p)) for p in data]
        self.insert_bref_players(data)

    async def action(self):
        for letter, next_letter in iterate_with_next(self.missing_letters, ''):
            await self.collect_bref_players_by_letter(letter)
            self.current_letter = next_letter
            await self.finish_subtask()
        if self.complete_index:
            self.missing_players = self.get_missing_players()
            self.current_player = self.missing_players[0] if self.missing_players else None
            await self.refresh_status()
        for current_player, next_player in iterate_with_next(self.missing_players):
            await self.collect_bref_player_from_page(current_player)
            self.current_player = next_player
            await self.finish_subtask()

    @abstractmethod
    def get_letters_to_fetch(self) -> List[str]:
        pass

    def subtasks_count(self) -> Union[int, None]:
        return len(self.missing_letters) + len(self.missing_players)

    def get_current_subtask_text_abs(self) -> str:
        # fetching players starting with letter %{letter}
        if self.current_letter:
            return gettext('resources.bref_players.actions.update_bref_players.fetching_players',
                           letter=self.current_letter)
        return gettext('resources.bref_players.actions.update_bref_players.fetching_player',
                       player=self.current_player.player_nba_name if self.current_player else '')


class UpdateBREFPlayersAction(UpdateBREFPlayersGeneralAction):
    def __init__(self, session: scoped_session):
        super().__init__(session, True)

    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return UpdateBREFPlayers

    def get_letters_to_fetch(self) -> List[str]:
        missing_players_stmt = (
            select(PlayerMapping.PlayerBREFId, PlayerMapping.PlayerNBAId).
            outerjoin(BREFPlayer, PlayerMapping.PlayerBREFId == BREFPlayer.PlayerId).
            where(BREFPlayer.PlayerId.is_(None)).
            group_by(PlayerMapping.PlayerNBAId)
        )
        missing_players = self.session.execute(missing_players_stmt).fetchall()
        missing_letters = list(set(player_bref_id[0] for player_bref_id, player_nba_id in missing_players))
        return missing_letters


class RedownloadBREFPlayersAction(UpdateBREFPlayersGeneralAction):
    def __init__(self, session: scoped_session):
        super().__init__(session, True)

    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return RedownloadBREFPlayers

    def get_letters_to_fetch(self) -> List[str]:
        return [letter for letter in string.ascii_lowercase]
