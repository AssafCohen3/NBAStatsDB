from typing import List, Type
from dbmanager.AppI18n import gettext
from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc, ActionInput
from dbmanager.Resources.ResourceSpecifications.BREFPlayersResourceSpecification import BREFPlayersResourceSpecification
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc


class UpdateBREFPlayers(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return BREFPlayersResourceSpecification

    @classmethod
    def validate_request_abs(cls, session, params):
        return

    @classmethod
    def get_action_id(cls) -> str:
        return 'update_bref_players'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.bref_players.actions.update_bref_players.title')

    @classmethod
    def get_action_inputs(cls, session) -> List[ActionInput]:
        return []


class RedownloadBREFPlayers(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return BREFPlayersResourceSpecification

    @classmethod
    def validate_request_abs(cls, session, params):
        return

    @classmethod
    def get_action_id(cls) -> str:
        return 'redownload_bref_players'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.bref_players.actions.redownload_bref_players.title')

    @classmethod
    def get_action_inputs(cls, session) -> List[ActionInput]:
        return []