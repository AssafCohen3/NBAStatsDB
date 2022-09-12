from typing import List, Type
from dbmanager.AppI18n import gettext
from dbmanager.Resources.ActionSpecifications.ActionInput import FileSelector
from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc, ActionInput
from dbmanager.Resources.ResourceSpecifications.PlayersMappingsResourceSpecification import \
    PlayersMappingsResourceSpecification
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc


class CompleteMissingPlayersMappings(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return PlayersMappingsResourceSpecification

    @classmethod
    def validate_request_abs(cls, session, params):
        return

    @classmethod
    def get_action_id(cls) -> str:
        return 'complete_missing_players_mappings'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.players_mappings.actions.complete_missing_players_mappings.title')

    @classmethod
    def get_action_inputs(cls, session) -> List[ActionInput]:
        return []


class ReadPlayersMappingsFromFile(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return PlayersMappingsResourceSpecification

    @classmethod
    def validate_request_abs(cls, session, params):
        return

    @classmethod
    def get_action_id(cls) -> str:
        return 'read_players_mappings_from_file'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.players_mappings.actions.read_players_mappings_from_file.title')

    @classmethod
    def get_action_inputs(cls, session) -> List[ActionInput]:
        return [
            FileSelector()
        ]
