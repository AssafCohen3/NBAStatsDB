import re

from dbmanager.Downloaders.DownloaderAbs import HandlerAbs
from dbmanager.MainRequestsSession import requests_session as requests
from bs4 import BeautifulSoup
from dbmanager.constants import *


class BREFStartersHandler(HandlerAbs):
    def __init__(self, season, team_id, players_mapping):
        self.season = season
        self.team_id = team_id
        self.players_mapping = players_mapping
        self.finished = False
        self.resp = None

    def get_filename(self):
        return BREF_STARTERS_FILE_TEMPLATE % (self.team_id, self.season)

    def load_file(self, f):
        return self.from_html(f.read())

    def downloader(self):
        to_send = BREF_STARTERS_ENDPOINT % (self.get_team_abbrevation(), self.season+1)
        r = requests.get(to_send)
        self.resp = r.text
        return self.from_html(r.text)

    def from_html(self, html_resp):
        soup = BeautifulSoup(html_resp, 'html.parser')
        team_summery_div = soup.select('#meta div[data-template="Partials/Teams/Summary"]')[0]
        next_game_line = team_summery_div.find_all('strong', text=re.compile('Next Game:'))
        if len(next_game_line) == 0:
            self.finished = True
        games_rows = soup.select('table#starting_lineups_po0 tbody tr, table#starting_lineups_po1 tbody tr', {'class': ''})
        to_ret = []
        for game in games_rows:
            game_date = game.select('[data-stat=\"date_game\"]')[0]['csk']
            starters = game.select('[data-stat=\"game_starters\"]')[0]
            starters_links = starters.select('a')
            if len(starters_links) == 0:
                continue
            starters_ids = [re.findall(r'^.*/([^/]*?)\.html$', s['href'])[0] for s in starters_links]
            starters_ids = [self.players_mapping[s] for s in starters_ids]
            to_ret.append([game_date, starters_ids])
        return to_ret

    def to_cache(self, data):
        return False

    def cache(self, data, f):
        f.write(self.resp)

    def get_team_abbrevation(self):
        return [team_abbr for first_season, last_season, team_abbr in TEAM_IDS_TO_BREF_ABBR[self.team_id] if first_season <= self.season <= last_season][0]
