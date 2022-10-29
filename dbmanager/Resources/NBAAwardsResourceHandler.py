from typing import List, Type
from sqlalchemy import select, func
from sqlalchemy.orm import scoped_session
from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.NBAAwards import NBAAwards
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.Resources.Actions.NBAAwardsActions import DownloadAllPlayersAwardsAction, \
    DownloadActivePlayersAwardsAction, DownloadRookiesAwardsInSeasonsRangeAction, DownloadPlayerAwardsAction
from dbmanager.Resources.ResourceAbc import ResourceAbc, ResourceMessage, StatusOption
from dbmanager.Resources.ResourceSpecifications.NBAAwardsResourceSpecification import NBAAwardsResourceSpecification
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc


class NBAAwardsResourceHandler(ResourceAbc):
    @classmethod
    def get_resource_spec(cls) -> Type[ResourceSpecificationAbc]:
        return NBAAwardsResourceSpecification

    @classmethod
    def get_actions(cls) -> List[Type[ActionAbc]]:
        return [
            DownloadAllPlayersAwardsAction,
            DownloadActivePlayersAwardsAction,
            DownloadRookiesAwardsInSeasonsRangeAction,
            DownloadPlayerAwardsAction
        ]

    @classmethod
    def get_messages(cls, session: scoped_session) -> List[ResourceMessage]:
        stmt = (
            select(func.count(NBAAwards.PlayerId), func.count(NBAAwards.PlayerId.distinct()))
        )
        res = session.execute(stmt).fetchall()
        return [
            ResourceMessage(
                gettext('resources.nba_awards.messages.players_with_awards.title'),
                gettext('resources.nba_awards.messages.players_with_awards.text', players_count=res[0][1]),
                StatusOption.INFO,
            ),
            ResourceMessage(
                gettext('resources.nba_awards.messages.awards.title'),
                gettext('resources.nba_awards.messages.awards.text', awards_count=res[0][0]),
                StatusOption.INFO,
            ),
        ]
