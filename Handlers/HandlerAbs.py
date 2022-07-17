from abc import ABC, abstractmethod


class HandlerAbs(ABC):
    @abstractmethod
    def get_filename(self):
        pass

    @abstractmethod
    def load_file(self, f):
        pass

    @abstractmethod
    def downloader(self):
        pass

    @abstractmethod
    def to_cache(self, data):
        pass

    @abstractmethod
    def cache(self, data, f):
        pass
