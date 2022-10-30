import datetime
import logging
import re

import requests
from bs4 import BeautifulSoup

from dbmanager.Downloaders.DownloaderAbs import DownloaderAbs
from dbmanager.constants import BREF_STARTERS_URL, TEAM_IDS_TO_BREF_ABBR


class BREFStartersDownloader(DownloaderAbs):
    def __init__(self, season, team_id, players_mapping):
        self.season = season
        self.team_id = team_id
        self.players_mapping = players_mapping

    def download(self):
        to_send = BREF_STARTERS_URL % (self.get_team_abbrevation(), self.season+1)
        r = requests.get(to_send, timeout=10)
        return self.from_html(r.text)

    def from_html(self, html_resp):
        soup = BeautifulSoup(html_resp, 'html.parser')
        games_rows = soup.select('table#starting_lineups_po0 tbody tr, table#starting_lineups_po1 tbody tr', {'class': ''})
        to_ret = []
        for game in games_rows:
            game_date = game.select('[data-stat=\"date_game\"]')[0]['csk']
            starters = game.select('[data-stat=\"game_starters\"]')[0]
            starters_links = starters.select('a')
            if len(starters_links) == 0:
                continue
            starters_ids = [re.findall(r'^.*/([^/]*?)\.html$', s['href'])[0] for s in starters_links]
            # TODO if no mappings?
            starters_nba_ids = [self.players_mapping[s] for s in starters_ids if s in self.players_mapping]
            if len(starters_ids) != 5:
                logging.info(f'***************** {game_date} - {starters_ids} *******************')
                continue
            to_ret.append([datetime.date.fromisoformat(game_date), starters_nba_ids])
        return to_ret

    def get_team_abbrevation(self):
        return [team_abbr for first_season, last_season, team_abbr in TEAM_IDS_TO_BREF_ABBR[self.team_id] if first_season <= self.season <= last_season][0]
