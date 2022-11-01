import datetime
from functools import wraps
from itertools import tee, islice, chain
from typing import Iterable, TypeVar, Tuple, Optional, Callable

import requests
from flask import request
from typeguard import typechecked
from dbmanager.Errors import RequestTypeError


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


def estimate_season_start_date(season: int) -> datetime.date:
    return datetime.date(year=season, month=10, day=1)


def protocol_retry_request(url: str, *args, **kwargs):
    without_protocol = url.replace('https://', '').replace('http://', '')
    resp = requests.get('https://' + without_protocol, *args, **kwargs)
    if resp.status_code == 200:
        return resp
    return requests.get('http://' + without_protocol, *args, **kwargs)
