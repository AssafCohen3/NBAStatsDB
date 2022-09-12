from abc import ABC, abstractmethod
from threading import Lock


class SharedDataResourceAbc(ABC):

    def __init__(self):
        self._lock = Lock()
        self.cached_data = None

    def get_data(self):
        if not self.cached_data:
            with self._lock:
                self.cached_data = self._fetch_data()
        return self.cached_data

    @abstractmethod
    def _fetch_data(self):
        pass
