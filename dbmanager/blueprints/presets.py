from typing import Dict

from flask import Blueprint, jsonify

from dbmanager.blueprints.actions_recipes import actions_recipes_bp
from dbmanager.extensions import db_manager
from dbmanager.tasks.TaskManager import enqueue_task
from dbmanager.utils import with_flask_parameters

presets_bp = Blueprint('presets', __name__, url_prefix='/presets')
presets_bp.register_blueprint(actions_recipes_bp)


@presets_bp.route('/', methods=['GET'])
def get_presets_list():
    to_ret = db_manager.get_actions_presets_list()
    to_ret = jsonify(to_ret)
    return to_ret


@presets_bp.route('/extended', methods=['GET'])
def get_extended_presets_list():
    to_ret = db_manager.get_extended_actions_presets_list()
    to_ret = jsonify(to_ret)
    return to_ret


@presets_bp.route('/details/<preset_id>', methods=['GET'])
def get_preset_details(preset_id):
    to_ret = db_manager.get_actions_preset_details(preset_id)
    to_ret = jsonify(to_ret)
    return to_ret


@presets_bp.route('/dispatch/<preset_id>', methods=['POST'])
def dispatch_actions_preset(preset_id: str):
    preset_to_run = db_manager.dispatch_preset(preset_id)
    enqueue_task(preset_to_run)
    return 'ok'


@presets_bp.route('/create', methods=['POST'])
@with_flask_parameters([
    ('preset_id', str),
    ('preset_name_json', dict)
])
def create_preset(preset_id: str, preset_name_json: Dict) -> str:
    return db_manager.create_preset(preset_id, preset_name_json)


@presets_bp.route('/update', methods=['POST'])
@with_flask_parameters([
    ('preset_id', str),
    ('preset_name_json', dict)
])
def edit_preset(preset_id: str, preset_name_json: Dict) -> str:
    return db_manager.edit_preset(preset_id, preset_name_json)


@presets_bp.route('/delete', methods=['POST'])
@with_flask_parameters([
    ('preset_id', str),
])
def remove_preset(preset_id: str) -> str:
    return db_manager.remove_preset(preset_id)
