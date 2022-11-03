from dataclasses import dataclass, field
from enum import Enum
from typing import List


class AwardTypes(Enum):
    SEASON_PLAYER = 1
    SEASON_ALL_NBA_TEAM = 2
    MONTHLY = 3
    HONORARY = 4


@dataclass
class BREFAwardToFetch:
    award_id: str
    award_name: str
    award_type: AwardTypes
    person_type: str = field(default='player')


AWARDS = [
    BREFAwardToFetch('mvp', 'Most Valuable Player', AwardTypes.SEASON_PLAYER),
    BREFAwardToFetch('roy', 'Rookie of the Year', AwardTypes.SEASON_PLAYER),
    BREFAwardToFetch('dpoy', 'Defensive Player of the Year', AwardTypes.SEASON_PLAYER),
    BREFAwardToFetch('smoy', 'Sixth Man of the Year', AwardTypes.SEASON_PLAYER),
    BREFAwardToFetch('mip', 'Most Improved Player', AwardTypes.SEASON_PLAYER),
    BREFAwardToFetch('finals_mvp', 'NBA Finals Most Valuable Player', AwardTypes.SEASON_PLAYER),
    BREFAwardToFetch('wcf_mvp', 'Western Conference Finals Most Valuable Player', AwardTypes.SEASON_PLAYER),
    BREFAwardToFetch('ecf_mvp', 'Eastern Conference Finals Most Valuable Player', AwardTypes.SEASON_PLAYER),
    BREFAwardToFetch('all_star_mvp', 'All-Star Game Most Valuable Player', AwardTypes.SEASON_PLAYER),
    BREFAwardToFetch('coy', 'Coach of the Year', AwardTypes.SEASON_PLAYER, 'coach'),
    BREFAwardToFetch('all_league', 'All-NBA', AwardTypes.SEASON_ALL_NBA_TEAM),
    BREFAwardToFetch('all_rookie', 'All-Rookie', AwardTypes.SEASON_ALL_NBA_TEAM),
    BREFAwardToFetch('all_defense', 'All-Defensive', AwardTypes.SEASON_ALL_NBA_TEAM),
    BREFAwardToFetch('nba_75th_anniversary', 'NBA 75th Anniversary Team', AwardTypes.HONORARY),
    BREFAwardToFetch('nba_50_greatest', '50 Greatest Players in NBA History', AwardTypes.HONORARY),
    BREFAwardToFetch('nba_35th_anniversary', 'NBA 35th Anniversary All-Time Team', AwardTypes.HONORARY),
    BREFAwardToFetch('pom', 'Player of the Month', AwardTypes.MONTHLY),
    BREFAwardToFetch('rom', 'Rookie of the Month', AwardTypes.MONTHLY),
    BREFAwardToFetch('com', 'Coach of the Month', AwardTypes.MONTHLY, 'coach'),
    BREFAwardToFetch('pow', 'Player of the Week', AwardTypes.MONTHLY),
]


def get_awards(award_ids: List[str]) -> List[BREFAwardToFetch]:
    return [aw for aw in AWARDS if aw.award_id in award_ids]
