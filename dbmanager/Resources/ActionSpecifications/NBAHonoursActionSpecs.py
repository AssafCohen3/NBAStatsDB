from typing import List, Dict, Any, Type
from sqlalchemy.orm import scoped_session
from dbmanager.AppI18n import gettext
from dbmanager.Errors import IlegalParameterValueError
from dbmanager.Resources.ActionSpecifications.ActionInput import ActionInput, TeamsAutoComplete
from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc
from dbmanager.Resources.ResourceSpecifications.NBAHonoursResourceSpecification import NBAHonoursResourceSpecification
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc
from dbmanager.SharedData.FranchisesHistory import franchises_history


class DownloadAllHonours(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return NBAHonoursResourceSpecification

    @classmethod
    def get_action_id(cls) -> str:
        return 'download_all_honours'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.nba_honours.actions.download_all_honours.title')

    @classmethod
    def validate_request_abs(cls, session: scoped_session, params: Dict[str, Any]):
        return

    @classmethod
    def get_action_inputs(cls, session: scoped_session) -> List[ActionInput]:
        return []


class DownloadTeamHonours(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return NBAHonoursResourceSpecification

    @classmethod
    def get_action_id(cls) -> str:
        return 'download_team_honours'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.nba_honours.actions.download_team_honours.title')

    @classmethod
    def validate_request_abs(cls, session: scoped_session, params: Dict[str, Any]):
        if not franchises_history.get_last_span_with_id(params['team_id']):
            raise IlegalParameterValueError(cls, 'team_id', params['team_id'], 'no franchise with the supplied id')

    @classmethod
    def get_action_inputs(cls, session: scoped_session) -> List[ActionInput]:
        return [
            TeamsAutoComplete()
        ]
