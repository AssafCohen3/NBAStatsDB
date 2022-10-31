from dbmanager.Downloaders.DownloaderAbs import DownloaderAbs
from dbmanager.RequestHandlers.Sessions import bref_session
from dbmanager.constants import BREF_PLAYER_PAGE_URL


class BREFPlayerPageDownloader(DownloaderAbs):

    def __init__(self, player_id: str):
        self.player_id: str = player_id

    def download(self):
        to_send = BREF_PLAYER_PAGE_URL % (self.player_id[0], self.player_id)
        return bref_session.get(to_send).text
