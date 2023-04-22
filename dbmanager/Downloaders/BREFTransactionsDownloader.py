from dbmanager.Downloaders.DownloaderAbs import DownloaderAbs
from dbmanager.RequestHandlers.Sessions import bref_session
from dbmanager.constants import BREF_TRANSACTIONS_URL


class BREFTransactionsDownloader(DownloaderAbs):
    def __init__(self, league, season):
        self.league = league
        self.season = season

    async def download(self):
        to_send = BREF_TRANSACTIONS_URL % (self.league, self.season + 1)
        r = await bref_session.async_get(to_send)
        return r.text
