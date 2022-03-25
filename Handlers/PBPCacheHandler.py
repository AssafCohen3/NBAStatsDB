import json
import requests
from constants import *


class PBPCacheHandler:
    def __init__(self, game_id):
        self.game_id = game_id

    def get_filename(self):
        return PBP_FILE_TEMPLATE % self.game_id

    def load_file(self, f):
        return json.load(f)

    def downloader(self):
        to_send = PBP_ENDPOINT % self.game_id
        return requests.get(to_send, headers=STATS_HEADERS).json()

    def to_cache(self, data):
        return True

    def cache(self, data, f):
        json.dump(data, f)
