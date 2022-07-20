import json

from dbmanager.Handlers.HandlerAbs import HandlerAbs
from dbmanager.MainRequestsSession import requests_session as requests
from dbmanager.constants import *


class PlayersHandler(HandlerAbs):
    def __init__(self, season):
        self.season = season

    def get_filename(self):
        return PLAYERS_INDEX_FILE_TEMPLATE % self.season

    def load_file(self, f):
        return json.load(f)

    def downloader(self):
        to_send = PLAYERS_INDEX_ENDPOINT % f'{self.season}-{str(self.season + 1)[2:]}'
        return requests.get(to_send, headers=STATS_HEADERS).json()

    def to_cache(self, data):
        return False

    def cache(self, data, f):
        json.dump(data, f)
