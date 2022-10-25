import requests

from dbmanager.Downloaders.DownloaderAbs import DownloaderAbs
from dbmanager.constants import BREF_TRANSACTIONS_URL


class BREFTransactionsDownloader(DownloaderAbs):
    def __init__(self, league, season):
        self.league = league
        self.season = season

    def download(self):
        to_send = BREF_TRANSACTIONS_URL % (self.league, self.season + 1)
        r = requests.get(to_send)
        return r.text
