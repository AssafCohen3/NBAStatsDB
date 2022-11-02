from typing import List, Type

from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.BREFPlayoffSerie import BREFPlayoffSerie
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc, Source
from dbmanager.base import MyModel


class BREFPlayoffSeriesResourceSpecification(ResourceSpecificationAbc):
    @classmethod
    def get_id(cls) -> str:
        return 'bref_playoff_series'

    @classmethod
    def get_name(cls) -> str:
        # TODO translate?
        return 'Playoff Series(BREF)'

    @classmethod
    def get_related_tables(cls) -> List[Type[MyModel]]:
        return [
            BREFPlayoffSerie
        ]

    @classmethod
    def get_dependencies(cls) -> List[Type['ResourceSpecificationAbc']]:
        return []

    @classmethod
    def get_source(cls) -> Source:
        return Source('BREF', 'https://www.basketball-reference.com/playoffs/NBA_2021.html')

    @classmethod
    def get_description(cls) -> str:
        return gettext('resources.bref_playoff_series.description')
