from typing import Type, List
from sqlalchemy import select, func, join
from sqlalchemy.orm import scoped_session

from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.BREFPlayer import BREFPlayer
from dbmanager.Database.Models.PlayerMapping import PlayerMapping
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.Resources.Actions.BREFPlayersActions import UpdateBREFPlayersAction, RedownloadBREFPlayersAction
from dbmanager.Resources.ResourceAbc import ResourceAbc, ResourceMessage, StatusOption
from dbmanager.Resources.ResourceSpecifications.BREFPlayersResourceSpecification import BREFPlayersResourceSpecification
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc
from dbmanager.SharedData.PlayersIndex import players_index


class BREFPlayersResourceHandler(ResourceAbc):
    @classmethod
    def get_resource_spec(cls) -> Type[ResourceSpecificationAbc]:
        return BREFPlayersResourceSpecification

    @classmethod
    def get_actions(cls) -> List[Type[ActionAbc]]:
        return [
            UpdateBREFPlayersAction,
            RedownloadBREFPlayersAction,
        ]

    @classmethod
    def get_messages(cls, session: scoped_session) -> List[ResourceMessage]:
        joined = join(BREFPlayer, PlayerMapping, BREFPlayer.PlayerId == PlayerMapping.PlayerBREFId)
        saved_players_stmt = select(func.count(BREFPlayer.PlayerId)).select_from(joined)
        saved_players_count: int = session.execute(saved_players_stmt).fetchall()[0][0]
        missing_players_stmt = (
            select(PlayerMapping.PlayerBREFId, PlayerMapping.PlayerNBAId).
            outerjoin(BREFPlayer, PlayerMapping.PlayerBREFId == BREFPlayer.PlayerId).
            where(BREFPlayer.PlayerId.is_(None)).
            group_by(PlayerMapping.PlayerNBAId)
        )
        missing_players = session.execute(missing_players_stmt).fetchall()
        missing_players = [(player_bref_id, player_nba_id) for player_bref_id, player_nba_id in missing_players
                           if players_index.is_player_played_games(player_nba_id)]
        possible_players_count = len(missing_players) + saved_players_count
        return [
            ResourceMessage(
                gettext('resources.bref_players.messages.players.title'),
                gettext('resources.bref_players.messages.players.text',
                        players_count=saved_players_count,
                        possible_players_count=possible_players_count),
                StatusOption.OK if saved_players_count == possible_players_count else StatusOption.MISSING
            ),
        ]
