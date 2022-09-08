from typing import List, Type
from dbmanager.AppI18n import gettext
from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc, ActionInput
from dbmanager.Resources.ResourceSpecifications.NBAPlayersResourceSpecification import NBAPlayersResourceSpecification
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc


class UpdateNBAPlayers(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return NBAPlayersResourceSpecification

    @classmethod
    def validate_request_abs(cls, session, params):
        return

    @classmethod
    def get_action_id(cls) -> str:
        return 'update_nba_players'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.nba_players.actions.update_nba_players.title')

    @classmethod
    def get_action_inputs(cls, session) -> List[ActionInput]:
        return []
