from flask import Blueprint, jsonify, request
from dbmanager.extensions import db_manager
from dbmanager.tasks.TaskManager import enqueue_task

resources_bp = Blueprint('resources', __name__, url_prefix='/resources')


@resources_bp.route('/', methods=['GET'])
def get_resources_list():
    to_ret = db_manager.get_resources_list_compact()
    to_ret = jsonify(to_ret)
    return to_ret


@resources_bp.route('/<resource_id>', methods=['GET'])
def get_resource_details(resource_id):
    to_ret = db_manager.get_resource_details(resource_id)
    to_ret = jsonify(to_ret)
    return to_ret


@resources_bp.route('/<resource_id>/actions/<action_id>', methods=['POST'])
def dispatch_action(resource_id: str, action_id: str):
    action_to_run = db_manager.dispatch_action(resource_id, action_id, request.json)
    enqueue_task(action_to_run)
    return 'ok'
