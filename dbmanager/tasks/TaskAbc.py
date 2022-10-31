import asyncio
import itertools
import logging
from abc import ABC, abstractmethod
from asyncio import TimerHandle
from typing import Optional, Union, List
import requests.exceptions
from dbmanager.AppI18n import gettext
from dbmanager.Errors import TaskPathNotExistError, TaskDismissedError, TaskAlreadyFinishedError, TaskNotInitiatedError, \
    TaskNotFinishedError
from dbmanager.tasks.RetryManager import RetryManager, RetryConfig, AttemptContextManager, RetryStatus
from dbmanager.tasks.TaskAnnouncer import AnnouncerAbc
from dbmanager.tasks.TaskMessage import TaskMessage, ExceptionMessage


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
    def __init__(self):
        self._task_id: int = -1
        self.pre_active = True
        self.active: Optional[ThreadSafeEvent] = None
        self.cancelled = False
        self._error_msg: Optional[Exception] = None
        self.completed_subtasks_count = 0
        self.finished = False
        self.started = False
        self.announcer: Optional[AnnouncerAbc] = None
        self.subtask_finished = False
        self.dismissed = False
        self._data_initiated = False
        self.retry_manager: Optional[RetryManager] = None
        self.resume_timer_handler: Optional[TimerHandle] = None

    def init_task(self, counter: itertools.count, announcer: AnnouncerAbc, retry_config: RetryConfig):
        self.set_task_id(next(counter))
        self.set_announcer(announcer)
        self.retry_manager = RetryManager(retry_config, self.after_attempt_fail, self.after_retry_fail, True)

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

    def cancel_task_silent(self):
        if self.is_finished():
            raise TaskAlreadyFinishedError(self.get_task_id())
        for sub_task in self.get_sub_tasks():
            sub_task.cancel_task_silent()
        self.cancelled = True
        self.reset_resume_timer()
        if self.active is None:
            self.pre_active = True
        else:
            self.active.set()

    def cancel_task(self):
        self.cancel_task_silent()
        if self.active is None:
            self.announce_task_update('cancel')

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
        self.reset_resume_timer()
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

            # if actually paused and woke up because of resume(and not because cancelling)
            if paused and not self.cancelled:
                self.announce_task_update('resume')

            # if cancelled finish
            if self.cancelled:
                self.announce_task_update('cancel')
                return None

            # if crashed not in action
            if self.is_error():
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
                self.raise_error(gen_err)
                self.announce_task_update('error')
                return None
            else:
                send = iter_send
            # sub finish
            # if already started and finished with finish_subtask()
            if self.started and self.subtask_finished:
                self.announce_task_update('sub-finish')
            try:
                message = yield signal
            except BaseException as err:
                send, message = iter_throw, err

    def current_status(self) -> str:
        if self.is_error():
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
        if self.is_error():
            return repr(self.get_current_error())
        if self.cancelled:
            return gettext('common.cancelled')
        if self.is_finished():
            return gettext('common.finished')
        if self.is_recover_mode():
            if isinstance(self.get_last_failed_attempt().attempt_exception, requests.exceptions.RequestException):
                return gettext('common.received_recoverable_connection_error')
            else:
                return gettext('common.received_recoverable_arbitrary_error')
        return self.get_current_subtask_text_abs()

    @abstractmethod
    def get_current_subtask_text_abs(self) -> str:
        """
        get subtasks completed
        """

    def is_finished(self) -> bool:
        return self.cancelled or self.is_error() or self.finished

    def is_dismissed(self) -> bool:
        return self.dismissed

    def is_active(self) -> bool:
        return not self.is_finished() and ((self.started and self.active.is_set()) or (not self.started and self.pre_active))

    def is_error(self):
        return self.get_current_error() is not None

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
            self.raise_error(e)

    def call_annnouncer_with_data(self, event: str, data: str):
        try:
            if self.announcer:
                self.announcer.announce_data(event, data)
        except Exception as e:
            self.raise_error(e)

    async def finish_subtask(self):
        self.completed_subtasks_count += 1
        self.subtask_finished = True
        await asyncio.sleep(0)

    async def refresh_status(self):
        self.subtask_finished = True
        await asyncio.sleep(0)

    @abstractmethod
    def get_sub_tasks(self) -> List['TaskAbc']:
        pass

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

    def raise_error(self, e: Exception):
        self._error_msg = e

    def get_current_error(self):
        return self._error_msg

    def is_recover_mode(self) -> bool:
        return self.started and self.retry_manager and self.retry_manager.get_last_recoverable_failed_attempt() is not None and not self.is_active()

    def get_last_failed_attempt(self) -> Optional[AttemptContextManager]:
        return self.retry_manager.get_last_recoverable_failed_attempt() if self.retry_manager else None

    async def after_attempt_fail(self, attempt: AttemptContextManager, seconds_to_wait: float):
        logging.info(f'task {self.get_task_id()}: attempt number {attempt.attempt_number} of retry number {attempt.retry_number} failed. sleeping for {seconds_to_wait} seconds')
        await asyncio.sleep(seconds_to_wait)

    async def after_retry_fail(self, attempt: AttemptContextManager, seconds_to_wait: float):
        logging.info(f'task {self.get_task_id()}: attempt number {attempt.attempt_number}(last attempt) of retry number {attempt.retry_number} failed. '
                     f'sleeping for {seconds_to_wait} seconds')
        self.pause()
        if seconds_to_wait > 0:
            self.resume_timer_handler = asyncio.get_event_loop().call_later(seconds_to_wait, self.resume)
        await asyncio.sleep(0)

    def reset_resume_timer(self):
        if self.resume_timer_handler:
            self.resume_timer_handler.cancel()
            self.resume_timer_handler = None

    def get_task_error_message(self) -> Optional[ExceptionMessage]:
        if self.is_error():
            return ExceptionMessage.build_from_exception(self.get_current_error())
        if self.is_recover_mode():
            return ExceptionMessage.build_from_exception(self.get_last_failed_attempt().attempt_exception)
        return None

    def get_retry_status(self) -> Optional[RetryStatus]:
        if self.is_recover_mode():
            return RetryStatus.build_from_attempt(self.get_last_failed_attempt())
        return None
