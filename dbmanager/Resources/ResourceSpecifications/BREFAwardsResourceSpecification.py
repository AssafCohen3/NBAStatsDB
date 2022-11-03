from typing import List, Type

from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.BREFAwards import BREFAwards
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc, Source
from dbmanager.base import MyModel


class BREFAwardsResourceSpecification(ResourceSpecificationAbc):
    @classmethod
    def get_id(cls) -> str:
        return 'bref_awards'

    @classmethod
    def get_name(cls) -> str:
        return 'Awards(BREF)'

    @classmethod
    def get_related_tables(cls) -> List[Type[MyModel]]:
        return [
            BREFAwards,
        ]

    @classmethod
    def get_dependencies(cls) -> List[Type['ResourceSpecificationAbc']]:
        return []

    @classmethod
    def get_source(cls) -> Source:
        return Source('BREF', 'https://www.basketball-reference.com/awards/mvp.html')

    @classmethod
    def get_description(cls) -> str:
        return gettext('resources.bref_awards.description')
