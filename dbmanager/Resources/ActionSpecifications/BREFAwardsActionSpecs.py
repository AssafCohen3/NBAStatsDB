from typing import List, Dict, Any, Type
from sqlalchemy.orm import scoped_session
from dbmanager.AppI18n import gettext
from dbmanager.DataTypes.BREFAwardConst import get_awards
from dbmanager.Errors import IlegalParameterValueError
from dbmanager.Resources.ActionSpecifications.ActionInput import ActionInput, AwardsSelector
from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc, ActionDependency
from dbmanager.Resources.ResourceSpecifications.BREFAwardsResourceSpecification import BREFAwardsResourceSpecification
from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc


class DownloadAllAwards(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return BREFAwardsResourceSpecification

    @classmethod
    def get_action_id(cls) -> str:
        return 'download_awards'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.bref_awards.actions.download_awards.title')

    @classmethod
    def validate_request_abs(cls, session: scoped_session, params: Dict[str, Any]):
        return

    @classmethod
    def get_action_inputs(cls, session: scoped_session) -> List[ActionInput]:
        return []


class DownloadSpecificAward(ActionSpecificationAbc):
    @classmethod
    def get_resource(cls) -> Type[ResourceSpecificationAbc]:
        return BREFAwardsResourceSpecification

    @classmethod
    def get_action_id(cls) -> str:
        return 'download_award'

    @classmethod
    def get_action_title(cls) -> str:
        return gettext('resources.bref_awards.actions.download_award.title')

    @classmethod
    def validate_request_abs(cls, session: scoped_session, params: Dict[str, Any]):
        # if params['award_id'] not in awards_list raise
        relevant_awards = get_awards([params['award_id']])
        if len(relevant_awards) == 0:
            raise IlegalParameterValueError(cls, 'award_id', params['award_id'], 'there is no award with this id')

    @classmethod
    def get_action_inputs(cls, session: scoped_session) -> List[ActionInput]:
        return [
            AwardsSelector()
        ]

    @classmethod
    def get_action_dependencies(cls, parsed_params: Dict[str, Any]) -> List[ActionDependency]:
        return []
