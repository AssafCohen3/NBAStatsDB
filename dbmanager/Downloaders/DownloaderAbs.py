from abc import ABC, abstractmethod


class DownloaderAbs(ABC):
    @abstractmethod
    async def download(self):
        pass
