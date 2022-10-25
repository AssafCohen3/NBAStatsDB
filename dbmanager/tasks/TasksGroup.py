import itertools
from typing import List, Union, Dict
from dbmanager.AppI18n import TranslatableField
from dbmanager.Errors import TaskPathNotExistError
from dbmanager.tasks.TaskAbc import TaskAbc
from dbmanager.tasks.TaskAnnouncer import AnnouncerAbc
from dbmanager.tasks.TaskMessage import TaskMessage


class TasksGroup(TaskAbc, AnnouncerAbc):
    def __init__(self, group_id: str, group_translatable_name: TranslatableField, actions: List[TaskAbc]):
        super().__init__()
        self.tasks_to_run: List[TaskAbc] = actions
        self.tasks_dict: Dict[int, TaskAbc] = {}
        self.group_id = group_id
        self.group_translatable_name = group_translatable_name
        self.current_task_index = 0

    def to_task_message(self) -> TaskMessage:
        return TaskMessage(
            self.get_task_id(),
            self.group_id,
            self.group_translatable_name.get_value(),
            None,
            None,
            self.get_current_subtask_text(),
            self.completed_subtasks(),
            self.subtasks_count(),
            self.current_status(),
            [a.to_task_message() for a in self.tasks_to_run if not a.is_dismissed()]
        )

    async def action(self):
        for i, task in enumerate(self.tasks_to_run):
            await task
            self.current_task_index = i+1
            await self.finish_subtask()

    def subtasks_count(self) -> Union[int, None]:
        return len(self.tasks_to_run)

    def get_current_subtask_text_abs(self) -> str:
        return self.tasks_to_run[self.current_task_index].get_task_title() if self.current_task_index < len(self.tasks_to_run) else ''

    def init_task(self, counter: itertools.count, announcer: AnnouncerAbc):
        super().init_task(counter, announcer)
        for action in self.tasks_to_run:
            action.init_task(counter, self)
            self.tasks_dict[action.get_task_id()] = action

    def get_sub_task_abs(self, task_path: List[int]) -> 'TaskAbc':
        if task_path[0] not in self.tasks_dict:
            raise TaskPathNotExistError(self.get_task_id(), task_path)
        return self.tasks_dict[task_path[0]].get_sub_task(task_path[1:])

    def announce(self, event: str, task_path: List[int], task: TaskAbc):
        self.announcer.announce(event, [self.get_task_id(), *task_path], task)

    def get_task_title(self) -> str:
        return self.group_translatable_name.get_value()
