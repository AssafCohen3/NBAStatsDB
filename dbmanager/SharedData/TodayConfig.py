import json

import requests

from dbmanager.SharedData.SharedDataResourceAbs import SharedDataResourceAbc
from dbmanager.constants import DATA_PROD_TODAY_FILE


class TodayConfig(SharedDataResourceAbc):
    def _fetch_data(self):
        today_resp = requests.get(DATA_PROD_TODAY_FILE)
        return json.loads(today_resp.text)

    def get_current_season(self):
        return self.get_data()['seasonScheduleYear']


today_config = TodayConfig()
