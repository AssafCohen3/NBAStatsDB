from abc import ABC, abstractmethod


class DownloaderAbs(ABC):
    @abstractmethod
    def download(self):
        pass
