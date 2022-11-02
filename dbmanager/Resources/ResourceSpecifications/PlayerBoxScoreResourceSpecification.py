from typing import List, Type

from dbmanager.AppI18n import gettext
from dbmanager.Database.Models.BoxScoreP import BoxScoreP
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc, Source
from dbmanager.base import MyModel


class PlayerBoxScoreResourceSpecification(ResourceSpecificationAbc):
    @classmethod
    def get_id(cls) -> str:
        return 'playerboxscore'

    @classmethod
    def get_name(cls) -> str:
        # TODO translate?
        return 'PlayerBoxScore'

    @classmethod
    def get_related_tables(cls) -> List[Type[MyModel]]:
        return [
            BoxScoreP
        ]

    @classmethod
    def get_dependencies(cls) -> List[Type['ResourceSpecificationAbc']]:
        return []

    @classmethod
    def get_source(cls) -> Source:
        return Source('stats.nba', 'https://www.nba.com/stats/players/boxscores')

    @classmethod
    def get_description(cls) -> str:
        return gettext('resources.playerboxscore.description')
