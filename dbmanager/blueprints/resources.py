from typing import Dict

from flask import Blueprint, jsonify
from dbmanager.extensions import db_manager
from dbmanager.tasks.TaskManager import enqueue_task
from dbmanager.utils import flask_request_validation

resources_bp = Blueprint('resources', __name__, url_prefix='/resources')


@resources_bp.route('/', methods=['GET'])
def get_resources_list():
    to_ret = db_manager.get_resources_with_actions_compact()
    to_ret = jsonify(to_ret)
    return to_ret


@resources_bp.route('/<resource_id>', methods=['GET'])
@flask_request_validation
def get_resource_details(resource_id: str):
    to_ret = db_manager.get_resource_details(resource_id)
    to_ret = jsonify(to_ret)
    return to_ret


@resources_bp.route('/<resource_id>/actions/<action_id>', methods=['GET'])
@flask_request_validation
def get_action_spec(resource_id: str, action_id: str):
    to_ret = db_manager.get_action_spec(resource_id, action_id)
    to_ret = jsonify(to_ret)
    return to_ret


@resources_bp.route('/<resource_id>/actions/<action_id>/dispatch', methods=['POST'])
@flask_request_validation
def dispatch_action(resource_id: str, action_id: str, params: Dict[str, str]):
    action_to_run = db_manager.dispatch_action(resource_id, action_id, params)
    enqueue_task(action_to_run)
    return 'ok'
