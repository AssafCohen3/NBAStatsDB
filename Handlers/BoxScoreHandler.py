import json

from Handlers.HandlerAbs import HandlerAbs
from MainRequestsSession import requests_session as requests
from constants import *


class BoxScoreHandler(HandlerAbs):
    def __init__(self, date_from, season_type_index, box_score_type):
        self.date_from = date_from
        self.season_type_index = season_type_index
        self.box_score_type = box_score_type

    def get_filename(self):
        if self.date_from:
            return BOXSCORE_FILE_TEMPLATE % (self.date_from, self.season_type_index, self.box_score_type)
        return BOXSCORE_FILE_TEMPLATE % ("first", self.season_type_index, self.box_score_type)

    def load_file(self, f):
        return json.load(f)

    def downloader(self):
        to_send = BOXSCORES_ENDPOINT % (self.date_from, self.box_score_type, SEASON_TYPES[self.season_type_index]['name'])
        r = requests.get(to_send, headers=STATS_HEADERS)
        to_ret = json.loads(r.content)
        return to_ret

    def to_cache(self, data):
        data = data["resultSets"][0]
        results = data["rowSet"]
        return len(results) >= API_COUNT_THRESHOLD

    def cache(self, data, f):
        json.dump(data, f)
