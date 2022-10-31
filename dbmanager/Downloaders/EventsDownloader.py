import json
from dbmanager.Downloaders.DownloaderAbs import DownloaderAbs
from dbmanager.RequestHandlers.Sessions import stats_session
from dbmanager.constants import PBP_ENDPOINT


class EventsDownloader(DownloaderAbs):
    def __init__(self, game_id):
        self.game_id = game_id

    async def download(self):
        to_send = PBP_ENDPOINT % self.game_id
        resp = await stats_session.async_get(to_send)
        return json.loads(resp.content)
