from dataclasses import dataclass
from typing import Optional


@dataclass
class TaskMessage:
    task_id: int
    action_id: str
    action_title: str
    mini_title: str
    completed: int
    to_finish: Optional[int]
    status: str
