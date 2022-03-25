import json
import requests
from constants import *


class TeamDetailsHandler:
    def __init__(self, team_id):
        self.team_id = team_id

    def get_filename(self):
        return TEAM_DETAILS_FILE_TEMPLATE % self.team_id

    def load_file(self, f):
        return json.load(f)

    def downloader(self):
        to_send = TEAM_DETAILS_ENDPOINT % self.team_id
        return requests.get(to_send, headers=STATS_HEADERS).json()

    def to_cache(self, data):
        return True

    def cache(self, data, f):
        json.dump(data, f)
