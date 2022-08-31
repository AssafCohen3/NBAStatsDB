import datetime
from abc import ABC, abstractmethod
from typing import Dict, Any, List

from sqlalchemy.orm import Session

from dbmanager.Errors import RequiredParameterMissingError, UnknownParameterTypeError, IncorrectParameterTypeError, \
    UnexpectedParameterError
from dbmanager.Resources.ActionSpecifications.ActionInput import ActionInput, ActionParameter


def param_parser(param_value: str, param_type: str):
    if param_type == 'str':
        return param_value
    if param_type == 'int':
        return int(param_value)
    if param_type == 'isodate':
        return datetime.date.fromisoformat(param_value)
    return None


class ActionSpecificationAbc(ABC):

    @classmethod
    @abstractmethod
    def get_action_id(cls) -> str:
        """
        get the action id
        """

    @classmethod
    @abstractmethod
    def get_action_title(cls) -> str:
        """
        get the action title
        """

    @classmethod
    def parse_params(cls, session: Session, params: Dict[str, str]) -> Dict[str, Any]:
        parsed_params = {}
        for param in cls.get_action_params(session):
            parsed_params[param.parameter_name] = None
            if param.required and param.parameter_name not in params:
                raise RequiredParameterMissingError(cls.get_action_id(), param.parameter_name)
            if param.parameter_name not in params:
                # not required
                continue
            try:
                val = param_parser(params[param.parameter_name], param.parameter_type)
            except ValueError:
                raise IncorrectParameterTypeError(cls.get_action_id(), param.parameter_name,
                                                  param.parameter_type, params[param.parameter_name])
            if val is None:
                raise UnknownParameterTypeError(cls.get_action_id(),
                                                param.parameter_name, param.parameter_type)
            parsed_params[param.parameter_name] = val
            params.pop(param.parameter_name)
        if len(params.keys()) > 0:
            raise UnexpectedParameterError(cls.get_action_id(), list(params.keys()))
        return parsed_params

    @classmethod
    def validate_request(cls, session: Session, params: Dict[str, str]) -> Dict[str, Any]:
        parsed_params = cls.parse_params(session, params)
        cls.validate_request_abs(session, parsed_params)
        return parsed_params

    @classmethod
    @abstractmethod
    def validate_request_abs(cls, session: Session, params: Dict[str, Any]):
        """
        validate the request params
        """

    @classmethod
    @abstractmethod
    def get_action_inputs(cls, session: Session) -> List[ActionInput]:
        """
        get the action inputs
        """

    @classmethod
    def get_action_params(cls, session: Session) -> List[ActionParameter]:
        return [action_parameter for action_input in cls.get_action_inputs(session) for action_parameter in action_input.expected_params]

    @classmethod
    def to_dict(cls, session: Session):
        return {
            'action_id': cls.get_action_id(),
            'action_title': cls.get_action_title(),
            'action_inputs': cls.get_action_inputs(session)
        }