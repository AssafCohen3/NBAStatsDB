import json

from dbmanager.Downloaders.DownloaderAbs import HandlerAbs
from dbmanager.MainRequestsSession import requests_session as requests
from dbmanager.constants import *


class PlayerAwardsHandler(HandlerAbs):
    def __init__(self, player_id):
        self.player_id = player_id

    def get_filename(self):
        return PLAYER_AWARDS_FILE_TEMPLATE % self.player_id

    def load_file(self, f):
        return json.load(f)

    def downloader(self):
        to_send = PLAYER_AWARDS_ENDPOINT % self.player_id
        r = requests.get(to_send, headers=STATS_HEADERS)
        return r.json()

    def to_cache(self, data):
        return True

    def cache(self, data, f):
        json.dump(data, f)
