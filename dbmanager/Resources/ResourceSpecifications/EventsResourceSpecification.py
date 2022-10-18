from typing import List, Type

from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc, RelatedTable
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
