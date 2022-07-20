import json

from dbmanager.Handlers.HandlerAbs import HandlerAbs
from dbmanager.MainRequestsSession import requests_session as requests
from dbmanager.constants import *


class TeamRosterHandler(HandlerAbs):
    def __init__(self, season, team_id):
        self.season = season
        self.team_id = team_id

    def get_filename(self):
        return TEAM_ROSTER_FILE_TEMPLATE % (self.team_id, self.season)

    def load_file(self, f):
        return json.load(f)

    def downloader(self):
        to_send = TEAM_ROSTER_ENDPOINT % (f'{self.season}-{str(self.season + 1)[2:]}', self.team_id)
        return requests.get(to_send, headers=STATS_HEADERS).json()

    def to_cache(self, data):
        return True

    def cache(self, data, f):
        json.dump(data, f)
