"""
very inspired by the great library https://github.com/jd/tenacity which is sadly not fully supporting async currently
"""
from __future__ import annotations

import sqlite3
import time
import typing
from dataclasses import dataclass
from functools import wraps
from itertools import count
from typing import Callable, Awaitable, TypeVar, Tuple, Type, Optional, Generator
import requests.exceptions
import sqlalchemy.exc

from dbmanager.Errors import LibraryError

if typing.TYPE_CHECKING:
    from dbmanager.tasks.TaskAbc import TaskAbc


MAX_WAIT_SECONDS = 60 * 30
AfterFailCallbackType = Callable[['AttemptContextManager'], None]
AfterFailAsyncCallbackType = Callable[['AttemptContextManager', float], Awaitable]
ConnectionErrors: Tuple[Type[Exception], ...] = (
    requests.exceptions.ConnectionError,
    requests.exceptions.RetryError,
    requests.exceptions.ReadTimeout,
)
DatabaseErrors: Tuple[Type[Exception], ...] = (
    sqlite3.OperationalError,
    sqlalchemy.exc.OperationalError,
)

RecoverableError: Tuple[Type[Exception], ...] = (
    *ConnectionErrors,
    *DatabaseErrors,
)


@dataclass
class RetryConfig:
    max_attempts_in_retry: int
    seconds_delay_between_attempts: float
    max_retries_number: int
    delay_between_retries_exponential_base: float
    delay_between_retries_multiplyer: float


# waits 1, 2, 4, 8 minutes before retrying
DEFAULT_CONFIG = RetryConfig(
    max_attempts_in_retry=2,
    seconds_delay_between_attempts=5,
    max_retries_number=4,
    delay_between_retries_exponential_base=2,
    delay_between_retries_multiplyer=60
)


class AttemptContextManager:
    def __init__(self, retry_manager: 'RetryManager',
                 retry_number: int, attempt_number: int):
        self.retry_manager: 'RetryManager' = retry_manager
        self.retry_number: int = retry_number
        self.attempt_number: int = attempt_number
        self.attempt_exception: Optional[RecoverableError] = None
        self.failed: bool = False
        self.to_recover: bool = False
        self.fail_timestamp: Optional[float] = None

    def get_config(self) -> RetryConfig:
        return self.retry_manager.retry_config

    def get_wait_after_retry_time(self) -> float:
        try:
            exp = self.get_config().delay_between_retries_exponential_base ** self.retry_number
            result = self.get_config().delay_between_retries_multiplyer * exp
        except OverflowError:
            return MAX_WAIT_SECONDS
        return min(result, MAX_WAIT_SECONDS)

    async def __aenter__(self):
        self.failed = False
        self.to_recover: bool = False

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if isinstance(exc_val, BaseException):
            self.failed = True
        if isinstance(exc_val, RecoverableError):
            self.to_recover = True
            self.fail_timestamp = time.time()
            self.attempt_exception = exc_val
            self.retry_manager.after_fail_always_callback(self)
            if self.attempt_number < self.get_config().max_attempts_in_retry:
                # not last attempt
                await self.retry_manager.after_fail_attempt_callback(self,
                                                                     self.get_config().seconds_delay_between_attempts)
            elif self.retry_number < self.get_config().max_retries_number:
                # last attempt of non last retry
                await self.retry_manager.after_fail_retry_callback(self, self.get_wait_after_retry_time())
            else:
                # last attempt of after last retry
                await self.retry_manager.after_fail_retry_callback(self, -1)
            return True


class RetryManager:
    def __init__(self, retry_config: RetryConfig,
                 after_fail_always_callback: AfterFailCallbackType,
                 after_fail_attempt_callback: AfterFailAsyncCallbackType,
                 after_fail_retry_callback: AfterFailAsyncCallbackType,
                 forever: bool):
        self.retry_config: RetryConfig = retry_config
        self.after_fail_always_callback: AfterFailCallbackType = after_fail_always_callback
        self.after_fail_attempt_callback: AfterFailAsyncCallbackType = after_fail_attempt_callback
        self.after_fail_retry_callback: AfterFailAsyncCallbackType = after_fail_retry_callback
        self.forever: bool = forever
        self.current_attempt: Optional[AttemptContextManager] = None

    def _iter(self) -> Generator[AttemptContextManager, None, None]:
        to_iterate = count(0) if self.forever else range(0, self.retry_config.max_retries_number+1)
        for retry_number in to_iterate:
            for attempt_number in range(1, self.retry_config.max_attempts_in_retry + 1):
                self.current_attempt = AttemptContextManager(self, retry_number, attempt_number)
                yield self.current_attempt
                # not certain to reach here(if the context manager passed fine)

    def get_last_recoverable_failed_attempt(self) -> Optional[AttemptContextManager]:
        return self.current_attempt if self.current_attempt and self.current_attempt.to_recover else None

    def reset(self):
        self.current_attempt = None

    def __enter__(self):
        return self._iter()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.reset()


@dataclass
class RetryStatus:
    retry_number: int
    timestamp: float
    seconds_to_wait: float
    is_last_retry: bool

    @classmethod
    def build_from_attempt(cls, failed_attempt: AttemptContextManager):
        if not failed_attempt.failed:
            raise LibraryError('cant build retry status from a non failed attempt')
        return RetryStatus(failed_attempt.retry_number, failed_attempt.fail_timestamp, failed_attempt.get_wait_after_retry_time(),
                           failed_attempt.retry_number >= failed_attempt.get_config().max_retries_number)


TR = TypeVar('TR')


def retry_wrapper(method: TR) -> TR:
    @wraps(method)
    async def real_wrapper(self: TaskAbc, *args, **kwargs):
        # start new retry session
        with self.retry_manager as attempts_contexts_managers:
            # for every attempt in the retry
            for attempt_context_manager in attempts_contexts_managers:
                # start new attempt context.
                async with attempt_context_manager:
                    res = await method(self, *args, **kwargs)
                    return res
            # if in not forever mode and the retries ended raise the last error
            raise self.retry_manager.get_last_recoverable_failed_attempt().attempt_exception
    return real_wrapper
