import json
import requests
from constants import *


class PlayerProfileHandler:
    def __init__(self, player_id):
        self.player_id = player_id

    def get_filename(self):
        return PLAYER_PROFILE_FILE_TEMPLATE % self.player_id

    def load_file(self, f):
        return json.load(f)

    def downloader(self):
        to_send = PLAYER_PROFILE_ENDPOINT % self.player_id
        return requests.get(to_send, headers=STATS_HEADERS).json()

    def to_cache(self, data):
        return True

    def cache(self, data, f):
        json.dump(data, f)
