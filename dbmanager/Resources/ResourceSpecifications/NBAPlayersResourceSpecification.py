from typing import List, Type

from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.NBAPlayer import NBAPlayer
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc, Source
from dbmanager.base import MyModel


class NBAPlayersResourceSpecification(ResourceSpecificationAbc):
    @classmethod
    def get_id(cls) -> str:
        return 'nba_players'

    @classmethod
    def get_name(cls) -> str:
        # TODO translate?
        return 'Players(NBA)'

    @classmethod
    def get_related_tables(cls) -> List[Type[MyModel]]:
        return [
            NBAPlayer
        ]

    @classmethod
    def get_dependencies(cls) -> List[Type['ResourceSpecificationAbc']]:
        return []

    @classmethod
    def get_source(cls) -> Source:
        return Source('stats.nba', 'https://www.nba.com/players')

    @classmethod
    def get_description(cls) -> str:
        return gettext('resources.nba_players.description')
