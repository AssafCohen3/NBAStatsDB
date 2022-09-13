from __future__ import annotations
import itertools
import json
import logging
import typing
from abc import ABC, abstractmethod
from dataclasses import asdict
from queue import Queue
from typing import Dict, Tuple, List

if typing.TYPE_CHECKING:
    from dbmanager.tasks.TaskAbc import TaskAbc


class AnnouncerAbc(ABC):
    @abstractmethod
    def announce(self, event: str, task_path: List[int], task: TaskAbc):
        pass


class TaskAnnouncer(AnnouncerAbc):
    def __init__(self):
        self.listeners: Dict[int, Queue] = {}
        self.next_id = itertools.count()

    def listen(self) -> Tuple[int, Queue]:
        q = Queue()
        listener_id = next(self.next_id)
        self.listeners[listener_id] = q
        return listener_id, q

    def unlisten(self, listener_id: int):
        del self.listeners[listener_id]

    def announce(self, event: str, task_path: List[int], task: TaskAbc):
        to_send = format_sse(event, task_path, task)
        logging.info(f'announcing {to_send}')
        for q in self.listeners.values():
            q.put_nowait(to_send)


def format_sse(event: str, task_path: List[int], task: TaskAbc) -> str:
    data_to_send = {
        'task_path': task_path,
        'task_message': asdict(task.to_task_message())
    }
    to_ret = f'event: {event}\ndata: {json.dumps(data_to_send)}\n\n'
    return to_ret
