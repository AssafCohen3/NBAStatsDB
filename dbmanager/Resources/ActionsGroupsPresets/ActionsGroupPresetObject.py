from dataclasses import dataclass
from typing import List, Type, Tuple, Dict

from dbmanager.AppI18n import TranslatableField
from dbmanager.Database.Models.ActionsGroupPreset import ActionsGroupPreset
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.Resources.ActionsGroupsPresets.ActionRecipeObject import ActionRecipeObject


@dataclass
class ActionsGroupPresetObject:
    preset_id: int
    preset_name: TranslatableField
    action_recipes: List[ActionRecipeObject]


def create_actions_group_preset(preset_id: int, preset_name: TranslatableField,
                                actions_classes_with_params: List[Tuple[Type[ActionAbc], Dict[str, str]]]):
    actions_recipes = [
        ActionRecipeObject(preset_id, action_cls, order, params)
        for order, (action_cls, params) in enumerate(actions_classes_with_params)
    ]
    return ActionsGroupPresetObject(preset_id, preset_name, actions_recipes)
