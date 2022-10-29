from typing import List, Type
from sqlalchemy import select, func, and_
from sqlalchemy.orm import scoped_session
from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.BoxScoreP import BoxScoreP
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.Resources.Actions.BREFStartersActions import UpdateStartersAction, RedownloadStartersAction, \
    RedownloadStartersInSeasonsRangeAction
from dbmanager.Resources.ResourceAbc import ResourceAbc, ResourceMessage, StatusOption
from dbmanager.Resources.ResourceSpecifications.BREFStartersResourceSpecification import \
    BREFStartersResourceSpecification
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc
from dbmanager.constants import BREF_STARTERS_FIRST_SEASON


class BREFStartersResourceHandler(ResourceAbc):
    @classmethod
    def get_resource_spec(cls) -> Type[ResourceSpecificationAbc]:
        return BREFStartersResourceSpecification

    @classmethod
    def get_actions(cls) -> List[Type[ActionAbc]]:
        return [
            UpdateStartersAction,
            RedownloadStartersAction,
            RedownloadStartersInSeasonsRangeAction
        ]

    @classmethod
    def get_messages(cls, session: scoped_session) -> List[ResourceMessage]:
        stmt = (
            select(
                func.count(BoxScoreP.GameId),
                func.count(BoxScoreP.GameId).filter(BoxScoreP.Starter.is_(None)),
                func.count(BoxScoreP.Season.distinct()),
                func.count(BoxScoreP.Season.distinct()).filter(BoxScoreP.Starter.is_(None))
            )
            .where(and_(BREF_STARTERS_FIRST_SEASON <= BoxScoreP.Season,
                        BoxScoreP.SeasonType.in_([2, 4, 5])))
        )
        boxscores_count, boxscores_without_starters_count, seasons_count, seasons_without_starters_count = session.execute(stmt).fetchall()[0]
        return [
            ResourceMessage(
                gettext('resources.bref_starters.messages.seasons_with_starters.title'),
                gettext('resources.bref_starters.messages.seasons_with_starters.text',
                        seasons=seasons_count,
                        seasons_with_starters=seasons_count-seasons_without_starters_count),
                StatusOption.OK if seasons_without_starters_count == 0 else StatusOption.MISSING,
            ),
            ResourceMessage(
                gettext('resources.bref_starters.messages.boxscores_with_starters.title'),
                gettext('resources.bref_starters.messages.boxscores_with_starters.text',
                        boxscores=boxscores_count,
                        boxscores_with_starters=boxscores_count - boxscores_without_starters_count),
                StatusOption.OK if boxscores_without_starters_count == 0 else StatusOption.MISSING,
            ),
        ]
