import json
import re

import requests
from bs4 import BeautifulSoup
import pandas as pd
from constants import *


class BRPlayoffsSummaryHandler:
    def __init__(self, season, season_link):
        self.season = season
        self.season_link = season_link

    def get_filename(self):
        return PLAYOFF_PAGE_FILE_TEMPLATE % self.season

    def load_file(self, f):
        return json.load(f)

    def downloader(self):
        season_part = re.findall(r'/([^/]+?)$', self.season_link)[0]
        to_send = 'https://www.basketball-reference.com/playoffs/' + season_part
        r = requests.get(to_send)
        soup = BeautifulSoup(r.content, 'html.parser')
        playoff_series = soup.select('table#all_playoffs tbody > tr')
        to_ret = []
        level = 0
        for serie in playoff_series:
            if serie.has_attr('class'):
                if 'thead' in serie['class']:
                    level += 1
                continue
            level_description = serie.select('span strong')
            if not level_description:
                continue
            level_description = level_description[0].getText()
            summary_col = serie.select('td')[1]
            teams_tags = summary_col.select('a')
            winner_abbr = BR_ABBR_TO_NBA_ABBR[re.findall(r'/teams/(.+?)/', teams_tags[0]['href'])[0]]
            loser_abbr = BR_ABBR_TO_NBA_ABBR[re.findall(r'/teams/(.+?)/', teams_tags[1]['href'])[0]]
            results = summary_col.contents[-1].getText().strip().replace('(', '').replace(')', '').split('-')
            winner_wins = int(results[0])
            loser_wins = int(results[1])
            team_a_abbr, team_a_wins, team_b_abbr, team_b_wins = (winner_abbr, winner_wins, loser_abbr, loser_wins) if winner_abbr < loser_abbr else (loser_abbr, loser_wins, winner_abbr, winner_wins)
            to_ret.append([self.season, team_a_abbr, team_b_abbr, team_a_wins, team_b_wins, winner_abbr, loser_abbr, level + 1, level_description])
        return to_ret

    def to_cache(self, data):
        return True

    def cache(self, data, f):
        json.dump(data, f)
