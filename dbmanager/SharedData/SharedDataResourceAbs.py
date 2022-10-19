from abc import ABC, abstractmethod
from threading import Lock
from typing import Generic, TypeVar, Optional

D = TypeVar('D')


class SharedDataResourceAbc(ABC, Generic[D]):

    def __init__(self):
        self._lock = Lock()
        self.cached_data: Optional[D] = None

    def get_data(self) -> D:
        if not self.cached_data:
            with self._lock:
                self.cached_data = self._fetch_data()
        return self.cached_data

    @abstractmethod
    def _fetch_data(self) -> D:
        pass
