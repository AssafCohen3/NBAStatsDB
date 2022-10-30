import asyncio
import itertools
import logging
from abc import ABC, abstractmethod
from typing import Optional, Union, List
from dbmanager.AppI18n import gettext
from dbmanager.Errors import TaskPathNotExistError, TaskDismissedError, TaskAlreadyFinishedError, TaskNotInitiatedError, \
    TaskNotFinishedError
from dbmanager.tasks.TaskAnnouncer import AnnouncerAbc
from dbmanager.tasks.TaskMessage import TaskMessage
from dbmanager.utils import RecoverableError


class ThreadSafeEvent(asyncio.Event):
    def __init__(self):
        super().__init__()
        if hasattr(self, '_loop') and getattr(self, '_loop') is None:
            self._loop = asyncio.get_event_loop()

    def set(self):
        self._loop.call_soon_threadsafe(super().set)

    def clear(self):
        self._loop.call_soon_threadsafe(super().clear)


class TaskAbc(ABC):
    def __init__(self, max_retries_number: int = 1, seconds_to_sleep_between_retries: float = 1.0):
        self._task_id: int = -1
        self.pre_active = True
        self.active: Optional[ThreadSafeEvent] = None
        self.cancelled = False
        self.error_msg: Optional[Exception] = None
        self.completed_subtasks_count = 0
        self.finished = False
        self.started = False
        self.announcer: Optional[AnnouncerAbc] = None
        self.subtask_finished = False
        self.dismissed = False
        self._data_initiated = False
        self.recoverable_error: Optional[RecoverableError] = None
        self.max_retries_number = max_retries_number
        self.seconds_to_sleep_between_retries = seconds_to_sleep_between_retries

    def init_task(self, counter: itertools.count, announcer: AnnouncerAbc):
        self.set_task_id(next(counter))
        self.set_announcer(announcer)

    def init_task_data(self) -> bool:
        if self._data_initiated:
            return False
        to_refresh = self.init_task_data_abs()
        self._data_initiated = True
        return to_refresh

    @abstractmethod
    def init_task_data_abs(self) -> bool:
        pass

    def get_task_id(self) -> int:
        return self._task_id

    def set_task_id(self, task_id: int):
        self._task_id = task_id

    def set_announcer(self, announcer: AnnouncerAbc):
        self.announcer = announcer

    def cancel_task(self):
        if self.is_finished():
            raise TaskAlreadyFinishedError(self.get_task_id())
        self.cancelled = True
        if self.active is None:
            self.pre_active = True
            self.announce_task_update('cancel')
        else:
            self.active.set()

    def pause(self):
        if self.is_finished():
            raise TaskAlreadyFinishedError(self.get_task_id())
        if self.active is None:
            self.pre_active = False
            self.announce_task_update('paused')
        else:
            self.active.clear()

    def resume(self):
        if self.is_finished():
            raise TaskAlreadyFinishedError(self.get_task_id())
        if self.active is None:
            self.pre_active = True
            self.announce_task_update('resume')
        else:
            self.active.set()

    def dismiss_task(self):
        if not self.is_finished():
            raise TaskNotFinishedError(self.get_task_id())
        self.dismissed = True

    def __await__(self):
        # we want to run run_action
        target_iter = self.run_action().__await__()
        iter_send, iter_throw = target_iter.send, target_iter.throw
        send, message = iter_send, None
        # This "while" emulates yield from.
        while True:
            # check if paused. if yes wait for resume
            paused = False
            try:
                while self.started and self.active is not None and not self.active.is_set():
                    if not paused:
                        self.announce_task_update('paused')
                    paused = True
                    yield from self.active.wait().__await__()
            except BaseException as err:
                send, message = iter_throw, err

            if self.is_dismissed():
                return None

            # reset the recoverable error. if the user tried to resume it will be updated even if the resume wasnt a success
            self.recoverable_error = None

            # if actually paused and woke up because of resume(and not because cancelling)
            if paused and not self.cancelled:
                self.announce_task_update('resume')

            # if cancelled finish
            if self.cancelled:
                self.announce_task_update('cancel')
                return None

            # if crashed not in action
            if self.error_msg:
                self.announce_task_update('error')
                return None

            # continue with our regular program
            # clear the subtask finished flag
            # after the execution the flag will be up only if the execution finished with self.finish_subtask()
            self.subtask_finished = False
            try:
                signal = send(message)
            except StopIteration as err:
                # finished successfully
                self.finished = True
                self.announce_task_update('finish')
                return err.value
            except Exception as gen_err:
                # error
                self.error_msg = gen_err
                self.announce_task_update('error')
                return None
            else:
                send = iter_send
            # sub finish
            # if already started and finished with finish_subtask()
            if self.started and self.subtask_finished:
                self.announce_task_update('sub-finish')
            elif self.started and self.recoverable_error:
                self.pause()
            try:
                message = yield signal
            except BaseException as err:
                send, message = iter_throw, err

    def current_status(self) -> str:
        if self.error_msg:
            return 'error'
        if self.cancelled:
            return 'cancelled'
        if self.is_finished():
            return 'finished'
        if self.is_active():
            return 'active'
        return 'paused'

    async def run_action(self):
        if self._task_id < 0:
            raise TaskNotInitiatedError()
        self.active = ThreadSafeEvent()
        if self.pre_active:
            self.active.set()
        await asyncio.sleep(0)
        self.announce_task_update('start')
        self.started = True
        # if pre paused
        await asyncio.sleep(0)
        if self.init_task_data():
            await self.refresh_status()
        await self.action()

    @abstractmethod
    async def action(self):
        """
        the action to run
        """

    @abstractmethod
    def subtasks_count(self) -> Union[int, None]:
        """
        get subtasks count
        None means not known
        """

    def completed_subtasks(self):
        return self.completed_subtasks_count

    def get_current_subtask_text(self) -> str:
        if self.error_msg:
            return repr(self.error_msg)
        if self.cancelled:
            return gettext('common.cancelled')
        if self.is_finished():
            return gettext('common.finished')
        if self.recoverable_error:
            return 'Connection error. you can try to resume'
        return self.get_current_subtask_text_abs()

    @abstractmethod
    def get_current_subtask_text_abs(self) -> str:
        """
        get subtasks completed
        """

    def is_finished(self) -> bool:
        return self.cancelled or self.error_msg or self.finished

    def is_dismissed(self) -> bool:
        return self.dismissed

    def is_active(self) -> bool:
        return not self.is_finished() and ((self.started and self.active.is_set()) or (not self.started and self.pre_active))

    @abstractmethod
    def to_task_message(self) -> TaskMessage:
        pass

    @abstractmethod
    def get_task_title(self) -> str:
        pass

    @abstractmethod
    def after_execution_finished(self):
        pass

    def announce_task_update(self, event_type: str):
        try:
            if self.announcer:
                self.announcer.announce_task_event(f'task-update-{event_type}', [self.get_task_id()], self)
        except Exception as e:
            self.error_msg = e

    def call_annnouncer_with_data(self, event: str, data: str):
        try:
            if self.announcer:
                self.announcer.announce_data(event, data)
        except Exception as e:
            self.error_msg = e

    async def finish_subtask(self):
        self.completed_subtasks_count += 1
        self.subtask_finished = True
        await asyncio.sleep(0)

    async def refresh_status(self):
        self.subtask_finished = True
        await asyncio.sleep(0)

    def get_sub_task(self, task_path: List[int]) -> 'TaskAbc':
        if len(task_path) == 0:
            to_ret = self
        else:
            to_ret = self.get_sub_task_abs(task_path)
        if to_ret.is_dismissed():
            raise TaskDismissedError(to_ret.get_task_id())
        return to_ret

    def get_sub_task_abs(self, task_path: List[int]) -> 'TaskAbc':
        raise TaskPathNotExistError(self.get_task_id(), task_path)

    async def raise_recoverable_error(self, recoverable_error: RecoverableError):
        self.recoverable_error = recoverable_error
        await asyncio.sleep(0)

    def get_max_retries_number(self) -> int:
        return self.max_retries_number

    def on_retry(self, attempt_number, exception: RecoverableError):
        logging.info(f'task {self.get_task_id()}: received exception {exception} in attempt number {attempt_number}.')

    def get_seconds_tp_sleep_between_retries(self) -> float:
        return self.seconds_to_sleep_between_retries
