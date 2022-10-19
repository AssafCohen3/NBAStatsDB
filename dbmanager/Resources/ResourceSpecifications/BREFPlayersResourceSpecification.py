from typing import List, Type

from dbmanager.AppI18n import gettext
from dbmanager.Resources.ResourceSpecifications.PlayersMappingsResourceSpecification import \
    PlayersMappingsResourceSpecification
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc, RelatedTable, \
    Source


class BREFPlayersResourceSpecification(ResourceSpecificationAbc):
    @classmethod
    def get_id(cls) -> str:
        return 'bref_players'

    @classmethod
    def get_name(cls) -> str:
        # TODO translate?
        return 'Players(BREF)'

    @classmethod
    def get_related_tables(cls) -> List[RelatedTable]:
        return [
            RelatedTable('BREFPlayer')
        ]

    @classmethod
    def get_dependencies(cls) -> List[Type['ResourceSpecificationAbc']]:
        return [
            PlayersMappingsResourceSpecification
        ]

    @classmethod
    def get_source(cls) -> Source:
        return Source('BREF', 'https://www.basketball-reference.com/players/a/')

    @classmethod
    def get_description(cls) -> str:
        return gettext('resources.bref_players.description')
