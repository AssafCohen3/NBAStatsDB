from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class TaskMessage:
    task_id: int
    action_id: str
    action_title: str
    resource_id: Optional[str]
    resource_name: Optional[str]
    mini_title: str
    completed: int
    to_finish: Optional[int]
    status: str
    subtasks_messages: List['TaskMessage'] = field(default_factory=list)
