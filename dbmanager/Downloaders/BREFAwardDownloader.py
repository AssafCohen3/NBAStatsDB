from dbmanager.Downloaders.DownloaderAbs import DownloaderAbs
from dbmanager.RequestHandlers.Sessions import bref_session
from dbmanager.constants import BREF_AWARD_PAGE_URL


class BREFAwardDownloader(DownloaderAbs):
    def __init__(self, award_id: str):
        self.award_id = award_id

    def download(self):
        to_send = BREF_AWARD_PAGE_URL % self.award_id
        r = bref_session.get(to_send)
        return r.text
