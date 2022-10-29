from typing import List, Type

from sqlalchemy import select, func
from sqlalchemy.orm import scoped_session

from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.NBAPlayer import NBAPlayer
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.Resources.Actions.NBAPlayersBirthdateActions import UpdatePlayersBirthdateAction, \
    RedownloadPlayersBirthdateAction, DownloadPlayersBirthdateInSeasonsRangeAction
from dbmanager.Resources.ResourceAbc import ResourceAbc, ResourceMessage, StatusOption
from dbmanager.Resources.ResourceSpecifications.NBAPlayersBirthdateResourceSpecification import \
    NBAPlayersBirthdateResourceSpecification
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc


class NBAPlayersBirthdateResourceHandler(ResourceAbc):

    @classmethod
    def get_resource_spec(cls) -> Type[ResourceSpecificationAbc]:
        return NBAPlayersBirthdateResourceSpecification

    @classmethod
    def get_actions(cls) -> List[Type[ActionAbc]]:
        return [
            UpdatePlayersBirthdateAction,
            RedownloadPlayersBirthdateAction,
            DownloadPlayersBirthdateInSeasonsRangeAction
        ]

    @classmethod
    def get_messages(cls, session: scoped_session) -> List[ResourceMessage]:
        stmt = (
            select(func.count(NBAPlayer.PlayerId), func.count(NBAPlayer.PlayerId).filter(NBAPlayer.BirthDate.is_(None)))
        )
        players_count, players_without_birthdates_count = session.execute(stmt).fetchall()[0]
        return [
            ResourceMessage(
                gettext('resources.nba_players_birthdate.messages.players_with_birthdate.title'),
                gettext('resources.nba_players_birthdate.messages.players_with_birthdate.text',
                        players_count=players_count,
                        players_with_birthdates_count=players_count - players_without_birthdates_count),
                StatusOption.OK if players_without_birthdates_count == 0 else StatusOption.MISSING,
            )
        ]
