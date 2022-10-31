import json

from dbmanager.Downloaders.DownloaderAbs import DownloaderAbs
from dbmanager.RequestHandlers.Sessions import stats_session
from dbmanager.constants import TEAM_DETAILS_ENDPOINT


class TeamDetailsDownloader(DownloaderAbs):
    def __init__(self, team_id: int):
        self.team_id: int = team_id

    async def download(self):
        to_send = TEAM_DETAILS_ENDPOINT % self.team_id
        to_ret = await stats_session.async_get(to_send)
        return json.loads(to_ret.text)
