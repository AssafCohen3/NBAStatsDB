import string
from abc import ABC, abstractmethod
from typing import Union, Type, List, Optional
from sqlalchemy import select, func
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import scoped_session
from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.BREFPlayer import BREFPlayer
from dbmanager.Database.Models.PlayerMapping import PlayerMapping
from dbmanager.Downloaders.BREFPlayersDownloader import BREFPlayersDownloader
from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc
from dbmanager.Resources.ActionSpecifications.BREFPlayersActionSpecs import UpdateBREFPlayers, RedownloadBREFPlayers
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.SharedData.PlayersIndex import players_index, PlayerDetails


class UpdateBREFPlayersGeneralAction(ActionAbc, ABC):

    def __init__(self, session: scoped_session, **kwargs):
        super().__init__(session, **kwargs)
        self.missing_letters: List[str] = []

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

    def collect_bref_players_by_letter(self, letter: str):
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
        handler = BREFPlayersDownloader(letter)
        data = handler.download()
        data = [dict(zip(headers, p)) for p in data]
        self.insert_bref_players(data)

    async def action(self):
        self.missing_letters = self.get_letters_to_fetch()
        for letter in self.missing_letters:
            self.collect_bref_players_by_letter(letter)
            await self.finish_subtask()

    @abstractmethod
    def get_letters_to_fetch(self) -> List[str]:
        pass

    def subtasks_count(self) -> Union[int, None]:
        return len(self.missing_letters)

    def get_current_subtask_text_abs(self) -> str:
        # fetching players starting with letter %{letter}
        return gettext('resources.bref_players.actions.update_bref_players.fetching_players',
                       letter=self.missing_letters[self.completed_subtasks()] if self.completed_subtasks() < len(self.missing_letters) else '')


class UpdateBREFPlayersAction(UpdateBREFPlayersGeneralAction):

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
        missing_players = [(player_bref_id, player_nba_id) for player_bref_id, player_nba_id in missing_players
                           if players_index.is_player_played_games(player_nba_id)]
        missing_letters = list(set(player_bref_id[0] for player_bref_id, player_nba_id in missing_players))
        return missing_letters


class RedownloadBREFPlayersAction(UpdateBREFPlayersGeneralAction):
    @classmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        return RedownloadBREFPlayers

    def get_letters_to_fetch(self) -> List[str]:
        return [letter for letter in string.ascii_lowercase]
