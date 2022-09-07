import asyncio
from abc import ABC, abstractmethod
from typing import Optional, Type, Union, Dict, Any

from sqlalchemy.orm import scoped_session

from dbmanager.AppI18n import gettext
from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc
from dbmanager.tasks.TaskAnnouncer import AnnouncerAbc
from dbmanager.tasks.TaskMessage import TaskMessage


class ThreadSafeEvent(asyncio.Event):
    def __init__(self):
        super().__init__()
        if hasattr(self, '_loop') and getattr(self, '_loop') is None:
            self._loop = asyncio.get_event_loop()

    def set(self):
        self._loop.call_soon_threadsafe(super().set)

    def clear(self):
        self._loop.call_soon_threadsafe(super().clear)


class ActionAbc(ABC):
    def __init__(self, session: scoped_session, **kwargs):
        self._task_id: int = -1
        self.pre_active = True
        self.active: Optional[ThreadSafeEvent] = None
        self.cancelled = False
        self.error_msg: Optional[Exception] = None
        self.finished = False
        self.started = False
        self.announcer: Optional[AnnouncerAbc] = None
        self.subtask_finished = False
        self.session: scoped_session = session

    @classmethod
    @abstractmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        """
        get action specification
        """

    @classmethod
    def get_action_id(cls) -> str:
        return cls.get_action_spec().get_action_id()

    @classmethod
    def create_action_from_params(cls, session: scoped_session, params: Dict[str, Any]) -> 'ActionAbc':
        return cls(session, **params)

    def get_task_id(self) -> int:
        return self._task_id

    def set_task_id(self, task_id: int):
        self._task_id = task_id

    def set_announcer(self, announcer: AnnouncerAbc):
        self.announcer = announcer

    def cancel_task(self):
        if self.is_finished():
            return
        self.cancelled = True
        if self.active:
            self.active.set()
        # TODO why at end
        self.pre_active = True

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
                while self.active is not None and not self.active.is_set():
                    if not paused:
                        self.announce_update('paused')
                    paused = True
                    yield from self.active.wait().__await__()
            except BaseException as err:
                send, message = iter_throw, err
            # if actually paused and woke up because of resume(and not because cancelling)
            if paused and not self.cancelled:
                self.announce_update('resume')

            # if cancelled finish
            if self.cancelled:
                self.announce_update('cancel')
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
                self.announce_update('finish')
                return err.value
            except Exception as gen_err:
                # error
                self.error_msg = gen_err
                self.announce_update('error')
                return None
            else:
                send = iter_send
            # sub finish
            # if already started and finished with finish_subtask()
            if self.started and self.subtask_finished:
                self.announce_update('sub-finish')
            try:
                message = yield signal
            except BaseException as err:
                send, message = iter_throw, err

    def pause(self):
        if self.is_finished():
            return
        if self.active is None:
            self.pre_active = False
        else:
            self.active.clear()

    def resume(self):
        if self.is_finished():
            return
        if self.active is None:
            self.pre_active = True
        else:
            self.active.set()

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
        self.active = ThreadSafeEvent()
        if self.pre_active:
            self.active.set()
        await asyncio.sleep(0)
        self.announce_update('start')
        self.started = True
        await self.action()

    @abstractmethod
    async def action(self):
        """
        the action to run
        """

    # None means not known
    @abstractmethod
    def subtasks_count(self) -> Union[int, None]:
        """
        get subtasks count
        """

    @abstractmethod
    def subtasks_completed(self) -> int:
        """
        get subtasks completed
        """

    def get_current_subtask_text(self) -> str:
        if self.error_msg:
            return str(self.error_msg)
        if self.cancelled:
            return gettext('common.cancelled')
        if self.is_finished():
            return gettext('common.finished')
        return self.get_current_subtask_text_abs()

    @abstractmethod
    def get_current_subtask_text_abs(self) -> str:
        """
        get subtasks completed
        """

    def is_finished(self) -> bool:
        return self.cancelled or self.error_msg or self.finished

    def is_active(self) -> bool:
        return not self.is_finished() and ((self.active is not None and self.active.is_set()) or (self.active is None and self.pre_active))

    def to_task_message(self):
        return TaskMessage(
            self.get_task_id(),
            self.get_action_id(),
            self.get_action_spec().get_action_title(),
            self.get_current_subtask_text(),
            self.subtasks_completed(),
            self.subtasks_count(),
            self.current_status()
        )

    def announce_update(self, event_type: str):
        try:
            if self.announcer:
                self.announcer.announce(f'task-update-{event_type}', self.to_task_message())
        except Exception as e:
            self.error_msg = e

    async def finish_subtask(self):
        self.subtask_finished = True
        await asyncio.sleep(0)
