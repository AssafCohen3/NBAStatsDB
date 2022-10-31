import json

from dbmanager.Downloaders.DownloaderAbs import DownloaderAbs
from dbmanager.RequestHandlers.Sessions import stats_session
from dbmanager.constants import PLAYER_PROFILE_ENDPOINT


class PlayerProfileDownloader(DownloaderAbs):
    def __init__(self, player_id: int):
        self.player_id: int = player_id

    async def download(self):
        to_send = PLAYER_PROFILE_ENDPOINT % self.player_id
        to_ret = await stats_session.async_get(to_send)
        return json.loads(to_ret.text)
