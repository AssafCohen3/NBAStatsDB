from functools import wraps
from threading import Lock
from typing import TypeVar, Generic, Optional, Callable

C = TypeVar('C')


class CachedData(Generic[C]):
    def __init__(self, load_func: Callable[[], C]):
        self._lock = Lock()
        self.data: Optional[C] = None
        self._load_func = load_func

    def get_data(self) -> C:
        with self._lock:
            if self.data is None:
                self.refresh()
        return self.data

    def refresh(self):
        self.data = self._load_func()


CT = TypeVar('CT')
RT = TypeVar('RT')


def refresh_function(get_cached_data: Callable[[CT], CachedData]):
    def real_decorator(method: RT) -> RT:
        @wraps(method)
        def _refresh_after(self: CT, *method_args):
            try:
                method_output = method(self, *method_args)
            except DontRefreshCacheError as e:
                method_output = e.return_val
            else:
                get_cached_data(self).refresh()
            return method_output
        return _refresh_after
    return real_decorator


class DontRefreshCacheError(Exception):
    def __init__(self, return_val):
        self.return_val = return_val

    def get_return_val(self):
        return self.return_val
