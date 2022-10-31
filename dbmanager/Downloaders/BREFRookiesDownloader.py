from dbmanager.Downloaders.DownloaderAbs import DownloaderAbs
from dbmanager.RequestHandlers.Sessions import bref_session
from dbmanager.constants import BREF_ROOKIES_PAGE_URL


class BREFRookiesDownloader(DownloaderAbs):

    def __init__(self, season: int):
        self.season: int = season

    def download(self):
        to_send = BREF_ROOKIES_PAGE_URL % (self.season + 1)
        return bref_session.get(to_send).text
