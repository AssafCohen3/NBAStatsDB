import asyncio
import itertools
from typing import Dict, List

from dbmanager.Errors import TaskNotExist, TaskAlreadyFinished, TaskNotFinished
from dbmanager.RequestHandlers.Limiter import stats_limiter
from dbmanager.Resources.Actions.ActionAbc import ActionAbc
from dbmanager.tasks.TaskMessage import TaskMessage


def run_tasks_loop():
    asyncio.set_event_loop(actions_loop)
    # TODO check this
    stats_limiter.init_async()
    actions_loop.run_forever()


actions_loop = asyncio.new_event_loop()
current_task_id = itertools.count()
actions_dictionary: Dict[int, ActionAbc] = {}


def enqueue_action(action: ActionAbc, done_callback=None):
    async def adder_coro():
        task_id = next(current_task_id)
        action.set_task_id(task_id)
        actions_dictionary[task_id] = action
        await action

    future = asyncio.run_coroutine_threadsafe(adder_coro(), actions_loop)
    if done_callback:
        future.add_done_callback(done_callback)


def get_tasks_messages() -> List[TaskMessage]:
    tasks_statuses = [task.to_task_message() for task_id, task in actions_dictionary.items()]
    return tasks_statuses


def get_task_message(task_id: int) -> TaskMessage:
    if task_id not in actions_dictionary:
        raise TaskNotExist(task_id)
    task = actions_dictionary[task_id]
    return task.to_task_message()


def pause_task(task_id: int):
    if task_id not in actions_dictionary:
        raise TaskNotExist(task_id)
    if actions_dictionary[task_id].is_finished():
        raise TaskAlreadyFinished(task_id)
    actions_dictionary[task_id].pause()


def resume_task(task_id: int):
    if task_id not in actions_dictionary:
        raise TaskNotExist(task_id)
    if actions_dictionary[task_id].is_finished():
        raise TaskAlreadyFinished(task_id)
    actions_dictionary[task_id].resume()


def cancel_task(task_id: int):
    if task_id not in actions_dictionary:
        raise TaskNotExist(task_id)
    if actions_dictionary[task_id].is_finished():
        raise TaskAlreadyFinished(task_id)
    actions_dictionary[task_id].cancel_task()


def dismiss_task(task_id: int):
    if task_id not in actions_dictionary:
        raise TaskNotExist(task_id)
    if not actions_dictionary[task_id].is_finished():
        raise TaskNotFinished(task_id)
    del actions_dictionary[task_id]
