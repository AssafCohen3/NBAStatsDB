from functools import wraps
from itertools import tee, islice, chain
from typing import Iterable, TypeVar, Tuple, Optional, Callable
from flask import request
from typeguard import typechecked


R = TypeVar('R')


def iterate_with_next(some_iterable: Iterable[R], last_val=None) -> Iterable[Tuple[R, Optional[R]]]:
    items, nexts = tee(some_iterable, 2)
    nexts = chain(islice(nexts, 1, None), [last_val])
    return zip(items, nexts)


def flask_request_validation(method: Callable):
    checked_method = typechecked(method)

    @wraps(method)
    def _with_check_params(*args, **kwargs):
        request_json = request.get_json(silent=True)
        json_params = request_json if request_json else {}
        return checked_method(*args, **kwargs, **json_params)
    return _with_check_params
