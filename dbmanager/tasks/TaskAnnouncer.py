import itertools
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import asdict
from queue import Queue
from typing import Dict, Tuple

from dbmanager.tasks.TaskMessage import TaskMessage


class AnnouncerAbc(ABC):
    @abstractmethod
    def announce(self, event: str, msg: TaskMessage):
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

    def announce(self, event: str, msg: TaskMessage):
        to_send = format_sse(event, msg)
        logging.info(f'announcing {to_send}')
        for q in self.listeners.values():
            q.put_nowait(to_send)


def format_sse(event: str, msg: TaskMessage) -> str:
    to_ret = f'event: {event}\ndata: {json.dumps(asdict(msg))}\n\n'
    return to_ret
