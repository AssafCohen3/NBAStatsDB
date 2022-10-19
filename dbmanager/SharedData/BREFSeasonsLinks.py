import re
from dataclasses import dataclass
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
from dbmanager.SharedData.SharedDataResourceAbs import SharedDataResourceAbc
from dbmanager.constants import BREF_SEASONS_INDEX_URL


@dataclass
class BREFSeasonLink:
    season: int
    season_link: str
    leagu_id: str


class BREFSeasonsLink(SharedDataResourceAbc):
    def _fetch_data(self):
        resp = requests.get(BREF_SEASONS_INDEX_URL)
        soup = BeautifulSoup(resp.content, 'html.parser')
        seasons_rows = soup.select('.stats_table tr')
        seasons_rows = [s for s in seasons_rows if not s.has_attr('class')]
        to_ret: List[BREFSeasonLink] = []
        for s in seasons_rows:
            season = s.select('[data-stat=\"season\"] a')[0]
            season_number = int(re.findall(r'^(.+?)-', season.getText())[0])
            season_link = season['href']
            league_id = s.select('[data-stat=\"lg_id\"] a')[0].getText()
            to_ret.insert(0, BREFSeasonLink(season_number, season_link, league_id))
        return to_ret

    def get_nba_seasons(self):
        seasons_links: List[BREFSeasonLink] = self.get_data()
        return [s for s in seasons_links if s.leagu_id in ('NBA', 'BAA')]

    def min_nba_season(self):
        return min(self.get_nba_seasons(), key=lambda s: s.season).season

    def max_nba_season(self):
        return max(self.get_nba_seasons(), key=lambda s: s.season).season

    def max_nba_season_link(self) -> BREFSeasonLink:
        return max(self.get_nba_seasons(), key=lambda s: s.season)

    def get_nba_season(self, season: int) -> Optional[BREFSeasonLink]:
        to_ret = [s for s in self.get_nba_seasons() if s.season == season]
        if len(to_ret) == 0:
            return None
        return to_ret[0]

    def get_nba_seasons_in_range(self, start_season: Optional[int], end_season: Optional[int]) -> List[BREFSeasonLink]:
        return [s for s in self.get_nba_seasons() if (start_season is None or s.season >= start_season) and (end_season is None or s.season <= end_season)]

    def get_nba_seasons_not_in_list(self, seasons_list: List[int]) -> List[BREFSeasonLink]:
        return [s for s in self.get_nba_seasons() if s.season not in seasons_list]


bref_seasons_links = BREFSeasonsLink()
