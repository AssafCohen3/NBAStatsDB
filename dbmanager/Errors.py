from abc import ABC
from typing import Dict, List

from dbmanager.AppI18n import gettext


class ActionNotExistError(Exception):
    def __init__(self, resource_id: str, action_id: str):
        self.resource_id = resource_id
        self.action_id = action_id
        super().__init__(gettext('errors.action_not_exist', resource_id=resource_id, action_id=action_id))


class InvalidActionCallError(Exception):
    def __init__(self, resource_id: str, action_id: str, params: Dict[str, str], error_msg: str):
        self.resource_id = resource_id
        self.action_id = action_id
        self.params = params
        self.error_msg = error_msg
        super().__init__(gettext('errors.invalid_action', resource_id=resource_id, action_id=action_id, params=params, error_msg=error_msg))


class ResourceNotExistError(Exception):
    def __init__(self, resource_id: str):
        self.resource_id = resource_id
        super().__init__(gettext('errors.resource_not_exist', resource_id=resource_id))


class RequiredParameterMissingError(Exception):
    def __init__(self, action_id: str, par: str):
        self.action_id = action_id
        self.par = par
        super().__init__(gettext('errors.required_parameter_missing', action_id=action_id, par=par))


class IncorrectParameterTypeError(Exception):
    def __init__(self, action_id: str, par_name: str, par_type: str, par_value: str):
        self.action_id = action_id
        self.par_name = par_name
        self.par_type = par_type
        self.par_value = par_value
        super().__init__(gettext('errors.incorrect_parameter_type', action_id=action_id,
                                 par_name=par_name, par_type=par_type, par_value=par_value))


class IlegalParameterValueError(Exception):
    def __init__(self, action_id: str, par_name: str, par_value: str, err_message: str):
        self.action_id = action_id
        self.par_name = par_name
        self.par_value = par_value
        self.err_message = err_message
        super().__init__(gettext('errors.ilegal_parameter_value', action_id=action_id,
                                 par_name=par_name, par_value=par_value, err_message=err_message))


class UnknownParameterTypeError(Exception):
    def __init__(self, action_id: str, par_name: str, par_type: str):
        self.action_id = action_id
        self.par_type = par_type
        super().__init__(f'unknown parameter type {par_type} of parameter {par_name}')


class UnexpectedParameterError(Exception):
    def __init__(self, action_id: str, unexpected_params: List[str]):
        self.action_id = action_id
        self.unexpected_params = unexpected_params
        super().__init__(gettext('errors.unexpected_parameter', action_id=action_id, unexpected_params=', '.join(unexpected_params)))


class TaskError(Exception, ABC):
    pass


class TaskNotExist(TaskError):
    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f'task with id {task_id} not exist')


class TaskAlreadyFinished(TaskError):
    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f'task with id {task_id} already finished')


class TaskNotFinished(TaskError):
    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f'task with id {task_id} not finished')
