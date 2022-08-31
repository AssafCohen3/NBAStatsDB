import datetime
import json
from typing import Optional

from dbmanager.Downloaders.DownloaderAbs import DownloaderAbs
from dbmanager.MainRequestsSession import requests_session as requests
from dbmanager.SeasonType import SeasonType
from dbmanager.constants import *


class BoxScoreDownloader(DownloaderAbs):
    def __init__(self, date_from: Optional[datetime.date], date_until: Optional[datetime.date],
                 season_type: SeasonType, box_score_type: str):
        self.date_from = date_from
        self.date_until = date_until
        self.season_type = season_type
        self.box_score_type = box_score_type

    def download(self):
        to_send = BOXSCORES_ENDPOINT % (self.date_from.isoformat() if self.date_from else '',
                                        self.date_until.isoformat() if self.date_until else '',
                                        self.box_score_type,
                                        self.season_type.api_name)
        r = requests.get(to_send, headers=STATS_HEADERS)
        to_ret = json.loads(r.content)
        return to_ret
