from typing import Dict, Optional

from flask import Blueprint, jsonify

from dbmanager.blueprints.actions_recipes import actions_recipes_bp
from dbmanager.extensions import db_manager
from dbmanager.tasks.TaskManager import enqueue_task
from dbmanager.utils import flask_request_validation

presets_bp = Blueprint('presets', __name__, url_prefix='/presets')
presets_bp.register_blueprint(actions_recipes_bp, url_prefix='/<preset_id>/actions_recipes')


@presets_bp.route('/', methods=['GET'])
def get_presets_list():
    to_ret = db_manager.get_extended_actions_presets_list()
    to_ret = jsonify(to_ret)
    return to_ret


@presets_bp.route('/<preset_id>/', methods=['GET'])
@flask_request_validation
def get_preset_details(preset_id: str):
    to_ret = db_manager.get_actions_preset_details(preset_id)
    to_ret = jsonify(to_ret)
    return to_ret


@presets_bp.route('/<preset_id>/dispatch', methods=['POST'])
@flask_request_validation
def dispatch_actions_preset(preset_id: str):
    preset_to_run = db_manager.dispatch_preset(preset_id)
    enqueue_task(preset_to_run)
    return 'ok'


@presets_bp.route('/', methods=['POST'])
@flask_request_validation
def create_preset(preset_id: str, preset_name_json: Dict[str, str]) -> str:
    return db_manager.create_preset(preset_id, preset_name_json)


@presets_bp.route('/<preset_id>', methods=['PUT'])
@flask_request_validation
def edit_preset(preset_id: str, preset_name_json: Dict[str, Optional[str]]) -> str:
    return db_manager.edit_preset(preset_id, preset_name_json)


@presets_bp.route('/<preset_id>', methods=['DELETE'])
@flask_request_validation
def remove_preset(preset_id: str) -> str:
    return db_manager.remove_preset(preset_id)
