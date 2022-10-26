from dataclasses import dataclass
from typing import List, Type, Tuple, Dict

from dbmanager.AppI18n import TranslatableField
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.Resources.ActionsGroupsPresets.ActionRecipeObject import ActionRecipeObject


@dataclass
class ActionsGroupPresetObject:
    preset_id: str
    preset_name: TranslatableField
    action_recipes: Dict[int, ActionRecipeObject]

    def get_repr(self) -> str:
        return f'{self.preset_name.get_value()}({self.preset_id})'


def create_actions_group_preset(preset_id: str, preset_name: TranslatableField,
                                actions_classes_with_params: List[Tuple[int, Type[ActionAbc], int, Dict[str, str]]]):
    preset = ActionsGroupPresetObject(preset_id, preset_name, {})
    actions_recipes = {
        action_recipe_id: ActionRecipeObject(preset, action_recipe_id, action_cls, order, params)
        for action_recipe_id, action_cls, order, params in actions_classes_with_params
    }
    preset.action_recipes.update(actions_recipes)
    return preset
