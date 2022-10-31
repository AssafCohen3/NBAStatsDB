import datetime
import json

import requests

from dbmanager.SharedData.SharedDataResourceAbs import SharedDataResourceAbc
from dbmanager.constants import DATA_PROD_TODAY_FILE


class TodayConfig(SharedDataResourceAbc[dict]):
    def _fetch_data(self):
        today_resp = requests.get(DATA_PROD_TODAY_FILE)
        if today_resp.status_code == 404:
            return {}
        return json.loads(today_resp.text)

    def get_current_season(self):
        # TODO the fuck why this is 404
        if 'seasonScheduleYear' not in self.get_data():
            today = datetime.date.today()
            if today.month < 10:
                return today.year - 1
            return today.year
        else:
            return self.get_data()['seasonScheduleYear']


today_config = TodayConfig()
