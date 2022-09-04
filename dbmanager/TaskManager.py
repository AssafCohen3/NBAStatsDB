import asyncio
import itertools
import logging
from typing import Dict, List, Any

from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.extensions import socketio


def run_tasks_loop():
    asyncio.set_event_loop(actions_loop)
    socketio.emit('action-exception')
    actions_loop.run_forever()


actions_loop = asyncio.new_event_loop()
current_task_id = itertools.count()
actions_dictionary: Dict[int, ActionAbc] = {}


def enqueue_action(action: ActionAbc, done_callback=None):
    async def adder_coro():
        logging.debug('enqueuing task async...')
        task_id = next(current_task_id)
        action.set_task_id(task_id)
        actions_dictionary[task_id] = action
        await action
        del actions_dictionary[task_id]

    future = asyncio.run_coroutine_threadsafe(adder_coro(), actions_loop)
    if done_callback:
        future.add_done_callback(done_callback)


def get_statuses() -> List[Dict[str, Any]]:
    tasks_statuses = [{
        'task_id': task_id,
        'action_id': task.get_action_spec().get_action_id(),
        'subtasks_count': task.subtasks_count(),
        'subtasks_completed': task.subtasks_completed(),
        'status': task.current_status(),
        'current_subtask_text': task.get_current_subtask_text()
    } for task_id, task in actions_dictionary.items()]
    return tasks_statuses


def pause_task(task_id: int):
    # TODO check task exist
    actions_dictionary[task_id].pause()


def resume_task(task_id: int):
    # async def resume_coro():
    #     actions_dictionary[task_id].resume()
    # asyncio.run_coroutine_threadsafe(resume_coro(), actions_loop)
    actions_dictionary[task_id].resume()


def cancel_task(task_id: int):
    actions_dictionary[task_id].cancel_task()
