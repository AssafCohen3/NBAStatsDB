from typing import List, Type

from sqlalchemy import select, func
from sqlalchemy.orm import scoped_session

from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.NBAHonours import NBAHonours
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.Resources.Actions.NBAHonoursActions import DownloadAllHonoursAction, DownloadTeamHonoursAction
from dbmanager.Resources.ResourceAbc import ResourceAbc, ResourceMessage
from dbmanager.Resources.ResourceSpecifications.NBAHonoursResourceSpecification import NBAHonoursResourceSpecification
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc


class NBAHonoursResourceHandler(ResourceAbc):
    @classmethod
    def get_resource_spec(cls) -> Type[ResourceSpecificationAbc]:
        return NBAHonoursResourceSpecification

    @classmethod
    def get_actions(cls) -> List[Type[ActionAbc]]:
        return [
            DownloadAllHonoursAction,
            DownloadTeamHonoursAction,
        ]

    @classmethod
    def get_messages(cls, session: scoped_session) -> List[ResourceMessage]:
        stmt = (
            select(func.count(NBAHonours.TeamId.distinct()))
        )
        result = session.execute(stmt).fetchall()
        return [
            ResourceMessage(
                gettext('resources.nba_honours.messages.teams_honours.title'),
                gettext('resources.nba_honours.messages.teams_honours.text', teams_count=result[0][0]),
                'ok'
            )
        ]
