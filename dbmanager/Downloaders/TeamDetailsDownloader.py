from dbmanager.Downloaders.DownloaderAbs import DownloaderAbs
from dbmanager.RequestHandlers.StatsAsyncRequestHandler import stats_session
from dbmanager.constants import TEAM_DETAILS_ENDPOINT, STATS_HEADERS


class TeamDetailsDownloader(DownloaderAbs):
    def __init__(self, team_id: int):
        self.team_id: int = team_id

    def download(self):
        to_send = TEAM_DETAILS_ENDPOINT % self.team_id
        return stats_session.get(to_send, headers=STATS_HEADERS).json()
