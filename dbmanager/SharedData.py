import json
from abc import ABC, abstractmethod
from threading import Lock
import requests
from dbmanager.constants import DATA_PROD_TODAY_FILE


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


class TodayConfig(SharedDataResourceAbc):
    def _fetch_data(self):
        today_resp = requests.get(DATA_PROD_TODAY_FILE)
        return json.loads(today_resp.text)

    def get_current_season(self):
        return self.get_data()['seasonScheduleYear']


today_config = TodayConfig()
