from pbpstats.data_loader.stats_nba.base import StatsNbaLoaderBase


class MySourceLoader(StatsNbaLoaderBase):
    def __init__(self, file_directory, events):
        self.file_directory = None
        self.shots_source_loader = None
        self.events = events

    def load_data(self, game_id):
        return self.events
