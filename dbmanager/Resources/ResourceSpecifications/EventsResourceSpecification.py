from typing import List, Type

from dbmanager.AppI18n import gettext
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc, RelatedTable, \
    Source
from dbmanager.Resources.ResourceSpecifications.TeamBoxScoreResourceSpecification import \
    TeamBoxScoreResourceSpecification


class EventsResourceSpecification(ResourceSpecificationAbc):
    @classmethod
    def get_id(cls) -> str:
        return 'events'

    @classmethod
    def get_name(cls) -> str:
        # TODO translate?
        return 'Events'

    @classmethod
    def get_related_tables(cls) -> List[RelatedTable]:
        return [
            RelatedTable('Event')
        ]

    @classmethod
    def get_dependencies(cls) -> List[Type['ResourceSpecificationAbc']]:
        return [TeamBoxScoreResourceSpecification]

    @classmethod
    def get_source(cls) -> Source:
        return Source('stats.nba', 'https://stats.nba.com/stats/playbyplayv2/?gameId=0021600732&startPeriod=0&endPeriod=14')

    @classmethod
    def get_description(cls) -> str:
        return gettext('resources.events.description')
