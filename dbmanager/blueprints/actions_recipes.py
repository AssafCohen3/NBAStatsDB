from typing import Dict

from flask import Blueprint
from dbmanager.extensions import db_manager
from dbmanager.utils import with_flask_parameters

actions_recipes_bp = Blueprint('actions recipes', __name__, url_prefix='/actions_recipes')


@actions_recipes_bp.route('/create', methods=['POST'])
@with_flask_parameters([
    ('preset_id', str),
    ('resource_id', str),
    ('action_id', str),
    ('order', int),
    ('params', dict)
])
def create_action_recipe(preset_id: str, resource_id: str, action_id: str, order: int, params: Dict) -> str:
    return str(db_manager.create_action_recipe(preset_id, resource_id, action_id, order, params))


@actions_recipes_bp.route('/update_params', methods=['POST'])
@with_flask_parameters([
    ('preset_id', str),
    ('recipe_id', int),
    ('params', dict)
])
def edit_action_recipe_params(preset_id: str, recipe_id: int, params: Dict) -> str:
    return str(db_manager.edit_action_recipe_params(preset_id, recipe_id, params))


@actions_recipes_bp.route('/update_order', methods=['POST'])
@with_flask_parameters([
    ('preset_id', str),
    ('recipe_id', int),
    ('new_order', int)
])
def change_action_recipe_order(preset_id: str, recipe_id: int, new_order: int) -> str:
    return str(db_manager.change_action_recipe_order(preset_id, recipe_id, new_order))


@actions_recipes_bp.route('/delete', methods=['POST'])
@with_flask_parameters([
    ('preset_id', str),
    ('recipe_id', int),
])
def delete_action_recipe(preset_id: str, recipe_id: int) -> str:
    return str(db_manager.delete_action_recipe(preset_id, recipe_id))
