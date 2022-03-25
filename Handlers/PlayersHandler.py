import json
import requests
from constants import *


class PlayersHandler:
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
        return True

    def cache(self, data, f):
        json.dump(data, f)
