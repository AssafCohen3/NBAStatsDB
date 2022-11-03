from typing import List, Type
from sqlalchemy import select, func
from sqlalchemy.orm import scoped_session
from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.BREFAwards import BREFAwards
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.Resources.Actions.BREFAwardsActions import DownloadAllAwardsAction, DownloadSpecificAwardAction
from dbmanager.Resources.ResourceAbc import ResourceAbc, ResourceMessage, StatusOption
from dbmanager.Resources.ResourceSpecifications.BREFAwardsResourceSpecification import BREFAwardsResourceSpecification
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc


class BREFAwardsResourceHandler(ResourceAbc):
    @classmethod
    def get_resource_spec(cls) -> Type[ResourceSpecificationAbc]:
        return BREFAwardsResourceSpecification

    @classmethod
    def get_actions(cls) -> List[Type[ActionAbc]]:
        return [
            DownloadAllAwardsAction,
            DownloadSpecificAwardAction,
        ]

    @classmethod
    def get_messages(cls, session: scoped_session) -> List[ResourceMessage]:
        stmt = (
            select(func.count(BREFAwards.PersonId), func.count(BREFAwards.PersonId.distinct()))
        )
        awards_count, players_with_awards_count = session.execute(stmt).fetchall()[0]
        return [
            ResourceMessage(
                gettext('resources.bref_awards.messages.awards_count.title'),
                gettext('resources.bref_awards.messages.awards_count.text',
                        awards=awards_count),
                StatusOption.INFO,
            ),
            ResourceMessage(
                gettext('resources.bref_awards.messages.players_with_awards_count.title'),
                gettext('resources.bref_awards.messages.players_with_awards_count.text',
                        players=players_with_awards_count),
                StatusOption.INFO,
            ),
        ]
