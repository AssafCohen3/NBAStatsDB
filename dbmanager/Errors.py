from __future__ import annotations

import typing
from abc import ABC
from typing import Dict, List, Type

from dbmanager.AppI18n import gettext

if typing.TYPE_CHECKING:
    from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc
    from dbmanager.Resources.ActionsGroupsPresets.ActionRecipeObject import ActionRecipeObject
    from dbmanager.Resources.ActionsGroupsPresets.ActionsGroupPresetObject import ActionsGroupPresetObject


class ActionNotExistError(Exception):
    def __init__(self, resource_id: str, action_id: str):
        self.resource_id = resource_id
        self.action_id = action_id
        super().__init__(gettext('errors.action_not_exist', resource_id=resource_id, action_id=action_id))


class InvalidActionCallError(Exception):
    def __init__(self, action_spec: Type[ActionSpecificationAbc], params: Dict[str, str], error_msg: str):
        self.action_spec = action_spec
        self.params = params
        self.error_msg = error_msg
        super().__init__(gettext('errors.invalid_action', resource_id=action_spec.get_resource().get_id(), action_id=action_spec.get_action_id(), params=params, error_msg=error_msg))


class ActionFailedError(Exception):
    def __init__(self, action_spec: Type[ActionSpecificationAbc], msg: str):
        super().__init__(f'could not complete the action {action_spec.get_action_title()} of resource {action_spec.get_resource().get_name()}.\n{msg}')


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


class PresetNotExistError(Exception):
    def __init__(self, preset_id: str):
        self.preset_id = preset_id
        super().__init__(f'preset with id {preset_id} not exist')


class PresetAlreadyExistError(Exception):
    def __init__(self, preset_id: str):
        self.preset_id = preset_id
        super().__init__(f'preset with id {preset_id} already exist')


class ActionRecipeNotExistError(Exception):
    def __init__(self, preset: ActionsGroupPresetObject, action_recipe_id: int):
        self.preset = preset
        self.action_recipe_id = action_recipe_id
        super().__init__(f'action recipe with id {action_recipe_id} not exist in the preset {preset.get_repr()}')


class ParamAlreadyExistError(Exception):
    def __init__(self, recipe: ActionRecipeObject, param_key: str):
        self.recipe = recipe
        self.param_key = param_key
        super().__init__(f'parameter {param_key} already exist in the recipe {recipe.action_recipe_id} of the preset {recipe.preset.get_repr()}')


class TaskError(Exception, ABC):
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


class RequiredRequestArgumentMissing(Exception):
    def __init__(self, arg_name: str):
        self.arg_name = arg_name
        super().__init__(f'argument "{arg_name}" is missing in the request')


class IncorrectRequestArgumentType(Exception):
    def __init__(self, arg_name: str, expected_type: type, val):
        self.arg_name = arg_name
        self.expected_type = expected_type
        self.val = val
        super().__init__(f'argument "{arg_name}" has incorrect type. expected {str(expected_type)}, received: {val}')


class IlegalValueError(Exception):
    def __init__(self, arg_name: str, value, error_msg: str):
        self.arg_name = arg_name
        self.value = value
        self.error_msg = error_msg
        super().__init__(f'argument "{self.arg_name}" has ilegal value: {self.value}. {error_msg}')
