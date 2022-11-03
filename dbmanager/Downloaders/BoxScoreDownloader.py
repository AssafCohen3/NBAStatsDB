import datetime
import json
from typing import Optional
from dbmanager.Downloaders.DownloaderAbs import DownloaderAbs
from dbmanager.RequestHandlers.Sessions import stats_session
from dbmanager.DataTypes.SeasonType import SeasonType
from dbmanager.constants import BOXSCORES_ENDPOINT


class BoxScoreDownloader(DownloaderAbs):
    def __init__(self, date_from: Optional[datetime.date], date_until: Optional[datetime.date],
                 season_type: SeasonType, box_score_type: str):
        self.date_from = date_from
        self.date_until = date_until
        self.season_type = season_type
        self.box_score_type = box_score_type

    async def download(self):
        to_send = BOXSCORES_ENDPOINT % (self.date_from.isoformat() if self.date_from else '',
                                        self.date_until.isoformat() if self.date_until else '',
                                        self.box_score_type,
                                        self.season_type.api_name)
        r = await stats_session.async_get(to_send)
        to_ret = json.loads(r.content)
        return to_ret
