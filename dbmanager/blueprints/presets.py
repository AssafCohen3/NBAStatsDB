from flask import Blueprint, jsonify
from dbmanager.extensions import db_manager
from dbmanager.tasks.TaskManager import enqueue_task

presets_bp = Blueprint('presets', __name__, url_prefix='/presets')


@presets_bp.route('/', methods=['GET'])
def get_presets_list():
    to_ret = db_manager.get_actions_presets_list()
    to_ret = jsonify(to_ret)
    return to_ret


@presets_bp.route('/<preset_id>', methods=['GET'])
def get_preset_details(preset_id):
    to_ret = db_manager.get_actions_preset_details(preset_id)
    to_ret = jsonify(to_ret)
    return to_ret


@presets_bp.route('/<preset_id>/dispatch', methods=['POST'])
def dispatch_actions_preset(preset_id: str):
    preset_to_run = db_manager.dispatch_preset(preset_id)
    enqueue_task(preset_to_run)
    return 'ok'
