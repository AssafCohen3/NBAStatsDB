import re

from Handlers.HandlerAbs import HandlerAbs
from MainRequestsSession import requests_session as requests
import unidecode
from bs4 import BeautifulSoup
from constants import *


class BREFSeasonDraftHandler(HandlerAbs):
    def __init__(self, season, leage):
        self.season = season
        self.league = leage
        self.resp = None

    def get_filename(self):
        return BREF_DRAFT_FILE_TEMPLATE % (self.league, self.season)

    def load_file(self, f):
        return self.from_html(f.read())

    def downloader(self):
        to_send = BREF_DRAFT_ENDPOINT % (self.league, self.season)
        r = requests.get(to_send)
        self.resp = r.text
        return self.from_html(r.text)

    def from_html(self, html_resp):
        soup = BeautifulSoup(html_resp, 'html.parser')
        table = soup.select('.stats_table tbody')[0]
        picks = table.select('tr')
        current_round = 1
        to_ret = []
        for pick in picks:
            if pick.has_attr('class'):
                if 'over_header' in pick['class']:
                    current_round += 1
                continue
            player = pick.select('[data-stat=\"player\"] a')
            if len(player) == 0:
                continue
            player = player[0]
            pick_number = pick.select('[data-stat=\"pick_overall\"] a')
            if len(pick_number) == 0:
                pick_number = ''
            else:
                pick_number = pick_number[0].getText()
            pick_number = int(pick_number) if pick_number != '' else None
            player_id = player['href']
            player_id = re.findall(r'^.*/(.*?)\.html$', player_id)[0]
            player_name = unidecode.unidecode(player.getText().strip())
            to_ret.append([player_id, player_name, self.season, self.league, current_round, pick_number])
        return to_ret

    def to_cache(self, data):
        return True

    def cache(self, data, f):
        f.write(self.resp)
