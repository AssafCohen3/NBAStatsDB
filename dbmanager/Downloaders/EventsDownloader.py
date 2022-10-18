import json

from dbmanager.Downloaders.DownloaderAbs import DownloaderAbs
from dbmanager.RequestHandlers.StatsAsyncRequestHandler import stats_session
from dbmanager.constants import PBP_ENDPOINT, STATS_HEADERS


class EventsDownloader(DownloaderAbs):
    def __init__(self, game_id):
        self.game_id = game_id

    def download(self):
        to_send = PBP_ENDPOINT % self.game_id
        resp = stats_session.get(to_send, headers=STATS_HEADERS)
        return json.loads(resp.content)
