from typing import List, Type

from dbmanager.AppI18n import gettext
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc, RelatedTable, \
    Source


class PlayersMappingsResourceSpecification(ResourceSpecificationAbc):
    @classmethod
    def get_id(cls) -> str:
        return 'players_mappings'

    @classmethod
    def get_name(cls) -> str:
        # TODO translate?
        return 'Players Mappings'

    @classmethod
    def get_related_tables(cls) -> List[RelatedTable]:
        return [
            RelatedTable('PlayerMapping')
        ]

    @classmethod
    def get_dependencies(cls) -> List[Type['ResourceSpecificationAbc']]:
        return []

    @classmethod
    def get_source(cls) -> Source:
        return Source('', '')

    @classmethod
    def get_description(cls) -> str:
        return gettext('resources.players_mappings.description')
