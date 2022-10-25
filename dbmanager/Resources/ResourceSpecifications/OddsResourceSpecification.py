from typing import List, Type

from dbmanager.AppI18n import gettext
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc, RelatedTable, \
    Source


class OddsResourceSpecification(ResourceSpecificationAbc):
    @classmethod
    def get_id(cls) -> str:
        return 'odds'

    @classmethod
    def get_name(cls) -> str:
        return 'Odds'

    @classmethod
    def get_related_tables(cls) -> List[RelatedTable]:
        return [
            RelatedTable('Odds')
        ]

    @classmethod
    def get_dependencies(cls) -> List[Type['ResourceSpecificationAbc']]:
        return []

    @classmethod
    def get_source(cls) -> Source:
        return Source('sportsoddshistory', 'https://www.sportsoddshistory.com/nba-main/?y=1972-1973&sa=nba&a=finals&o=r')

    @classmethod
    def get_description(cls) -> str:
        return gettext('resources.odds.description')