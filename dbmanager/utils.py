from functools import wraps
from itertools import tee, islice, chain
from typing import Iterable, TypeVar, Tuple, Optional, List

from flask import request

from dbmanager.Errors import RequiredRequestArgumentMissing, IncorrectRequestArgumentType

R = TypeVar('R')


def iterate_with_next(some_iterable: Iterable[R], last_val=None) -> Iterable[Tuple[R, Optional[R]]]:
    items, nexts = tee(some_iterable, 2)
    nexts = chain(islice(nexts, 1, None), [last_val])
    return zip(items, nexts)


def with_flask_parameters(expected_params: List[Tuple[str, type]]):
    def real_decorator(method):
        @wraps(method)
        def _with_check_params():
            params = request.json
            to_send = []
            for expected_param, expected_param_type in expected_params:
                if expected_param not in params:
                    raise RequiredRequestArgumentMissing(expected_param)
                if not isinstance(params[expected_param], expected_param_type):
                    raise IncorrectRequestArgumentType(expected_param, expected_param_type, params[expected_param])
                to_send.append(params[expected_param])
            return method(*to_send)
        return _with_check_params
    return real_decorator
