from dataclasses import dataclass
from typing import List, Callable
from dbmanager.Downloaders.BREFPlayoffSeriesDownloader import BREFPlayoffSeriesDownloader
from dbmanager.SharedData.BREFSeasonsLinks import BREFSeasonLink, bref_seasons_links
from dbmanager.SharedData.SharedDataResourceAbs import SharedDataResourceAbc


@dataclass
class SerieDetails:
    season: int
    team_a_id: int
    team_a_name: str
    team_b_id: int
    team_b_name: str
    serie_order: int


class SeasonPlayoffs(SharedDataResourceAbc[List[SerieDetails]]):
    def __init__(self, get_season_link: Callable[[], BREFSeasonLink]):
        self._season_link_func = get_season_link
        super().__init__()

    def _fetch_data(self):
        downloader = BREFPlayoffSeriesDownloader(self._season_link_func())
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
        to_ret = [
            SerieDetails(s[headers.index('Season')],
                         s[headers.index('TeamAId')],
                         s[headers.index('TeamAName')],
                         s[headers.index('TeamBId')],
                         s[headers.index('TeamBName')],
                         s[headers.index('SerieOrder')],
                         )
            for s in data
        ]
        return to_ret

    def get_last_round(self) -> int:
        return min(self.get_data(), key=lambda s: s.serie_order).serie_order if self.get_data() else -1


last_season_playoffs = SeasonPlayoffs(bref_seasons_links.max_nba_season_link)


def get_last_season_with_playoffs() -> int:
    return bref_seasons_links.max_nba_season() if last_season_playoffs.get_last_round() != -1 else bref_seasons_links.max_nba_season() - 1
