import json
import re

import requests
from bs4 import BeautifulSoup
import pandas as pd
from constants import *


class BRPlayoffsSummaryHandler:
    def __init__(self, season, season_link, current_teams):
        self.season = season
        self.season_link = season_link
        self.current_teams = current_teams
        self.resp = None

    def get_filename(self):
        return PLAYOFF_PAGE_FILE_TEMPLATE % self.season

    def load_file(self, f):
        return self.from_html(f.read())

    def downloader(self):
        season_part = re.findall(r'/([^/]+?)$', self.season_link)[0]
        to_send = 'https://www.basketball-reference.com/playoffs/' + season_part
        r = requests.get(to_send)
        self.resp = r.text
        return self.from_html(r.text)

    def from_html(self, html_resp):
        soup = BeautifulSoup(html_resp, 'html.parser')
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
            if 'Tiebreaker' in level_description or 'Round Robin' in level_description:
                continue
            summary_col = serie.select('td')[1]
            teams_tags = summary_col.select('a')
            winner_name = teams_tags[0].getText()
            loser_name = teams_tags[1].getText()
            winner_abbr = BR_ABBR_TO_NBA_ABBR[re.findall(r'/teams/(.+?)/', teams_tags[0]['href'])[0]]
            loser_abbr = BR_ABBR_TO_NBA_ABBR[re.findall(r'/teams/(.+?)/', teams_tags[1]['href'])[0]]
            winner_row = [t for t in self.current_teams if (t[2] == winner_name or t[1] == winner_abbr) and t[3] <= self.season <= t[4]]
            loser_row = [t for t in self.current_teams if (t[2] == loser_name or t[1] == loser_abbr) and t[3] <= self.season <= t[4]]
            if len(winner_row) != 1 or len(loser_row) != 1:
                aaaaa = 4
            winner_row = winner_row[0]
            loser_row = loser_row[0]
            winner_id = winner_row[0]
            winner_name = winner_row[2]
            loser_id = loser_row[0]
            loser_name = loser_row[2]
            results = summary_col.contents[-1].getText().strip().replace('(', '').replace(')', '').split('-')
            winner_wins = int(results[0])
            loser_wins = int(results[1])
            team_a_id, team_a_name, team_a_wins, team_b_id, team_b_name, team_b_wins = (winner_id, winner_name, winner_wins, loser_id, loser_name, loser_wins) if winner_id < loser_id else (loser_id, loser_name, loser_wins, winner_id, winner_name, winner_wins)
            to_ret.append([self.season, team_a_id, team_a_name, team_b_id, team_b_name, team_a_wins, team_b_wins, winner_id, winner_name, loser_id, loser_name, level + 1, level_description])
        return to_ret

    def to_cache(self, data):
        return True

    def cache(self, data, f):
        f.write(self.resp)
