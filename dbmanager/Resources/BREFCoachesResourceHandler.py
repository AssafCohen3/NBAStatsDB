from typing import List, Type
from sqlalchemy import select, func
from sqlalchemy.orm import scoped_session
from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.BREFCoachSeason import BREFCoachSeason
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.Resources.Actions.BREFCoachesActions import DownloadAllCoachesAction, DownloadCoachesInSeasonsRangeAction
from dbmanager.Resources.ResourceAbc import ResourceAbc, ResourceMessage, StatusOption
from dbmanager.Resources.ResourceSpecifications.BREFCoachesResourceSpecification import BREFCoachesResourceSpecification
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc


class BREFCoachesResourceHandler(ResourceAbc):
    @classmethod
    def get_resource_spec(cls) -> Type[ResourceSpecificationAbc]:
        return BREFCoachesResourceSpecification

    @classmethod
    def get_actions(cls) -> List[Type[ActionAbc]]:
        return [
            DownloadAllCoachesAction,
            DownloadCoachesInSeasonsRangeAction,
        ]

    @classmethod
    def get_messages(cls, session: scoped_session) -> List[ResourceMessage]:
        stmt = (
            select(func.count(BREFCoachSeason.CoachId), func.count(BREFCoachSeason.Season.distinct()),
                   func.count(BREFCoachSeason.CoachId.distinct()))
        )
        coaches_seasons_count, seasons_count, coaches_count = session.execute(stmt).fetchall()[0]
        return [
            ResourceMessage(
                gettext('resources.bref_coaches.messages.coaches_seasons_count.title'),
                gettext('resources.bref_coaches.messages.coaches_seasons_count.text',
                        coaches_seasons=coaches_seasons_count),
                StatusOption.INFO,
            ),
            ResourceMessage(
                gettext('resources.bref_coaches.messages.seasons_count.title'),
                gettext('resources.bref_coaches.messages.seasons_count.text',
                        seasons=seasons_count),
                StatusOption.INFO,
            ),
            ResourceMessage(
                gettext('resources.bref_coaches.messages.coaches_count.title'),
                gettext('resources.bref_coaches.messages.coaches_count.text',
                        coaches=coaches_count),
                StatusOption.INFO,
            ),
        ]
