from typing import List, Type
from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.BREFCoachSeason import BREFCoachSeason
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc, Source
from dbmanager.base import MyModel


class BREFCoachesResourceSpecification(ResourceSpecificationAbc):
    @classmethod
    def get_id(cls) -> str:
        return 'bref_coaches'

    @classmethod
    def get_name(cls) -> str:
        return 'Coaches(BREF)'

    @classmethod
    def get_related_tables(cls) -> List[Type[MyModel]]:
        return [
            BREFCoachSeason
        ]

    @classmethod
    def get_dependencies(cls) -> List[Type['ResourceSpecificationAbc']]:
        return []

    @classmethod
    def get_source(cls) -> Source:
        return Source('BREF', 'https://www.basketball-reference.com/leagues/NBA_2015_coaches.html')

    @classmethod
    def get_description(cls) -> str:
        return gettext('resources.bref_coaches.description')
