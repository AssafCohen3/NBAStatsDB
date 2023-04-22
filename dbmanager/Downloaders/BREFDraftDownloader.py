from dbmanager.Downloaders.DownloaderAbs import DownloaderAbs
from dbmanager.RequestHandlers.Sessions import bref_session
from dbmanager.constants import BREF_DRAFT_URL


class BREFDraftDownloader(DownloaderAbs):

    def __init__(self, season: int):
        self.season: int = season

    async def download(self):
        to_send = BREF_DRAFT_URL % self.season
        resp = await bref_session.async_get(to_send)
        return resp.text
