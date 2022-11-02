import json
from typing import Dict, List, Type, Optional
from sqlalchemy import insert, update, delete, and_
from sqlalchemy.orm import scoped_session
from dbmanager.AppI18n import get_default_locale
from dbmanager.Database.Models.ActionRecipe import ActionRecipe
from dbmanager.Database.Models.ActionRecipeParam import ActionRecipeParam
from dbmanager.Database.Models.ActionsGroupPreset import ActionsGroupPreset
from dbmanager.Errors import PresetNotExistError, PresetAlreadyExistError, ActionRecipeNotExistError, IlegalValueError, \
    LibraryValueError
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.Resources.ActionsGroupsPresets.ActionsGroupPresetObject import ActionsGroupPresetObject
from dbmanager.SharedData.CachedData import CachedData, refresh_function, DontRefreshCacheError
from dbmanager.utils import safe_session_execute


class PresetsManager:
    def __init__(self, session: scoped_session, cached_presets: CachedData[Dict[str, ActionsGroupPresetObject]]):
        self.session = session
        self.presets_cache = cached_presets

    def get_presets_cache(self) -> CachedData[Dict[str, ActionsGroupPresetObject]]:
        return self.presets_cache

    def get_presets(self) -> Dict[str, ActionsGroupPresetObject]:
        return self.presets_cache.get_data()

    def get_actions_presets_list(self) -> List[Dict]:
        to_ret = [
            {
                'preset_id': actions_preset.preset_id,
                'preset_name': actions_preset.preset_name.get_value(),
            }
            for actions_preset in self.get_presets().values()
        ]
        return to_ret

    def get_actions_preset_details(self, preset_id: str) -> Dict:
        if preset_id not in self.get_presets():
            raise PresetNotExistError(preset_id)
        preset = self.get_presets()[preset_id]
        to_ret = {
            'preset_id': preset.preset_id,
            'preset_name': preset.preset_name.get_value(),
            'action_recipes': [recipe.to_dict() for recipe in preset.action_recipes.values()]
        }
        return to_ret

    def get_extended_actions_presets_list(self) -> List[Dict]:
        to_ret = [
            {
                'preset_id': actions_preset.preset_id,
                'preset_name': actions_preset.preset_name.get_value(),
                'preset_name_json': actions_preset.preset_name.get_translations(),
                'action_recipes': [recipe.to_dict() for recipe in actions_preset.action_recipes.values()]
            }
            for actions_preset in self.get_presets().values()
        ]
        return to_ret

    @refresh_function(get_presets_cache)
    def create_preset(self, preset_id: str, preset_name_json: Dict[str, str]) -> str:
        if preset_id in self.get_presets():
            raise PresetAlreadyExistError(preset_id)
        default_locale = get_default_locale()
        if not preset_name_json.get(default_locale):
            raise LibraryValueError(f'received preset name is missing the default translation locale ({default_locale})')
        insert_stmt = insert(ActionsGroupPreset)
        with safe_session_execute(self.session):
            self.session.execute(insert_stmt, {
                'ActionsGroupPresetId': preset_id,
                'PresetTranslatableNameJson': json.dumps(preset_name_json)
            })
            self.session.commit()
        return preset_id

    @refresh_function(get_presets_cache)
    def edit_preset(self, preset_id: str, preset_name_json: Dict[str, str]) -> str:
        if preset_id not in self.get_presets():
            raise PresetNotExistError(preset_id)
        default_locale = get_default_locale()
        if not preset_name_json.get(default_locale):
            raise LibraryValueError(f'received preset name is missing the default translation locale ({default_locale})')
        update_stmt = (
            update(ActionsGroupPreset)
            .where(ActionsGroupPreset.ActionsGroupPresetId == preset_id)
            .values(PresetTranslatableNameJson=json.dumps(preset_name_json))
        )
        with safe_session_execute(self.session):
            self.session.execute(update_stmt)
            self.session.commit()
        return preset_id

    @refresh_function(get_presets_cache)
    def remove_preset(self, preset_id: str) -> str:
        if preset_id not in self.get_presets():
            raise PresetNotExistError(preset_id)
        delete_stmt = (
            delete(ActionsGroupPreset)
            .where(ActionsGroupPreset.ActionsGroupPresetId == preset_id)
        )
        with safe_session_execute(self.session):
            self.session.execute(delete_stmt)
            self.session.commit()
        return preset_id

    @refresh_function(get_presets_cache)
    def create_action_recipe(self, preset_id: str, action_cls: Type[ActionAbc], order: int, params: Dict[str, str]) -> int:
        preset = self.get_presets().get(preset_id)
        if not preset:
            raise PresetNotExistError(preset_id)
        if order < 0:
            raise IlegalValueError('order', order, 'order must be a non negative integer')
        # keep orders sequential
        order = min(order, preset.next_available_order())
        # insert new recipe
        action_to_insert = {
            'ActionsGroupPresetId': preset_id,
            'ResourceId': action_cls.get_action_spec().get_resource().get_id(),
            'ActionId': action_cls.get_action_spec().get_action_id(),
            'Order': order
        }
        insert_stmt = (
            insert(ActionRecipe)
        )
        with safe_session_execute(self.session):
            new_action_recipe_id = self.session.execute(insert_stmt, action_to_insert).lastrowid
            # move other recipes down
            update_rest_stmt = (
                update(ActionRecipe)
                .where(and_(ActionRecipe.ActionsGroupPresetId == preset_id, ActionRecipe.ActionRecipeId != new_action_recipe_id, ActionRecipe.Order >= order))
                .values(Order=ActionRecipe.Order+1)
            )
            self.session.execute(update_rest_stmt)
            # insert params
            params_to_insert = [
                {
                    'ActionRecipeId': new_action_recipe_id,
                    'ParamKey': key,
                    'ParamValue': value
                }
                for key, value in params.items()
            ]
            if params_to_insert:
                self.session.execute(insert(ActionRecipeParam, params_to_insert))
            self.session.commit()
        return new_action_recipe_id

    @refresh_function(get_presets_cache)
    def edit_action_recipe_params(self, preset_id: str, recipe_id: int, params: Dict[str, str]) -> int:
        preset = self.get_presets().get(preset_id)
        if not preset:
            raise PresetNotExistError(preset_id)
        recipe = preset.action_recipes.get(recipe_id)
        if not recipe:
            raise ActionRecipeNotExistError(preset, recipe_id)
        delete_stmt = delete(ActionRecipeParam).where(ActionRecipeParam.ActionRecipeId == recipe_id)
        with safe_session_execute(self.session):
            self.session.execute(delete_stmt)
            params_to_insert = [
                {
                    'ActionRecipeId': recipe_id,
                    'ParamKey': key,
                    'ParamValue': value
                }
                for key, value in params.items()
            ]
            if params_to_insert:
                self.session.execute(insert(ActionRecipeParam, params_to_insert))
            self.session.commit()
        return recipe_id

    @refresh_function(get_presets_cache)
    def change_action_recipe_order(self, preset_id: str, recipe_id: int, new_order: int) -> int:
        preset = self.get_presets().get(preset_id)
        if not preset:
            raise PresetNotExistError(preset_id)
        recipe = preset.action_recipes.get(recipe_id)
        if not recipe:
            raise ActionRecipeNotExistError(preset, recipe_id)
        if new_order < 0:
            raise IlegalValueError('new_order', new_order, 'new_order must be a non negative integer')
        # keep orders sequential
        new_order = min(new_order, preset.next_available_order(recipe_id))
        if new_order == recipe.order:
            raise DontRefreshCacheError(None)
        update_recipe_stmt = (
            update(ActionRecipe)
            .where(and_(ActionRecipe.ActionsGroupPresetId == preset_id, ActionRecipe.ActionRecipeId == recipe_id))
            .values(Order=new_order)
        )
        offset = 1 if new_order < recipe.order else -1
        lower_bound, higher_bound = min(new_order, recipe.order), max(new_order, recipe.order)
        update_rest_stmt = (
            update(ActionRecipe)
            .where(and_(ActionRecipe.ActionsGroupPresetId == preset_id,
                        ActionRecipe.ActionRecipeId != recipe_id,
                        ActionRecipe.Order >= lower_bound, ActionRecipe.Order <= higher_bound))
            .values(Order=ActionRecipe.Order+offset)
        )
        with safe_session_execute(self.session):
            self.session.execute(update_recipe_stmt)
            self.session.execute(update_rest_stmt)
            self.session.commit()
        return recipe_id

    @refresh_function(get_presets_cache)
    def delete_action_recipe(self, preset_id: str, recipe_id: int) -> int:
        preset = self.get_presets().get(preset_id)
        if not preset:
            raise PresetNotExistError(preset_id)
        recipe = preset.action_recipes.get(recipe_id)
        if not recipe:
            raise ActionRecipeNotExistError(preset, recipe_id)
        delete_recipe_stmt = (
            delete(ActionRecipe)
            .where(and_(ActionRecipe.ActionsGroupPresetId == preset_id, ActionRecipe.ActionRecipeId == recipe_id))
        )
        update_rest_stmt = (
            update(ActionRecipe)
            .where(and_(ActionRecipe.ActionsGroupPresetId == preset_id, ActionRecipe.ActionRecipeId != recipe_id, ActionRecipe.Order > recipe.order))
            .values(Order=ActionRecipe.Order-1)
        )
        with safe_session_execute(self.session):
            self.session.execute(delete_recipe_stmt)
            self.session.execute(update_rest_stmt)
            self.session.commit()
        return recipe_id

    def copy_action_recipe(self, preset_id: str, recipe_id: int, new_preset_id: str, order_in_new_preset: int) -> Optional[int]:
        preset = self.get_presets().get(preset_id)
        if not preset:
            raise PresetNotExistError(preset_id)
        recipe = preset.action_recipes.get(recipe_id)
        if not recipe:
            raise ActionRecipeNotExistError(preset, recipe_id)
        new_preset = self.get_presets().get(new_preset_id)
        if not new_preset:
            raise PresetNotExistError(new_preset_id)
        if order_in_new_preset < 0:
            raise IlegalValueError('order_in_new_preset', order_in_new_preset, 'order_in_new_preset must be a non negative integer')
        if preset_id == new_preset_id:
            return None
        # keep orders sequential
        order_in_new_recipe = min(order_in_new_preset, new_preset.next_available_order())
        return self.create_action_recipe(new_preset_id, recipe.action_cls, order_in_new_recipe, recipe.params)
