import asyncio
import itertools
from typing import Dict, List
from dbmanager.Errors import EmptyTaskPathError, TaskNotExistError
from dbmanager.RequestHandlers.Limiter import stats_limiter
from dbmanager.extensions import announcer
from dbmanager.tasks.TaskAbc import TaskAbc
from dbmanager.tasks.TaskMessage import TaskMessage


def run_tasks_loop():
    asyncio.set_event_loop(tasks_loop)
    # TODO check this
    stats_limiter.init_async()
    tasks_loop.run_forever()


tasks_loop = asyncio.new_event_loop()
current_task_id = itertools.count()
tasks_dictionary: Dict[int, TaskAbc] = {}


def enqueue_task(task: TaskAbc, done_callback=None):
    async def adder_coro():
        task.init_task(current_task_id, announcer)
        tasks_dictionary[task.get_task_id()] = task
        await task
        task.after_execution_finished()

    future = asyncio.run_coroutine_threadsafe(adder_coro(), tasks_loop)
    if done_callback:
        future.add_done_callback(done_callback)


def get_tasks_messages() -> List[TaskMessage]:
    tasks_statuses = [task.to_task_message() for task_id, task in tasks_dictionary.items()]
    return tasks_statuses


def get_task_message(task_path: List[int]) -> TaskMessage:
    if len(task_path) < 1:
        raise EmptyTaskPathError()
    if task_path[0] not in tasks_dictionary:
        raise TaskNotExistError(task_path[0])
    task = tasks_dictionary[task_path[0]]
    return task.get_sub_task(task_path[1:]).to_task_message()


def pause_task(task_path: List[int]):
    if len(task_path) < 1:
        raise EmptyTaskPathError()
    if task_path[0] not in tasks_dictionary:
        raise TaskNotExistError(task_path[0])
    task = tasks_dictionary[task_path[0]]
    task.get_sub_task(task_path[1:]).pause()


def resume_task(task_path: List[int]):
    if len(task_path) < 1:
        raise EmptyTaskPathError()
    if task_path[0] not in tasks_dictionary:
        raise TaskNotExistError(task_path[0])
    task = tasks_dictionary[task_path[0]]
    task.get_sub_task(task_path[1:]).resume()


def cancel_task(task_path: List[int]):
    if len(task_path) < 1:
        raise EmptyTaskPathError()
    if task_path[0] not in tasks_dictionary:
        raise TaskNotExistError(task_path[0])
    task = tasks_dictionary[task_path[0]]
    task.get_sub_task(task_path[1:]).cancel_task()


def dismiss_task(task_path: List[int]):
    if len(task_path) < 1:
        raise EmptyTaskPathError()
    if task_path[0] not in tasks_dictionary:
        raise TaskNotExistError(task_path[0])
    task = tasks_dictionary[task_path[0]]
    task.get_sub_task(task_path[1:]).dismiss_task()
    if len(task_path) == 1:
        del tasks_dictionary[task_path[0]]
