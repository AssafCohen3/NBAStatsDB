import json

from dbmanager.Downloaders.DownloaderAbs import DownloaderAbs
from dbmanager.RequestHandlers.StatsAsyncRequestHandler import stats_session
from dbmanager.constants import PLAYER_PROFILE_ENDPOINT, STATS_HEADERS


class PlayerProfileDownloader(DownloaderAbs):
    def __init__(self, player_id: int):
        self.player_id: int = player_id

    def download(self):
        to_send = PLAYER_PROFILE_ENDPOINT % self.player_id
        return json.loads(stats_session.get(to_send, headers=STATS_HEADERS).text)
