import datetime
import unidecode
from Handlers.HandlerAbs import HandlerAbs
from MainRequestsSession import requests_session as requests
from bs4 import BeautifulSoup
from constants import *


class BREFPlayerHandler(HandlerAbs):
    def __init__(self, letter):
        self.letter = letter
        self.resp = None

    def get_filename(self):
        return BREF_PLAYERS_FILE_TEMPLATE % self.letter

    def load_file(self, f):
        return self.from_html(f.read())

    def downloader(self):
        to_send = BREF_PLAYERS_ENDPOINT % self.letter
        r = requests.get(to_send)
        self.resp = r.text
        return self.from_html(r.text)

    @staticmethod
    def from_html(html_resp):
        soup = BeautifulSoup(html_resp, 'html.parser')
        players_rows = soup.select('table tbody tr')
        to_ret = []
        for row in players_rows:
            if row.has_attr('class'):
                continue
            id_col = row.select('[data-stat="player"]')[0]
            player_id = id_col['data-append-csv']
            player_name = unidecode.unidecode(str(id_col.select('a')[0].get_text().strip()))
            is_active = 1 if len(id_col.select('strong')) > 0 else 0
            hof = 1 if '*' in id_col.contents[-1].get_text() else 0
            from_year = int(row.select('[data-stat="year_min"]')[0].getText())
            to_year = int(row.select('[data-stat="year_max"]')[0].getText())
            position = row.select('[data-stat="pos"]')[0].getText()
            height = float(row.select('[data-stat="height"]')[0]['csk'])
            weight = row.select('[data-stat="weight"]')[0].getText()
            weight = int(weight) if weight else None
            birth_date = row.select('[data-stat="birth_date"]')[0]
            if 'csk' in birth_date.attrs:
                birth_date = birth_date['csk']
                year = birth_date[:4]
                month = birth_date[4:6]
                day = birth_date[6:8]
                birth_date = year + '-' + month + '-' + day
                birth_date = datetime.datetime.strptime(birth_date, '%Y-%m-%d').date()
            else:
                birth_date = None
            to_ret.append([player_id, player_name, from_year, to_year, position, height, weight, birth_date, is_active, hof])
        return to_ret

    def to_cache(self, data):
        return False

    def cache(self, data, f):
        f.write(self.resp)
