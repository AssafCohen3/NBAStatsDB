import json
from dbmanager.Downloaders.DownloaderAbs import DownloaderAbs
from dbmanager.RequestHandlers.StatsAsyncRequestHandler import stats_session
from dbmanager.constants import PLAYERS_INDEX_ENDPOINT, STATS_HEADERS


class NBAPlayersDownloader(DownloaderAbs):
    def __init__(self, season):
        self.season = season

    def download(self):
        to_send = PLAYERS_INDEX_ENDPOINT % f'{self.season}-{str(self.season + 1)[2:]}'
        to_ret = stats_session.get(to_send, headers=STATS_HEADERS)
        return json.loads(to_ret.text)
