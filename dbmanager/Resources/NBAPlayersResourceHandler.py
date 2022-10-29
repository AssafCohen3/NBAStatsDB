from typing import List, Type

from sqlalchemy import select, func
from sqlalchemy.orm import scoped_session

from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.NBAPlayer import NBAPlayer
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.Resources.Actions.NBAPlayersActions import UpdateNBAPlayersAction
from dbmanager.Resources.ResourceAbc import ResourceAbc, ResourceMessage, StatusOption
from dbmanager.Resources.ResourceSpecifications.NBAPlayersResourceSpecification import NBAPlayersResourceSpecification
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc


class NBAPlayersResourceHandler(ResourceAbc):
    @classmethod
    def get_resource_spec(cls) -> Type[ResourceSpecificationAbc]:
        return NBAPlayersResourceSpecification

    @classmethod
    def get_actions(cls) -> List[Type[ActionAbc]]:
        return [
            UpdateNBAPlayersAction
        ]

    @classmethod
    def get_messages(cls, session: scoped_session) -> List[ResourceMessage]:
        stmt = (
            select(func.count(NBAPlayer.PlayerId), func.count(NBAPlayer.PlayerId).filter(NBAPlayer.Active == 1))
        )
        res = session.execute(stmt).fetchall()
        return [
            ResourceMessage(
                gettext('resources.nba_players.messages.players.title'),
                gettext('resources.nba_players.messages.players.text', players_count=res[0][0]),
                StatusOption.INFO,
            ),
            ResourceMessage(
                gettext('resources.nba_players.messages.active_players.title'),
                gettext('resources.nba_players.messages.active_players.text', active_players_count=res[0][1]),
                StatusOption.INFO,
            ),
        ]
