from __future__ import annotations

import traceback
import typing
from abc import ABC
from dataclasses import dataclass
from typing import Dict, List, Type


if typing.TYPE_CHECKING:
    from dbmanager.Resources.ActionSpecifications.ActionInput import ActionParameter
    from dbmanager.Resources.ResourceSpecifications.ResourceSpecificationAbc import ResourceSpecificationAbc
    from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc
    from dbmanager.Resources.ActionsGroupsPresets.ActionRecipeObject import ActionRecipeObject
    from dbmanager.Resources.ActionsGroupsPresets.ActionsGroupPresetObject import ActionsGroupPresetObject


class LibraryError(Exception):
    pass


class ActionNotExistError(LibraryError):
    def __init__(self, resource_cls: Type[ResourceSpecificationAbc], action_id: str):
        self.resource_cls: Type[ResourceSpecificationAbc] = resource_cls
        self.action_id: str = action_id

    def __str__(self):
        return f'action {self.action_id} does not exist in resource {self.resource_cls.get_name()}'


class InvalidActionCallError(LibraryError):
    def __init__(self, action_spec: Type[ActionSpecificationAbc], params: Dict[str, str], error_msg: str):
        self.action_spec = action_spec
        self.params = params
        self.error_msg = error_msg

    def __str__(self):
        return self.error_msg

    def __repr__(self):
        return f'invalid call to action {self.action_spec.get_action_id()} of resource ' \
               f'{self.action_spec.get_resource().get_id()} with params {self.params}.\n{self.error_msg}'


class ActionFailedError(LibraryError):
    def __init__(self, action_spec: Type[ActionSpecificationAbc], msg: str):
        self.action_spec = action_spec
        self.msg = msg

    def __str__(self):
        return self.msg

    def __repr__(self):
        return f'could not complete the action {self.action_spec.get_action_title()} of resource ' \
               f'{self.action_spec.get_resource().get_name()}.\n{self.msg}'


class ResourceNotExistError(LibraryError):
    def __init__(self, resource_id: str):
        self.resource_id = resource_id
        super().__init__(f'resource {resource_id} does not exist')


class RequiredParameterMissingError(LibraryError):
    def __init__(self, action_spec: Type[ActionSpecificationAbc], par: str):
        self.action_spec = action_spec
        self.par = par

    def __str__(self):
        return f'missing parameter {self.par}'

    def __repr__(self):
        return f'The call to action {self.action_spec.get_action_id()} of resource ' \
               f'{self.action_spec.get_resource().get_id()} missing the param {self.par}'


class IncorrectParameterTypeError(LibraryError):
    def __init__(self, action_spec: Type[ActionSpecificationAbc], param: ActionParameter, par_value: str):
        self.action_spec = action_spec
        self.param = param
        self.par_value = par_value

    def __str__(self):
        return f'the type of {self.param.parameter_name} is incorrect. expected {self.param.parameter_type} but got "{self.par_value}"'

    def __repr__(self):
        return f'The value of the parameter {self.param.parameter_name} in the call to action  {self.action_spec.get_action_id()} of resource ' \
               f'{self.action_spec.get_resource().get_id()} is of incorrect type.\nexpected: {self.param.parameter_type}\nreceived: {self.par_value}'


class IlegalParameterValueError(LibraryError):
    def __init__(self, action_spec: Type[ActionSpecificationAbc], param_name: str, par_value: str, err_message: str):
        self.action_spec = action_spec
        self.param_name = param_name
        self.par_value = par_value
        self.err_message = err_message

    def __str__(self):
        return self.err_message

    def __repr__(self):
        return f'The value of the parameter {self.param_name} in the call to action  {self.action_spec.get_action_id()} of resource ' \
               f'{self.action_spec.get_resource().get_id()} is ilegal.\nreceived: {self.par_value}\n{self.err_message}'


class UnknownParameterTypeError(LibraryError):
    def __init__(self, action_spec: Type[ActionSpecificationAbc], param: ActionParameter):
        self.action_spec = action_spec
        self.param = param
        super().__init__(f'unknown parameter type {self.param.parameter_type} of parameter {self.param.parameter_name}')

    def __repr__(self):
        return f'The type of the parameter {self.param.parameter_name} in the call to action  {self.action_spec.get_action_id()} of resource ' \
               f'{self.action_spec.get_resource().get_id()} is unknown.\nunknown type: {self.param.parameter_type}'


class UnexpectedParameterError(LibraryError):
    def __init__(self, action_spec: Type[ActionSpecificationAbc], unexpected_params: List[str]):
        self.action_spec = action_spec
        self.unexpected_params = unexpected_params

    def __str__(self):
        return f'received unexpected params: {", ".join(self.unexpected_params)}'

    def __repr__(self):
        return f'unexpected params {", ".join(self.unexpected_params)} in the call to action  {self.action_spec.get_action_id()} of resource ' \
               f'{self.action_spec.get_resource().get_id()}.'


class PresetNotExistError(LibraryError):
    def __init__(self, preset_id: str):
        self.preset_id = preset_id
        super().__init__(f'preset with id {preset_id} not exist')


class PresetAlreadyExistError(LibraryError):
    def __init__(self, preset_id: str):
        self.preset_id = preset_id
        super().__init__(f'preset with id {preset_id} already exist')


class ActionRecipeNotExistError(LibraryError):
    def __init__(self, preset: ActionsGroupPresetObject, action_recipe_id: int):
        self.preset = preset
        self.action_recipe_id = action_recipe_id
        super().__init__(f'action recipe with id {action_recipe_id} not exist in the preset {preset.get_repr()}')


class ParamAlreadyExistError(LibraryError):
    def __init__(self, recipe: ActionRecipeObject, param_key: str):
        self.recipe = recipe
        self.param_key = param_key
        super().__init__(f'parameter {param_key} already exist in the recipe {recipe.action_recipe_id} of the preset {recipe.preset.get_repr()}')


class TaskError(LibraryError, ABC):
    pass


class TaskNotExistError(TaskError):
    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f'task {task_id} not exist')


class TaskPathNotExistError(TaskError):
    def __init__(self, task_id: int, task_path: List[int]):
        self.task_id = task_id
        self.task_path = task_path
        super().__init__(f'task with path {task_path} not exist in task {task_id} not exist')


class TaskAlreadyFinishedError(TaskError):
    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f'task {task_id} already finished')


class TaskNotFinishedError(TaskError):
    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f'task {task_id} has not finished')


class EmptyTaskPathError(TaskError):
    def __init__(self):
        super().__init__(f'recieved an empty task path')


class NotTaskGroupError(TaskError):
    def __init__(self):
        super().__init__(f'you trying to use tasks group functionallity on non tasks group')


class TaskDismissedError(TaskError):
    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f'you have tried to access task {task_id} which have already been dismissed')


class TaskNotInitiatedError(TaskError):
    def __init__(self):
        super().__init__('task not initiated')


class RequiredRequestArgumentMissingError(LibraryError):
    def __init__(self, arg_name: str):
        self.arg_name = arg_name
        super().__init__(f'argument "{arg_name}" is missing in the request')


class IncorrectRequestArgumentTypeError(LibraryError):
    def __init__(self, arg_name: str, expected_type: type, val):
        self.arg_name = arg_name
        self.expected_type = expected_type
        self.val = val
        super().__init__(f'argument "{arg_name}" has incorrect type. expected {str(expected_type)}, received: {val}')


class IlegalValueError(LibraryError):
    def __init__(self, arg_name: str, value, error_msg: str):
        self.arg_name = arg_name
        self.value = value
        self.error_msg = error_msg
        super().__init__(f'argument "{self.arg_name}" has ilegal value: {self.value}. {error_msg}')


class LibraryValueError(LibraryError):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class DatabaseError(LibraryError):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class DatabaseNotInitiatedError(DatabaseError):
    def __init__(self):
        super().__init__('DB is not initiated')


class RequestTypeError(LibraryError):
    def __init__(self, msg: str):
        super().__init__(msg)


@dataclass
class ExceptionMessage:
    message: str
    representation: str
    traceback: str
    type: str

    @classmethod
    def build_from_exception(cls, exc_val: Exception) -> ExceptionMessage:
        return ExceptionMessage(str(exc_val), repr(exc_val), '\n'.join(traceback.format_exception(exc_val.__class__,
                                                                                                  exc_val,
                                                                                                  exc_val.__traceback__)),
                                exc_val.__class__.__name__)
