import json

from dbmanager.Downloaders.DownloaderAbs import DownloaderAbs
from dbmanager.RequestHandlers.StatsAsyncRequestHandler import stats_session
from dbmanager.constants import PLAYER_AWARDS_ENDPOINT, STATS_HEADERS


class NBAAwardsDownloader(DownloaderAbs):
    def __init__(self, player_id):
        self.player_id = player_id

    def download(self):
        to_send = PLAYER_AWARDS_ENDPOINT % self.player_id
        r = stats_session.get(to_send, headers=STATS_HEADERS)
        return json.loads(r.text)
