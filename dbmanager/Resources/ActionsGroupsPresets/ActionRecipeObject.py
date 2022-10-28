from __future__ import annotations

import typing
from dataclasses import dataclass
from typing import Dict, Type
from dbmanager.Resources.Actions.ActionAbc import ActionAbc

if typing.TYPE_CHECKING:
    from dbmanager.Resources.ActionsGroupsPresets.ActionsGroupPresetObject import ActionsGroupPresetObject


@dataclass
class ActionRecipeObject:
    preset: 'ActionsGroupPresetObject'
    action_recipe_id: int
    action_cls: Type[ActionAbc]
    order: int
    params: Dict[str, str]

    def to_dict(self):
        return {
            'preset_id': self.preset.preset_id,
            'action_recipe_id': self.action_recipe_id,
            'action_id': self.action_cls.get_action_id(),
            'action_title': self.action_cls.get_action_spec().get_action_title(),
            'resource_id': self.action_cls.get_action_spec().get_resource().get_id(),
            'resource_name': self.action_cls.get_action_spec().get_resource().get_name(),
            'order': self.order,
            'params': self.params
        }
