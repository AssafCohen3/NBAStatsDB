import json

from dbmanager.Downloaders.DownloaderAbs import DownloaderAbs
from dbmanager.RequestHandlers.Sessions import stats_session
from dbmanager.constants import TEAM_ROSTER_ENDPOINT


class TeamRosterDownloader(DownloaderAbs):
    def __init__(self, season: int, team_id: int):
        self.season: int = season
        self.team_id: int = team_id

    async def download(self):
        to_send = TEAM_ROSTER_ENDPOINT % (f'{self.season}-{str(self.season + 1)[2:]}', self.team_id)
        to_ret = await stats_session.async_get(to_send)
        return json.loads(to_ret.text)
