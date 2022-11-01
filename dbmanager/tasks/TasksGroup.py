import itertools
from typing import List, Union, Dict, Optional
from dbmanager.AppI18n import TranslatableField
from dbmanager.Errors import TaskPathNotExistError, ExceptionMessage
from dbmanager.tasks.RetryManager import RetryConfig
from dbmanager.tasks.TaskAbc import TaskAbc
from dbmanager.tasks.TaskAnnouncer import AnnouncerAbc
from dbmanager.tasks.TaskMessage import TaskMessage
from dbmanager.utils import iterate_with_next


class TasksGroup(TaskAbc, AnnouncerAbc):
    def __init__(self, group_id: str, group_translatable_name: TranslatableField, actions: List[TaskAbc]):
        super().__init__()
        self.tasks_to_run: List[TaskAbc] = actions
        self.tasks_dict: Dict[int, TaskAbc] = {}
        self.group_id = group_id
        self.group_translatable_name = group_translatable_name
        self.current_task: Optional[TaskAbc] = self.tasks_to_run[0] if self.tasks_to_run else None

    def get_subtasks_messages(self) -> List[TaskMessage]:
        to_ret = []
        for sub_task in self.tasks_to_run:
            if not sub_task.is_dismissed():
                to_ret.append(sub_task.to_task_message())
        return to_ret

    def to_task_message(self) -> TaskMessage:
        return TaskMessage(
            task_id=self.get_task_id(),
            action_id=self.group_id,
            action_title=self.group_translatable_name.get_value(),
            resource_id=None,
            resource_name=None,
            mini_title=self.get_current_subtask_text(),
            completed=self.completed_subtasks(),
            to_finish=self.subtasks_count(),
            status=self.get_delegated_current_status(),
            subtasks_messages=self.get_subtasks_messages(),
            exception=self.get_delegated__exception_message(),
            retry_status=self.current_task.get_retry_status() if self.current_task else self.get_retry_status()
        )

    def get_delegated__exception_message(self) -> ExceptionMessage:
        if self.is_critical_error():
            return self.get_task_error_message()
        return self.current_task.get_task_error_message() if self.current_task else self.get_task_error_message()

    def get_delegated_current_status(self) -> str:
        if self.is_critical_error():
            return self.current_status()
        return self.current_task.current_status() if self.current_task else self.current_status()

    async def action(self):
        for task, next_task in iterate_with_next(self.tasks_to_run):
            task.init_task_data()
            await task
            task.after_execution_finished()
            self.current_task = next_task
            await self.finish_subtask()

    def subtasks_count(self) -> Union[int, None]:
        return len(self.tasks_to_run)

    def get_current_subtask_text_abs(self) -> str:
        return self.current_task.get_task_title() if self.current_task else ''

    def init_task(self, counter: itertools.count, announcer: AnnouncerAbc, retry_config: RetryConfig):
        super().init_task(counter, announcer, retry_config)
        for action in self.tasks_to_run:
            action.init_task(counter, self, retry_config)
            self.tasks_dict[action.get_task_id()] = action

    def get_sub_task_abs(self, task_path: List[int]) -> 'TaskAbc':
        if task_path[0] not in self.tasks_dict:
            raise TaskPathNotExistError(self.get_task_id(), task_path)
        return self.tasks_dict[task_path[0]].get_sub_task(task_path[1:])

    def announce_task_event(self, event: str, task_path: List[int], task: TaskAbc):
        try:
            if self.announcer:
                self.announcer.announce_task_event(event, [self.get_task_id()], self)
        except Exception as e:
            self.raise_critical_error(e)

    def get_task_title(self) -> str:
        return self.group_translatable_name.get_value()

    def after_execution_finished(self):
        return

    def announce_data(self, event: str, data: str):
        try:
            if self.announcer:
                self.announcer.announce_data(event, data)
        except Exception as e:
            self.raise_critical_error(e)

    def init_task_data_abs(self) -> bool:
        to_refresh = self.current_task.init_task_data() if self.current_task else False
        return to_refresh

    def get_sub_tasks(self) -> List['TaskAbc']:
        return self.tasks_to_run

    def pause(self):
        if self.current_task:
            self.current_task.pause()

    def resume(self):
        if self.current_task:
            self.current_task.resume()
