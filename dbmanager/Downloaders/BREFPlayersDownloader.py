import datetime
import unidecode
from dbmanager.Downloaders.DownloaderAbs import DownloaderAbs
from bs4 import BeautifulSoup

from dbmanager.RequestHandlers.Sessions import bref_session
from dbmanager.constants import BREF_PLAYERS_URL


class BREFPlayersDownloader(DownloaderAbs):
    def __init__(self, letter):
        self.letter = letter

    async def download(self):
        to_send = BREF_PLAYERS_URL % self.letter
        r = await bref_session.async_get(to_send)
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
