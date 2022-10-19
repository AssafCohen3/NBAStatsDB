from typing import List, Type

from dbmanager.AppI18n import gettext
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc, RelatedTable, \
    Source


class NBAHonoursResourceSpecification(ResourceSpecificationAbc):
    @classmethod
    def get_id(cls) -> str:
        return 'nba_honours'

    @classmethod
    def get_name(cls) -> str:
        # TODO translate?
        return 'Honours(NBA)'

    @classmethod
    def get_related_tables(cls) -> List[RelatedTable]:
        return [
            RelatedTable('NBAHonours')
        ]

    @classmethod
    def get_dependencies(cls) -> List[Type['ResourceSpecificationAbc']]:
        return []

    @classmethod
    def get_source(cls) -> Source:
        return Source('stats.nba', 'https://stats.nba.com/stats/teamdetails/?teamId=1610612745')

    @classmethod
    def get_description(cls) -> str:
        return gettext('resources.nba_honours.description')
