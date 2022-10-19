from typing import List, Type

from dbmanager.AppI18n import gettext
from dbmanager.Resources.ResourceSpecifications.PlayerBoxScoreResourceSpecification import \
    PlayerBoxScoreResourceSpecification
from dbmanager.Resources.ResourceSpecifications.PlayersMappingsResourceSpecification import \
    PlayersMappingsResourceSpecification
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc, Source, \
    RelatedTable


class BREFStartersResourceSpecification(ResourceSpecificationAbc):
    @classmethod
    def get_id(cls) -> str:
        return 'bref_starters'

    @classmethod
    def get_name(cls) -> str:
        return 'BoxScores Starters(BREF)'

    @classmethod
    def get_related_tables(cls) -> List[RelatedTable]:
        return [
            RelatedTable('BoxScoreP')
        ]

    @classmethod
    def get_dependencies(cls) -> List[Type['ResourceSpecificationAbc']]:
        return [
            PlayerBoxScoreResourceSpecification,
            PlayersMappingsResourceSpecification,
        ]

    @classmethod
    def get_source(cls) -> Source:
        return Source('BREF', 'https://www.basketball-reference.com/teams/BOS/2021_start.html')

    @classmethod
    def get_description(cls) -> str:
        return gettext('resources.bref_starters.description')
