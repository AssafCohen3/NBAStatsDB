from typing import List
from dbmanager.Downloaders.BREFPlayoffSeriesDownloader import BREFPlayoffSeriesDownloader
from dbmanager.SharedData.BREFSeasonsLinks import BREFSeasonLink, bref_seasons_links
from dbmanager.SharedData.SharedDataResourceAbs import SharedDataResourceAbc


class SeasonPlayoffs(SharedDataResourceAbc):
    def __init__(self, season_link: BREFSeasonLink):
        self.season_link = season_link
        super().__init__()

    def _fetch_data(self):
        downloader = BREFPlayoffSeriesDownloader(self.season_link)
        data = downloader.download()
        if not data:
            return []
        headers = [
            'Season',
            'TeamAId',
            'TeamAName',
            'TeamBId',
            'TeamBName',
            'TeamAWins',
            'TeamBWins',
            'WinnerId',
            'WinnerName',
            'LoserId',
            'LoserName',
            'SerieOrder',
            'LevelTitle',
            'SerieStartDate',
            'SerieEndDate',
            'IsOver'
        ]
        dicts = [dict(zip(headers, serie)) for serie in data]
        return dicts

    def get_series(self) -> List[dict]:
        return self.get_data()

    def get_last_round(self) -> int:
        return min(self.get_series(), key=lambda s: s['SerieOrder'])['SerieOrder'] if self.get_series() else -1


last_season_playoffs = SeasonPlayoffs(bref_seasons_links.max_nba_season_link())


def get_last_season_with_playoffs() -> int:
    return bref_seasons_links.max_nba_season() if last_season_playoffs.get_last_round() != -1 else bref_seasons_links.max_nba_season() - 1
