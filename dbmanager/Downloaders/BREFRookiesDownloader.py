from dbmanager.Downloaders.DownloaderAbs import DownloaderAbs
from dbmanager.RequestHandlers.Sessions import bref_session
from dbmanager.constants import BREF_ROOKIES_PAGE_URL


class BREFRookiesDownloader(DownloaderAbs):

    def __init__(self, season: int):
        self.season: int = season

    async def download(self):
        to_send = BREF_ROOKIES_PAGE_URL % (self.season + 1)
        r = await bref_session.async_get(to_send)
        return r.text
