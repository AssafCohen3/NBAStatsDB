from typing import List, Type

from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.NBAAwards import NBAAwards
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc, Source
from dbmanager.base import MyModel


class NBAAwardsResourceSpecification(ResourceSpecificationAbc):
    @classmethod
    def get_id(cls) -> str:
        return 'nba_awards'

    @classmethod
    def get_name(cls) -> str:
        # TODO translate?
        return 'Awards(NBA)'

    @classmethod
    def get_related_tables(cls) -> List[Type[MyModel]]:
        return [
            NBAAwards
        ]

    @classmethod
    def get_dependencies(cls) -> List[Type['ResourceSpecificationAbc']]:
        return []

    @classmethod
    def get_source(cls) -> Source:
        return Source('stats.nba', 'https://stats.nba.com/stats/playerawards/?playerId=201935')

    @classmethod
    def get_description(cls) -> str:
        return gettext('resources.nba_awards.description')
