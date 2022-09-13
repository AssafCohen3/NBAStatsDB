from dataclasses import dataclass
from typing import List, Type, Tuple, Dict

from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.Resources.ActionsGroupsPresets.ActionRecipe import ActionRecipe


@dataclass
class ActionsGroupPreset:
    preset_id: str
    preset_name_key: str
    action_recipes: List[ActionRecipe]


def create_actions_group_preset(preset_id: str, preset_name_key: str,
                                actions_classes_with_params: List[Tuple[Type[ActionAbc], Dict[str, str]]]):
    actions_recipes = [
        ActionRecipe(preset_id, action_cls, order, params)
        for order, (action_cls, params) in enumerate(actions_classes_with_params)
    ]
    return ActionsGroupPreset(preset_id, preset_name_key, actions_recipes)
