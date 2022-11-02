from __future__ import annotations
import itertools
import json
import logging
import typing
from abc import ABC, abstractmethod
from dataclasses import asdict
from queue import Queue
from threading import Lock
from typing import Dict, Tuple, List

if typing.TYPE_CHECKING:
    from dbmanager.tasks.TaskAbc import TaskAbc


class AnnouncerAbc(ABC):
    @abstractmethod
    def announce_task_event(self, event: str, task_path: List[int], task: TaskAbc):
        pass

    @abstractmethod
    def announce_data(self, event: str, data: str):
        pass


class TaskAnnouncer(AnnouncerAbc):
    def __init__(self):
        self.listeners: Dict[int, Queue] = {}
        self.next_id = itertools.count()
        self._lock = Lock()

    def listen(self) -> Tuple[int, Queue]:
        q = Queue()
        listener_id = next(self.next_id)
        self.listeners[listener_id] = q
        return listener_id, q

    def unlisten(self, listener_id: int):
        del self.listeners[listener_id]

    def announce_task_event(self, event: str, task_path: List[int], task: TaskAbc):
        data_to_send = {
            'task_path': task_path,
            'task_message': asdict(task.to_task_message())
        }
        to_send = format_sse(event, json.dumps(data_to_send))
        self.announce(to_send)

    def announce_data(self, event: str, data: str):
        to_send = format_sse(event, data)
        self.announce(to_send)

    def announce(self, event_and_data: str):
        with self._lock:
            logging.info(f'announcing {event_and_data}')
            for q in self.listeners.values():
                q.put_nowait(event_and_data)


def format_sse(event: str, data: str) -> str:
    to_ret = f'event: {event}\ndata: {data}\n\n'
    return to_ret
