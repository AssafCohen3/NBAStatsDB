import json

from dbmanager.Downloaders.DownloaderAbs import DownloaderAbs
from dbmanager.RequestHandlers.StatsAsyncRequestHandler import stats_session
from dbmanager.constants import TEAM_ROSTER_ENDPOINT, STATS_HEADERS


class TeamRosterDownloader(DownloaderAbs):
    def __init__(self, season: int, team_id: int):
        self.season: int = season
        self.team_id: int = team_id

    def download(self):
        to_send = TEAM_ROSTER_ENDPOINT % (f'{self.season}-{str(self.season + 1)[2:]}', self.team_id)
        return json.loads(stats_session.get(to_send, headers=STATS_HEADERS).text)
