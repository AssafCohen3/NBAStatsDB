import logging
from typing import List

import flask
from flask import Blueprint, jsonify, request

from dbmanager.Errors import TaskError
from dbmanager.extensions import announcer
from dbmanager.tasks.TaskManager import get_tasks_messages, pause_task, resume_task, cancel_task, \
    dismiss_task
from dbmanager.utils import flask_request_validation

tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')


@tasks_bp.route('/', methods=['GET'])
def get_tasks_list():
    to_ret = get_tasks_messages()
    to_ret = jsonify(to_ret)
    return to_ret


@tasks_bp.route('/pause_task', methods=['POST'])
@flask_request_validation
def pause_task_route(task_path: List[int]):
    pause_task(task_path)
    return 'ok'


@tasks_bp.route('/resume_task', methods=['POST'])
@flask_request_validation
def resume_task_route(task_path: List[int]):
    resume_task(task_path)
    return 'ok'


@tasks_bp.route('/cancel_task', methods=['POST'])
@flask_request_validation
def cancel_task_route(task_path: List[int]):
    cancel_task(task_path)
    return 'ok'


@tasks_bp.route('/dismiss_task', methods=['POST'])
@flask_request_validation
def dismiss_task_route(task_path: List[int]):
    dismiss_task(task_path)
    return 'ok'


@tasks_bp.route('/listen', methods=['GET'])
def listen():
    logging.info('client connected')

    def stream():
        listener_id, messages = announcer.listen()
        try:
            first_msg = 'event: first\ndata: {}\n\n'
            yield first_msg
            while True:
                msg: str = messages.get()
                yield msg
        finally:
            logging.info('client disconnected')
            announcer.unlisten(listener_id)
    return flask.Response(stream(), mimetype='text/event-stream')
