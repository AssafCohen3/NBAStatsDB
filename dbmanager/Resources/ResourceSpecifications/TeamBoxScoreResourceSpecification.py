from typing import List, Type

from dbmanager.AppI18n import gettext
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc, RelatedTable, \
    Source


class TeamBoxScoreResourceSpecification(ResourceSpecificationAbc):
    @classmethod
    def get_id(cls) -> str:
        return 'teamboxscore'

    @classmethod
    def get_name(cls) -> str:
        # TODO translate?
        return 'TeamBoxScore'

    @classmethod
    def get_related_tables(cls) -> List[RelatedTable]:
        return [
            RelatedTable('BoxScoreT')
        ]

    @classmethod
    def get_dependencies(cls) -> List[Type['ResourceSpecificationAbc']]:
        return []

    @classmethod
    def get_source(cls) -> Source:
        return Source('stats.nba', 'https://www.nba.com/stats/teams/boxscores')

    @classmethod
    def get_description(cls) -> str:
        return gettext('resources.teamboxscore.description')

