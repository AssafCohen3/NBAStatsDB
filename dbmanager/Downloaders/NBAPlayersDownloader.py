import json
from dbmanager.Downloaders.DownloaderAbs import DownloaderAbs
from dbmanager.RequestHandlers.Sessions import stats_session
from dbmanager.constants import PLAYERS_INDEX_ENDPOINT


class NBAPlayersDownloader(DownloaderAbs):
    def __init__(self, season):
        self.season = season

    async def download(self):
        to_send = PLAYERS_INDEX_ENDPOINT % f'{self.season}-{str(self.season + 1)[2:]}'
        to_ret = await stats_session.async_get(to_send)
        return json.loads(to_ret.text)
