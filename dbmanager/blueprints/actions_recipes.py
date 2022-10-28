from typing import Dict

from flask import Blueprint
from dbmanager.extensions import db_manager
from dbmanager.utils import flask_request_validation

actions_recipes_bp = Blueprint('actions recipes', __name__)


@actions_recipes_bp.route('/', methods=['POST'])
@flask_request_validation
def create_action_recipe(preset_id: str, resource_id: str, action_id: str, order: int, params: Dict[str, str]) -> str:
    return str(db_manager.create_action_recipe(preset_id, resource_id, action_id, order, params))


@actions_recipes_bp.route('/<int:recipe_id>/update_params', methods=['PUT'])
@flask_request_validation
def edit_action_recipe_params(preset_id: str, recipe_id: int, params: Dict[str, str]) -> str:
    return str(db_manager.edit_action_recipe_params(preset_id, recipe_id, params))


@actions_recipes_bp.route('/<int:recipe_id>/update_order', methods=['PUT'])
@flask_request_validation
def change_action_recipe_order(preset_id: str, recipe_id: int, new_order: int) -> str:
    return str(db_manager.change_action_recipe_order(preset_id, recipe_id, new_order))


@actions_recipes_bp.route('/<int:recipe_id>/copy', methods=['POST'])
@flask_request_validation
def copy_action_recipe(preset_id: str, recipe_id: int, new_preset_id: str, order_in_new_preset: int) -> str:
    return str(db_manager.copy_action_recipe(preset_id, recipe_id, new_preset_id, order_in_new_preset))


@actions_recipes_bp.route('/<int:recipe_id>', methods=['DELETE'])
@flask_request_validation
def delete_action_recipe(preset_id: str, recipe_id: int) -> str:
    return str(db_manager.delete_action_recipe(preset_id, recipe_id))
