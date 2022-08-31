import asyncio
from abc import ABC, abstractmethod
from typing import Optional, Type, Union, Dict, Any

from sqlalchemy.orm import Session

from dbmanager.AppI18n import gettext
from dbmanager.Resources.ActionSpecifications.ActionSpecificationAbc import ActionSpecificationAbc


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
    def __init__(self, session: Session, **kwargs):
        self._task_id: int = -1
        self.pre_active = True
        self.active: Optional[ThreadSafeEvent] = None
        self.cancelled = False
        self.session: Session = session

    @classmethod
    @abstractmethod
    def get_action_spec(cls) -> Type[ActionSpecificationAbc]:
        """
        get action specification
        """

    @classmethod
    def create_action_from_params(cls, session: Session, params: Dict[str, Any]) -> 'ActionAbc':
        return cls(session, **params)

    def get_task_id(self) -> int:
        return self._task_id

    def set_task_id(self, task_id: int):
        self._task_id = task_id

    def cancel_task(self):
        if self.is_finished():
            return
        self.cancelled = True
        if self.active:
            self.active.set()
        self.pre_active = True

    def __await__(self):
        target_iter = self.run_action().__await__()
        iter_send, iter_throw = target_iter.send, target_iter.throw
        send, message = iter_send, None
        # This "while" emulates yield from.
        while True:
            # wait for can_run before resuming execution of self._target
            try:
                while self.active is not None and not self.active.is_set():
                    yield from self.active.wait().__await__()
            except BaseException as err:
                send, message = iter_throw, err

            if self.cancelled:
                return None
            # continue with our regular program
            try:
                signal = send(message)
            except StopIteration as err:
                return err.value
            else:
                send = iter_send
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
        return self.cancelled

    def is_active(self) -> bool:
        return not self.cancelled and not self.is_finished() and ((self.active is not None and self.active.is_set()) or (self.active is None and self.pre_active))
