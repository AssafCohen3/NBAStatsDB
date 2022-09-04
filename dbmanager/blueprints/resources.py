import logging

from flask import Blueprint, jsonify, request

from dbmanager.TaskManager import enqueue_action
from dbmanager.extensions import db_manager, socketio

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
    action_to_run.set_start_callback(start_callback)
    action_to_run.set_finish_callback(finish_callback)
    action_to_run.set_mini_finish_callback(mini_finish_callback)
    action_to_run.set_exception_callback(exception_callback)
    action_to_run.set_pause_callback(pause_callback)
    action_to_run.set_resume_callback(resume_callback)
    enqueue_action(action_to_run)
    return 'ok'


def start_callback(action_id: str) -> None:
    logging.info(f'starting action {action_id}')
    socketio.emit('refresh-data')


def finish_callback(action_id: str) -> None:
    logging.info(f'finished action {action_id}')
    socketio.emit('refresh-data')
    # TODO translate
    socketio.emit('add-message', {
        'message': f'finished the execution of {action_id}',
        'message-type': 'success'
    })


def mini_finish_callback(action_id: str) -> None:
    logging.info(f'mini finish in {action_id}')
    socketio.emit('refresh-data')


def exception_callback(action_id: str, exception: Exception) -> None:
    logging.error(f'recieved exception while executing {action_id}. {exception}')
    socketio.emit('refresh-data')
    # TODO translate
    socketio.emit('add-message', {
        'message': f'the execution of {action_id} failed',
        'message-type': 'error'
    })


def pause_callback(action_id: str) -> None:
    logging.info(f'pausing action {action_id}')
    socketio.emit('refresh-data')


def resume_callback(action_id: str) -> None:
    logging.info(f'resuming action {action_id}')
    socketio.emit('refresh-data')
