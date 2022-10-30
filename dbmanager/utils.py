from __future__ import annotations

import asyncio
import logging
import typing
from functools import wraps
from itertools import tee, islice, chain
from typing import Iterable, TypeVar, Tuple, Optional, Callable, Type

import requests.exceptions
from flask import request
from typeguard import typechecked

from dbmanager.Errors import RequestTypeError
if typing.TYPE_CHECKING:
    from dbmanager.tasks.TaskAbc import TaskAbc

R = TypeVar('R')


def iterate_with_next(some_iterable: Iterable[R], last_val=None) -> Iterable[Tuple[R, Optional[R]]]:
    items, nexts = tee(some_iterable, 2)
    nexts = chain(islice(nexts, 1, None), [last_val])
    return zip(items, nexts)


def flask_request_validation(method: Callable):
    checked_method = typechecked(method, always=True)

    @wraps(method)
    def _with_check_params(*args, **kwargs):
        request_json = request.get_json(silent=True)
        json_params = request_json if request_json else {}
        try:
            res = checked_method(*args, **kwargs, **json_params)
        except TypeError as e:
            raise RequestTypeError(str(e))
        return res
    return _with_check_params


TR = TypeVar('TR')
RecoverableError: Tuple[Type[Exception], ...] = (requests.exceptions.ConnectionError, requests.exceptions.RetryError, requests.exceptions.ReadTimeout)


def retry_wrapper(method: TR) -> TR:
    @wraps(method)
    async def real_wrapper(self: TaskAbc, *args, **kwargs):
        while True:
            last_error: Optional[RecoverableError] = None
            for i in range(0, self.get_max_retries_number() + 1):
                try:
                    res = await method(self, *args, **kwargs)
                    return res
                except RecoverableError as e:
                    # TODO translate
                    logging.info(f'received connection error. retrying again...\n{e}')
                    last_error = e
                    self.on_retry(i+1, e)
                if i < self.get_max_retries_number():
                    await asyncio.sleep(self.get_seconds_tp_sleep_between_retries())
            await self.raise_recoverable_error(last_error)
    return real_wrapper
