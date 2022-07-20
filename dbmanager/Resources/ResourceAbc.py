from abc import ABC


class ResourceAbc(ABC):
    def __init__(self, session):
        self.session = session
