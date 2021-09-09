import json
import requests
from boxscores_db import files_template_quick, url_address_date, SEASON_TYPES, STATS_HEADERS, API_COUNT_THRESHOLD


class BoxScoreCacheHandler:
    def __init__(self, date_from, season_type_index, box_score_type):
        self.date_from = date_from
        self.season_type_index = season_type_index
        self.box_score_type = box_score_type

    def get_filename(self):
        if self.date_from:
            return files_template_quick % (self.date_from, self.season_type_index, self.box_score_type)
        return files_template_quick % ("first", self.season_type_index, self.box_score_type)

    def load_file(self, f):
        return json.load(f)

    def downloader(self):
        to_send = url_address_date % (self.date_from, self.box_score_type, SEASON_TYPES[self.season_type_index])
        return requests.get(to_send, headers=STATS_HEADERS).json()

    def to_cache(self, data):
        data = data["resultSets"][0]
        results = data["rowSet"]
        return len(results) >= API_COUNT_THRESHOLD

    def cache(self, data, f):
        json.dump(data, f)