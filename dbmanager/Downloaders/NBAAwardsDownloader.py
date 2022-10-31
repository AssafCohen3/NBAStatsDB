import json

from dbmanager.Downloaders.DownloaderAbs import DownloaderAbs
from dbmanager.RequestHandlers.Sessions import stats_session
from dbmanager.constants import PLAYER_AWARDS_ENDPOINT


class NBAAwardsDownloader(DownloaderAbs):
    def __init__(self, player_id):
        self.player_id = player_id

    async def download(self):
        to_send = PLAYER_AWARDS_ENDPOINT % self.player_id
        r = await stats_session.async_get(to_send)
        return json.loads(r.text)
